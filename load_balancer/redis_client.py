import redis 

redis_client=redis.Redis(
    # if we using redis in docker 
    host='redis',
    # if we use redis in localhost 
    # host='localhost',
    port = 6379,
    decode_responses=True
)