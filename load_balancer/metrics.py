from prometheus_client import Counter, Histogram

# create a metrics that only goes up 
REQUEST_COUNT=Counter("lb_request_total", "total number of request a load balacer received", ['method'])


# used for measuring the distribution 

REQUEST_LATENCY=Histogram("lb_request_latency_seconds", "Request latency in seconds")

BACKEND_REQUEST_COUNT=Counter('backend_request_total', 'Store the count of total backend server used', ['backend'])

STATUS_COUNT=Counter('status_total', "total count of status code", ['status'])

