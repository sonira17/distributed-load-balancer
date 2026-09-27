


class RoundRobin:
    def __init__(self, server):
        self.servers=server
        self.current_index=0



    def get_next_server(self):
        if not self.servers:
            return None
        if self.current_index >= len(self.servers):
            self.current_index = 0
        
        server=self.servers[self.current_index]
        self.current_index=(self.current_index+1)%len(self.servers)
        return server
    def update_servers(self, healthy_servers):
        self.servers = healthy_servers

        # Prevent index from going out of range
        if self.current_index >= len(self.servers):
            self.current_index = 0


