import time 


# circuit breaker state 

CLOSED='closed'
OPEN='open'
HALF_OPEN='half_open'

class CircuitBreaker:
    def __init__(self, failure_threshold : int , recovery_timeout: int):
        self.failure_threshold=failure_threshold
        self.recovery_timeout=recovery_timeout
        self.failure_count=0
        self.state=CLOSED
        self.open_at=None

    def allow_request(self):
        if self.state==CLOSED:
            return True 
        if self.state==OPEN:
            elapsed_time=time.time()-self.open_at
            if elapsed_time >= self.recovery_timeout:
                self.state=HALF_OPEN
                print("State is half open")
                return True 
            else:
                return False
        if self.state==HALF_OPEN:
            return True 


    def record_failure(self):
        # for half failure 1 failed request will make the state as open
        if self.state==HALF_OPEN:
            self.state=OPEN
            self.open_at=time.time()
            print("Circuit open again")
            return 

        self.failure_count+=1
        print(f"Circuit failure count {self.failure_count}")
        if self.failure_count>=self.failure_threshold:
            self.state=OPEN
            self.open_at=time.time()
            print("Cirucit open ")

    def record_success(self):
        self.failure_count=0
        self.state=CLOSED
        self.open_at=None
        print("Circuit closed")


# if __name__=='__main__':
#     circuit=CircuitBreaker(3,5)
#     print(circuit.allow_request())
#     circuit.record_failure()
#     print(circuit.allow_request())
#     circuit.record_failure()
#     print(circuit.allow_request())
#     circuit.record_failure()
#     print(circuit.allow_request())

        

      
