from fastapi import FastAPI,Request
from algorithm.round_robin import RoundRobin
import httpx
import asyncio
import random
from contextlib import asynccontextmanager
from health_checker import HealthChecker
from fastapi.responses import Response
import time 
from rate_limiter import RateLimiter
from redis_rate_limiter import RedisSlidingWindow
from circuit_breaker import CircuitBreaker
from logger import logger
from metrics import REQUEST_COUNT, REQUEST_LATENCY,BACKEND_REQUEST_COUNT,STATUS_COUNT
from prometheus_client import generate_latest,CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# servers=[
#     "http://localhost:8001",
#     "http://localhost:8002",
#     "http://localhost:8003",

# ]
# rate_limiter=RateLimiter(5,1)
rate_limiter = RedisSlidingWindow(
    max_requests=5,
    window_seconds=10
)
tracer = trace.get_tracer(__name__)
servers = [
    "http://server1:8001",
    "http://server2:8002",
    "http://server3:8003",
]
resource = Resource.create({
    "service.name": "load-balancer"
})

tracer_provider = TracerProvider(
    resource=resource
)

otlp_exporter = OTLPSpanExporter(
    endpoint="http://jaeger:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(
    otlp_exporter
)

tracer_provider.add_span_processor(
    span_processor
)

trace.set_tracer_provider(
    tracer_provider
)

# creating circuit bracker for each server -
circuit_breakers={
    server : CircuitBreaker(failure_threshold=3,recovery_timeout=10) for server in servers
}


load_balancer=RoundRobin(servers)
async def health_check_loop():
    health_checker = HealthChecker()
    while True:
       healthy_servers=[]
       for server in servers:
            if await health_checker.is_healthy(server):
                healthy_servers.append(server)
            else:
                logger.warning(f"skipping the server={server} as it is not healthy")
               
        

       load_balancer.update_servers(healthy_servers)
       logger.info(f"healthy servers : {healthy_servers}")
        
       await asyncio.sleep(2)



@asynccontextmanager
async def lifespan(app: FastAPI):

    task = asyncio.create_task(health_check_loop())

    yield

    task.cancel()


app=FastAPI(lifespan=lifespan)
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
@app.get('/metrics')
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST

    )

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(request:Request,path:str):
    # REQUEST_COUNT.inc() # increment the counter by one 
    REQUEST_COUNT.labels(method=request.method).inc()
    
    # perf_counter() -> it is the performance counter for benchmarkig used to measure the perfomrance with highest possible resolution
    start_time=time.perf_counter()
    client_ip=request.client.host
    logger.info(
        f"Incoming request"
        f"Method={request.method}"
        f"Path /{path}"
        f"client ip={client_ip}"
    )
    try:
        # apply tracing in rate limiter 
        with tracer.start_as_current_span("rate_limit") as span:
            span.set_attribute("client.ip", client_ip)

        # rate limiting 
            allowed=rate_limiter.allow_request(client_ip)
            span.set_attribute("rate_limit.allowed", allowed)
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded"
                    f"client={client_ip}"
                    f"path /{path}"
                )
                STATUS_COUNT.labels(status=429).inc()
                return Response(
                    content="Too Many Requests",
                    status_code=429
                )

        # retry loop

        max_retries=2
        for attempt in range(max_retries+1):
            with tracer.start_as_current_span("select_backend") as span:
                server=load_balancer.get_next_server()
        
                if server is None:
                    logger.error("No healthy sever is available")
                    STATUS_COUNT.labels(status=503).inc()
                    return Response(
                    content="No healthy servers available",
                    status_code=503
                    
            )
                BACKEND_REQUEST_COUNT.labels(
                            backend=server
                        ).inc()
                circuit=circuit_breakers[server]
                # cirucit breaker

                if not circuit.allow_request():
                    logger.warning(
                        f"Circuit OPEN"
                        f"server={server}"
                        f"skipping server"
                    )
                    print(f"Circuit is open for {server} skipping server.....")
                    continue
                logger.info(f"forward request to={server}")

                url=f"{server}/{path}"
                print("PATH:", path)
                print("FORWARDING TO:", url)
                body=await request.body()
                print("Body", body)
                # timeout=httpx.Timeout(
                #     connect=2.0,
                #     read=5.0,
                #     write=5.0,
                #     pool=2.0
                # )
            
                headers = dict(request.headers)
                headers.pop("host", None)
            try:
                async with httpx.AsyncClient(
                    timeout=5.0
                ) as client:
                    with tracer.start_as_current_span("backend_request") as span:

                        span.set_attribute("backend.server", server)
                        span.set_attribute("http.method", request.method)
                        span.set_attribute("http.path", f"/{path}")

                        response=await client.request(
                            method=request.method,
                            url=url,
                            headers=headers,
                            content=body,
                            
                        )
                        # getting the respone
                        latency = time.perf_counter() - start_time
                        logger.info(
                            f"Request successful "
                            f"server={server} "
                            f"status={response.status_code} "
                            f"latency={latency:.3f}s"
                        )
                        span.set_attribute(
                        "http.status_code",
                        response.status_code
                    )
                    circuit.record_success()
                    STATUS_COUNT.labels(status=str(response.status_code)).inc()
                    return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers={
                        "content-type":
                        response.headers.get("content-type", "")
                    }
                )
            except httpx.TimeoutException:
                circuit.record_failure()
                latency = time.perf_counter() - start_time
                logger.error(
                    f"Backend timeout "
                    f"server={server} "
                    f"attempt={attempt + 1} "
                    f"latency={latency:.3f}s"
                )
                
                base_delay=0.1
                exponentail_delay=base_delay* (2**attempt)
                jitter=random.uniform(0,0.1)
                delay=exponentail_delay+jitter

                logger.info(
                    f"Retrying request "
                    f"attempt={attempt + 2} "
                    f"delay={delay:.3f}s"
                )
                await asyncio.sleep(delay)
                continue
        
        latency = time.perf_counter() - start_time
        logger.error(
            f"Backend failed after retries "
            f"latency={latency:.3f}s"
        )
        STATUS_COUNT.labels(status=504).inc()    
        return Response(
        content="Backend timeout after retries",
        status_code=504
    )

    finally:
        latency = time.perf_counter() - start_time

        REQUEST_LATENCY.observe(latency)
            
