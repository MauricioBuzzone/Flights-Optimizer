import io
import logging
import signal

from common.query1HandlerMiddleware import Query1HandlerMiddleware
from utils.flightQ1Serializer import FlightQ1Serializer

class Query1Handler():
    def __init__(self):
        signal.signal(signal.SIGTERM, self.__handle_signal)

        self.flightSerializer = FlightQ1Serializer()

        # last thing to do:
        self.middleware = Query1HandlerMiddleware()

    def run(self):
        logging.info(f'action: listen_flights | result: in_progress')
        self.middleware.listen_flights(self.recv_flights)
        logging.info(f'action: listen_flights | result: success')

        self.middleware.start()

        self.middleware.stop()

    def recv_flights(self, flights_raw):
        reader = io.BytesIO(flights_raw)
        flights = self.flightSerializer.from_chunk(reader)

        logging.info(f'action: new_chunk_flights | chunck_len: {len(flights)}')

        filtered_flights = []
        for flight in flights:
            if len(flight.legs) >= 3:
                filtered_flights.append(flight)
                logging.info(f'action: publish_flight | value: {flight}')

        if filtered_flights:
            data = self.flightSerializer.to_bytes(filtered_flights)
            self.middleware.publish_results(data)

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | singal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')