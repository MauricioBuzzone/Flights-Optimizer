from utils.worker import Worker
from middleware.middlewareQQ import MiddlewareQQ
from utils.serializer.flightQ1Serializer import FlightQ1Serializer
from utils.serializer.resultQ3Serializer import ResultQ3Serializer
from utils.result.resultQ3 import ResultQ3

class Query3Worker(Worker):
    def __init__(self, peers, chunk_size):
        in_serializer = FlightQ1Serializer()
        out_serializer = ResultQ3Serializer()
        middleware = MiddlewareQQ(in_queue_name='Q3-workers',
                                  out_queue_name='Q3-sync')
        super().__init__(middleware=middleware,
                         in_serializer=in_serializer,
                         out_serializer=out_serializer,
                         peers=peers,
                         chunk_size=chunk_size)

    def work(self, input, idempotency_key):
        flight = input
        journey = (flight.origin, flight.destiny)
        if journey in self.results:
            self.results[journey].update(flight)
        else:
            self.results[journey] = ResultQ3(flight)