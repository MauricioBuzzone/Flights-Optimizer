import logging
from utils.worker import Worker
from middleware.middlewareQE import MiddlewareQE
from utils.serializer.flightQ1Serializer import FlightQ1Serializer

class Query1Handler(Worker):
    def __init__(self, peers, min_legs):
        middleware = MiddlewareQE(in_queue_name='Q1-flights',
                                  exchange='results',
                                  tag='Q1')
        super().__init__(middleware=middleware,
                         in_serializer=FlightQ1Serializer(),
                         out_serializer=FlightQ1Serializer(),
                         peers=peers,
                         chunk_size=1,)
        self.min_legs = min_legs

    def work(self, input):
        flight = input
        if len(flight.legs) >= self.min_legs:
            logging.info(f'action: publish_flight | value: {flight}')
            data = self.out_serializer.to_bytes([flight])
            self.middleware.publish(data)