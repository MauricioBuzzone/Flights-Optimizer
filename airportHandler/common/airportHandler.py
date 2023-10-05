import io
import signal
import logging

from geopy.distance import geodesic
from common.airportHandlerMiddleware import AirportHandlerMiddleware
from utils.airportSerializer import AirportSerializer
from utils.flightQ2Serializer import FlightQ2Serializer
from utils.protocol import is_airport_eof, is_flight_eof


class AirportHandler():
    def __init__(self):
        self.airports = {} #cod: (lat, lon)
        self.airportSerializer = AirportSerializer()
        self.flightSerializer = FlightQ2Serializer()
        signal.signal(signal.SIGTERM, self.__handle_signal)

        # last thing to do:
        self.middleware = AirportHandlerMiddleware()

    def run(self):
        logging.info(f'action: listen_airports | result: in_progress')
        self.middleware.listen_airports(self.recv_airports)
        logging.info(f'action: listen_airports | result: success')

        self.middleware.start()

        self.middleware.stop()

    def recv_airports(self, airports_raw):
        if is_airport_eof(airports_raw):
            logging.info(f'action: recv_airports | result: EOF')
            self.middleware.stop_listen_airports()
            logging.info(f'action: stop_receiving_airports | result: success')

            logging.info(f'action: listen_flights | result: in_progress')
            self.middleware.listen_flights(self.recv_flights)
            logging.info(f'action: listen_flights | result: success')
            return 

        reader = io.BytesIO(airports_raw)
        airports = self.airportSerializer.from_chunk(reader)
        logging.debug(f'action: new_chunk_airports | chunck_len: {len(airports)}')

        for airport in airports:
            self.airports[airport.cod] = (airport.latitude, airport.longitude)
            logging.debug(f'action: save_airport | value: {airport}')

        # save to file
        # self.middleware.ack()?

    def recv_flights(self, flights_raw):
        if is_flight_eof(flights_raw):
            logging.info(f'action: recv_flights | result: EOF')
            self.middleware.stop_listen_flights()
            logging.info(f'action: stop_receiving_flights | result: success')
            return

        reader = io.BytesIO(flights_raw)
        flights = self.flightSerializer.from_chunk(reader)
        logging.info(f'action: new_chunk_flights | chunck_len: {len(flights)}')

        for flight in flights:
            if not (flight.origin in self.airports):
                logging.info(f'action: Q2 filter | result: origin({flight.origin}) not in database')
                continue
            if not (flight.destiny in self.airports):
                logging.info(f'action: Q2 filter | result: destiny({flight.destiny}) not in database')
                continue

            distance = geodesic(self.airports[flight.origin], self.airports[flight.destiny])
            if flight.total_distance > 4 * distance:
                # self.middleware.publish(flight)
                logging.info(f'action: publish_flight | value: {flight}')

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | singal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')
