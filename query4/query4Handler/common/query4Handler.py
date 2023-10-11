import logging
from middleware.middlewareQQ import MiddlewareQQ

from utils.worker import Worker
from model.flight import Flight
from model.duration import Duration
from utils.serializer.flightQ4Serializer import FlightQ4Serializer

class Query4Handler(Worker):
    def __init__(self, chunk_size):
        middleware = MiddlewareQQ(in_queue_name='Q4-flights',
                                  out_queue_name='Q4-workers')
        super().__init__(middleware=middleware,
                         in_serializer=FlightQ4Serializer(),
                         out_serializer=FlightQ4Serializer(),
                         peers=1,
                         chunk_size=chunk_size)

        self.flights_list = []
        self.avg = 0
        self.n = 0

    def work(self, input):
        flight = input
        self.avg = (self.avg*self.n + flight.total_fare) / (self.n+1)
        # ¿A disco?
        self.flights_list.append((flight.id, flight.origin, flight.destiny, flight.total_fare))
        self.n += 1

    def send_results(self):
        chunk = []
        while self.flights_list:
            id, origin, destiny, total_fare = self.flights_list.pop()
            if total_fare > self.avg:
                flight = Flight(id = id, origin = origin, destiny = destiny, total_distance=0,
                                total_fare=total_fare, legs=[], flight_duration=Duration(0,0))
                chunk.append(flight)
                if len(chunk) >= self.chunk_size:
                    logging.debug(f'action: publishing_chunk | len(chunk): {len(chunk)}')
                    data = self.out_serializer.to_bytes(chunk)
                    self.middleware.publish(data)
                    chunk = []
        if chunk:
            logging.debug(f'action: publishing_chunk | len(chunk): {len(chunk)}')
            data = self.out_serializer.to_bytes(chunk)
            self.middleware.publish(data)