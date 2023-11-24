from utils.worker import Worker
from middleware.middlewareQQ import MiddlewareQQ
from utils.serializer.flightQ4Serializer import FlightQ4Serializer
from utils.serializer.resultQ4Serializer import ResultQ4Serializer
from utils.result.resultQ4 import ResultQ4

class Query4Worker(Worker):
    def __init__(self, peers, chunk_size):
        in_serializer = FlightQ4Serializer()
        out_serializer = ResultQ4Serializer()
        middleware = MiddlewareQQ(in_queue_name='Q4-workers',
                                  out_queue_name='Q4-sync')
        super().__init__(middleware=middleware,
                         in_serializer=in_serializer,
                         out_serializer=out_serializer,
                         peers=peers,
                         chunk_size=chunk_size)

    def work(self, input, idempotency_key):
        flight = input
        journey = (flight.origin, flight.destiny)
        if journey in self.results:
            self.results[journey].update(flight.total_fare)
        else:
            self.results[journey] = ResultQ4(origin=flight.origin,
                                                destiny=flight.destiny,
                                                fare_avg=flight.total_fare,
                                                fare_max=flight.total_fare,
                                                n=1)