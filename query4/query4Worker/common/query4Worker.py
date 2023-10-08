import io
import logging
import signal

from utils.flightQ4Serializer import FlightQ4Serializer
from utils.resultQ4Serializer import ResultQ4Serializer
from utils.resultQ4 import ResultQ4
from common.query4WorkerMiddleware import Query4WorkerMiddleware
from utils.protocol import is_flight_eof, get_closed_peers, make_flight_eof, make_resultQ4_eof

class Query4Worker():
    def __init__(self, peers, chunk_size):
        signal.signal(signal.SIGTERM, self.__handle_signal)

        self.flightSerializer = FlightQ4Serializer()
        self.resultSerializer = ResultQ4Serializer()

        self.results = {}
        self.peers = peers
        self.chunk_size = chunk_size

        # last thing to do:
        self.middleware = Query4WorkerMiddleware()

    def run(self):
        logging.info(f'action: listen_flights | result: in_progress')
        self.middleware.listen_flights(self.recv_flights)
        logging.info(f'action: listen_flights | result: success')

        self.middleware.start()

        self.middleware.stop()

    def recv_flights(self, flights_raw):
        if is_flight_eof(flights_raw):
           return self.recv_eof(flights_raw)

        reader = io.BytesIO(flights_raw)
        flights = self.flightSerializer.from_chunk(reader)
        logging.info(f'action: new_chunk_flights | chunck_len: {len(flights)}')

        for flight in flights:
            journey = (flight.origin, flight.destiny)
            if journey in self.results:
                self.results[journey].update_fare(flight.total_fare)
            else:
                self.results[journey] = ResultQ4(origin=flight.origin,
                                                 destiny=flight.destiny,
                                                 fare_avg=flight.total_fare,
                                                 fare_max=flight.total_fare,
                                                 n=1)

        return True

    def send_results(self):
        chunk = []
        for result in self.results.values():
            logging.info(f'action: publish_result | value: {result}')
            chunk.append(result)
            if len(chunk) >= self.chunk_size:
                data = self.resultSerializer.to_bytes(chunk)
                self.middleware.publish_results(data)
                chunk = []
        if chunk:
            data = self.resultSerializer.to_bytes(chunk)
            self.middleware.publish_results(data)

    def handle_eof(self, eof):
        closed_peers = get_closed_peers(eof)
        if closed_peers == -1:
            logging.error(f'action: close | result: fail | e = Error to parse eof')

        if closed_peers < self.peers - 1:
            # Send EOF to other peers.
            logging.info(f'action: recv EOF | result: in_progress | peers = {self.peers} | closed_peers: {closed_peers}')
            new_eof = make_flight_eof(closed_peers + 1)
            self.middleware.resend_eof(new_eof)
        else:
            # All my peers are closed, send EOF to ResultQueue
            logging.info(f'action: recv EOF | result: in_progress | peers = {self.peers} | closed_peers: {closed_peers}')
            last_eof = make_resultQ4_eof(0)
            self.middleware.publish_results(last_eof)

    def recv_eof(self, eof):
        self.send_results()
        self.handle_eof(eof)
        return False

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | signal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')