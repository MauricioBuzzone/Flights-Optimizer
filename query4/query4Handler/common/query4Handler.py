import io
import logging
import signal

from utils.protocol import is_eof, make_eof
from model.flight import Flight
from model.duration import Duration
from utils.flightQ4Serializer import FlightQ4Serializer
from common.query4HandlerMiddleware import Query4HandlerMiddleware

class Query4Handler():
    def __init__(self, chunk_size):
        signal.signal(signal.SIGTERM, self.__handle_signal)
        self.flightSerializer = FlightQ4Serializer()

        self.flights_list = []
        self.avg = 0
        self.n = 0

        self.chunk_size = chunk_size

        # last thing to do:
        self.middleware = Query4HandlerMiddleware()

    def run(self):
        logging.info(f'action: listen_flights | result: in_progress')
        self.middleware.listen_flights(self.recv_flights)
        logging.info(f'action: listen_flights | result: success')

        self.middleware.start()

        self.middleware.stop()

    def recv_flights(self, flights_raw):
        if is_eof(flights_raw):
           return self.recv_eof(flights_raw)

        reader = io.BytesIO(flights_raw)
        flights = self.flightSerializer.from_chunk(reader)
        logging.info(f'action: new_chunk_flights | chunck_len: {len(flights)}')

        for flight in flights:
            self.avg = (self.avg*self.n + flight.total_fare) / (self.n+1)
            # ¿A disco?
            self.flights_list.append((flight.id, flight.origin, flight.destiny, flight.total_fare))
            self.n += 1

        return True

    def recv_eof(self, eof):
        logging.info(f'action: calculate_average | result: success | value: {self.avg} | n_value: {self.n}')

        chunk = []
        while self.flights_list:
            id, origin, destiny, total_fare = self.flights_list.pop()
            if total_fare > self.avg:
                flight = Flight(id = id, origin = origin, destiny = destiny, total_distance=0,
                                total_fare=total_fare, legs=[], flight_duration=Duration(0,0))
                chunk.append(flight)
                if len(chunk) >= self.chunk_size:
                    logging.info(f'action: publishing_chunk | len(chunk): {len(chunk)}')
                    data = self.flightSerializer.to_bytes(chunk)
                    self.middleware.publish_flights(data)
                    chunk = []
        if chunk:
            logging.info(f'action: publishing_chunk | len(chunk): {len(chunk)}')
            data = self.flightSerializer.to_bytes(chunk)
            self.middleware.publish_flights(data)

        eof = make_eof(0)
        self.middleware.send_eof_to_workers(eof)

        return False

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | singal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')