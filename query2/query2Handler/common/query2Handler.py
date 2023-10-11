import logging
from utils.worker import Worker
from middleware.middlewareQE import MiddlewareQE
from utils.serializer.flightQ2Serializer import FlightQ2Serializer
from geopy.distance import geodesic

class Query2Handler(Worker):
    def __init__(self, airports: list, peers: int, chunk_size: int, distance_rate: float):
        middleware = MiddlewareQE(in_queue_name='Q2-flights',
                                  exchange='results',
                                  tag='Q2')
        super().__init__(middleware=middleware,
                         in_serializer=FlightQ2Serializer(),
                         out_serializer=FlightQ2Serializer(),
                         peers=peers,
                         chunk_size=chunk_size)
        self.airports = airports
        self.distance_rate = distance_rate
        self.filtered_flights = []

    def work(self, input):
        flight = input
        if not (flight.origin in self.airports):
            logging.error(f'action: Q2 filter | result: origin({flight.origin}) not in database')
            return
        if not (flight.destiny in self.airports):
            logging.error(f'action: Q2 filter | result: destiny({flight.destiny}) not in database')
            return

        distance = geodesic(self.airports[flight.origin], self.airports[flight.destiny]).miles
        if flight.total_distance > self.distance_rate * distance:
            logging.debug(f'action: publish_flight | value: {flight}')
            self.filtered_flights.append(flight)

    def do_after_work(self):
        if self.filtered_flights:
            data = self.out_serializer.to_bytes(self.filtered_flights)
            self.middleware.publish(data)