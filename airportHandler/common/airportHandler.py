import logging
from common.airportHandlerMiddleware import AirportHandlerMiddleware
from airportSerializer import AirportSerializer

class AirportHandler():
    def __init__(self):
        self.airports = {} #cod: (lat, lon)
        self.airportSerializer = AirportSerializer()

        # last thing to do:
        self.middleware = AirportHandlerMiddleware(self.save_airport)

    def run(self):
        self.recv_airports()

    def save_airport(self, airport_raw):
        airport = self.airportSerializer.from_bytes(airport_raw)
        self.airports[airport.cod] = (airport.latitude, airport.longitude)
        logging.info(f'action: save | value: {airport}')

        # save to file
        # self.middleware.ack()?