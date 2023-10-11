from utils.worker import Worker
from middleware.middlewareEQ import MiddlewareEQ
from utils.airportSerializer import AirportSerializer

class AirportHandler(Worker):
    def __init__(self, airports: list):
        middleware = MiddlewareEQ(exchange='airports',
                                  tag='',
                                  out_queue_name=None)
        super().__init__(middleware=middleware,
                         in_serializer=AirportSerializer(),
                         out_serializer=None,
                         peers=0,
                         chunk_size=0)
        self.airports = airports

    def work(self, input):
        airport = input
        self.airports[airport.cod] = (airport.latitude, airport.longitude)

    def recv_eof(self, eof):
        return