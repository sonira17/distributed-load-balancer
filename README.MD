#  Distributed Load Balancer

A production-inspired HTTP load balancer built from scratch using **Python, FastAPI, Redis, Nginx, Docker, Prometheus, Grafana, OpenTelemetry, and Jaeger**.

The project focuses on understanding and implementing important **backend engineering and distributed-systems concepts** such as load balancing, rate limiting, health checks, retries, circuit breakers, observability, metrics, alerting, and distributed tracing.

---

##  Architecture

```text
                              Client
                                |
                                v
                         +--------------+
                         |    Nginx     |
                         |    :80       |
                         +------+-------+
                                |
                                v
                    +-----------------------+
                    |   FastAPI Load        |
                    |      Balancer         |
                    |       :8000           |
                    +----------+------------+
                               |
             +-----------------+-----------------+
             |                 |                 |
             v                 v                 v
      +-------------+   +-------------+   +-------------+
      |   Server 1  |   |   Server 2  |   |   Server 3  |
      |    :8001    |   |    :8002    |   |    :8003    |
      +-------------+   +-------------+   +-------------+


                    Supporting Services
                    ===================

        +-------------+       +----------------+
        |    Redis    |       |   Prometheus   |
        |    :6379    |       |     :9090      |
        +-------------+       +-------+--------+
                                      |
                                      v
                              +---------------+
                              |    Grafana    |
                              |     :3000     |
                              +---------------+

        +----------------+
        |     Jaeger     |
        |     :16686     |
        +----------------+
                 ^
                 |
          OpenTelemetry
```



## Notes 
[Load Balancer Documentation](https://app.notion.com/p/Load-balancers-3e09db2619e1802789aefa60125a9fcc)
