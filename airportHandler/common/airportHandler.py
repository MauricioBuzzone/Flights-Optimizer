import logging
from common.airportHandlerMiddleware import AirportHandlerMiddleware
from airportSerializer import AirportSerializer

class AirportHandler():
    def __init__(self):
        self.airports = {} #cod: (lat, lon)
        self.airportSerializer = AirportSerializer()

        # last thing to do:
        self.middleware = AirportHandlerMiddleware(self.save_airports)

    def run(self):
        self.recv_airports()

    def save_airports(self, airports_raw):
        airports = self.airportSerializer.from_bytes(airports_raw)
        logging.info(f'action: new_chunk_received | chunck_len {len(airports)}')
        for airport in airports:
            self.airports[airport.cod] = (airport.latitude, airport.longitude)
            logging.info(f'action: save | value: {airport}')

        # save to file
        # self.middleware.ack()?