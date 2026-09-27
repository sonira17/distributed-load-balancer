import time 
from redis_client import redis_client

class RedisSlidingWindow:
    def __init__(self,max_requests:int ,window_seconds:int):
        self.max_requests=max_requests
        self.window_seconds=window_seconds
        

    def allow_request(self,client_id :str):
        current_time=time.time()
        window_start=current_time-self.window_seconds
        key=f"rate_limit:{client_id}"
        redis_client.zremrangebyscore(key,0,window_start)
        request_count=redis_client.zcard(key)
        if request_count>=self.max_requests:
            return False
        redis_client.zadd(key, {str(current_time): current_time})
        redis_client.expire(key,self.window_seconds)
        return True 


# if __name__ == "__main__":

#     limiter = RedisSlidingWindow(
#         max_requests=5,
#         window_seconds=10
#     )

#     for i in range(7):

#         allowed = limiter.allow_requests(
#             "client-A"
#         )

#         print(
#             f"Request {i + 1}: {allowed}"
#         )
#         print(
#     "Redis keys:",
#     redis_client.keys("*")
# )