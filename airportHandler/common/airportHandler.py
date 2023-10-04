import io
import signal
import logging

from geopy.distance import geodesic
from common.airportHandlerMiddleware import AirportHandlerMiddleware
from utils.airportSerializer import AirportSerializer
from utils.flightSerializer import FlightSerializer
from utils.protocol import is_airport_eof, is_flight_eof


class AirportHandler():
    def __init__(self):
        self.airports = {} #cod: (lat, lon)
        self.airportSerializer = AirportSerializer()
        self.flightSerializer = FlightSerializer()
        signal.signal(signal.SIGTERM, self.__handle_signal)

        # last thing to do:
        self.middleware = AirportHandlerMiddleware()

    def run(self):
        self.middleware.recieve_airports(self.recv_airports)
        #self.middleware.recieve_airports(self.recv_flights)
        self.middleware.stop()

    def recv_airports(self, airports_raw):
        if is_airport_eof(airports_raw):
            logging.info(f'action: recv airport EOF | result: stop receiving airports')
            self.middleware.stop_receiving()
            return 

        reader = io.BytesIO(airports_raw)
        airports = self.airportSerializer.from_chunk(reader)
        logging.info(f'action: new_chunk_received | chunck_len {len(airports)}')
        
        
        location = (0,0)
        for airport in airports:
            airport_loc = (airport.latitude, airport.longitude)

            distance = geodesic(location, airport_loc).miles
            self.airports[airport.cod] = (airport.latitude, airport.longitude)
            logging.info(f'action: save | value: {airport} | distance: {distance}')
            location = airport_loc

        # save to file
        # self.middleware.ack()?

    def recv_flights(self,flights_raw):
        if is_flight_eof(flights_raw):
            logging.info(f'action: recv flight EOF | result: stop receiving flights')
            self.middleware.stop_receiving()
            return 
        

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | singal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')
