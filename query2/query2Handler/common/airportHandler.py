from utils.worker import Worker
from middleware.middlewareEQ import MiddlewareEQ
from utils.serializer.airportSerializer import AirportSerializer

class AirportHandler(Worker):
    def __init__(self, airports: list):
        middleware = MiddlewareEQ(exchange='airports',
                                  tag='',
                                  out_queue_name=None)
        super().__init__(middleware=middleware,
                         in_serializer=AirportSerializer(),
                         out_serializer=None,
                         peers=1,
                         worker_id=1,
                         chunk_size=0)
        self.airports = airports

    def work(self, input, idempotency_key):
        airport = input
        self.airports[airport.cod] = (airport.latitude, airport.longitude)

    def recv_eof(self, eof):
        return