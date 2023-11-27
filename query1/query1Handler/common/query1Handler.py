import logging
from utils.worker import Worker
from middleware.middlewareQE import MiddlewareQE
from utils.serializer.flightQ1Serializer import FlightQ1Serializer
from utils.chunk import Chunk

class Query1Handler(Worker):
    def __init__(self, peers, worker_id, min_legs):
        middleware = MiddlewareQE(in_queue_name='Q1-flights',
                                  exchange='results',
                                  tag='Q1')
        super().__init__(middleware=middleware,
                         in_serializer=FlightQ1Serializer(),
                         out_serializer=FlightQ1Serializer(),
                         peers=peers,
                         worker_id=worker_id,
                         chunk_size=1,)
        self.min_legs = min_legs
        self.filtered_flights = []

    def work(self, input, idempotency_key):
        flight = input
        if len(flight.legs) >= self.min_legs:
            logging.debug(f'action: publish_flight | value: {flight}')
            self.filtered_flights.append(flight)

    def do_after_work(self, idempotency_key):
        if self.filtered_flights:
            _chunk = Chunk(id=idempotency_key, values=self.filtered_flights)
            data = self.out_serializer.to_bytes(_chunk)
            self.middleware.publish(data)
        self.filtered_flights = []