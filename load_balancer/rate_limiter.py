
import time 

class TokenBucket:
    def __init__(self,capacity:int , refill_rate:float):
        self.capacity=capacity
        self.refill_rate=refill_rate

        self.token=capacity
        self.last_refill_time=time.time()

    def refill(self):
        current_time=time.time()
        elapsed_time=current_time-self.last_refill_time
        new_token=elapsed_time*self.refill_rate
        self.token=min(self.capacity,self.token+new_token)
        self.last_refill_time=current_time

    def allow_request(self):
        self.refill()
        if self.token>=1:
            self.token-=1
            return True
        return False

class SlidingWindow:
    def __init__(self,max_requests:int, window_seconds:int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        self.requests = []

    def allow_request(self):
        current_time=time.time()
        window_start=current_time-self.window_seconds

        self.requests=[
            timestamp
        for timestamp in self.requests
        if timestamp > window_start
        ]
        if len(self.requests) >= self.max_requests:
            return False

        self.requests.append(current_time)

        return True




class RateLimiter:
    def __init__(self,capacity:int, refill_rate:float):
        self.capacity=capacity
        self.refill_rate=refill_rate
        self.buckets={}

    def get_bucket(self, client_id:str):
        if client_id not in self.buckets:
            self.buckets[client_id]=TokenBucket(self.capacity, self.refill_rate)
        return self.buckets[client_id]

    def allow_request(self,client_id:str):
        bucket=self.get_bucket(client_id )
        return bucket.allow_request()

# if __name__ == "__main__":

#     limiter = SlidingWindow(
#         max_requests=5,
#         window_seconds=10
#     )

#     for i in range(7):

#         allowed = limiter.allow_request()

#         print(
#             f"Request {i + 1}: {allowed}"
#         )