from utils.protocol import make_eof 
from middleware.middlewareEQ import MiddlewareEQ
from utils.listener import Listener

class Query3Handler(Listener):
    def __init__(self, chunk_size):
        middleware = MiddlewareEQ(exchange='results',
                                  tag='Q1',
                                  out_queue_name='Q3-workers')
        super().__init__(middleware)
        self.chunk_size = chunk_size

    def recv_raw(self, raw):
        self.middleware.publish(raw)

    def recv_eof(self, eof):
        eof = make_eof(0)
        self.middleware.publish(eof)