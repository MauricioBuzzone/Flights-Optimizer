import logging
from geopy.distance import geodesic
from common.airportHandlerMiddleware import AirportHandlerMiddleware
from airportSerializer import AirportSerializer
from protocol import is_eof

class AirportHandler():
    def __init__(self):
        self.airports = {} #cod: (lat, lon)
        self.airportSerializer = AirportSerializer()

        # last thing to do:
        self.middleware = AirportHandlerMiddleware(self.save_airports)

    def run(self):
        self.recv_airports()

    def save_airports(self, airports_raw):
        if is_eof(airports_raw):
            logging.info(f'action: EOF')
            # declarar la cola p/c para los vuelos.
            return 

        
        airports = self.airportSerializer.from_bytes(airports_raw)
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