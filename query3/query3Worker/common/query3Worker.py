import io
import logging
import signal

from utils.resultQ3 import ResultQ3
from utils.flightQ1Serializer import FlightQ1Serializer
from utils.resultQ3Serializer import ResultQ3Serializer
from common.query3WorkerMiddleware import Query3WorkerMiddleware

from utils.protocol import is_eof, get_closed_peers, make_eof

class Query3Worker():
    def __init__(self, peers, chunk_size):
        signal.signal(signal.SIGTERM, self.__handle_signal)

        self.flightSerializer = FlightQ1Serializer()
        self.resultSerializer = ResultQ3Serializer()

        self.results = {}

        self.peers = peers
        self.chunk_size = chunk_size

        # last thing to do:
        self.middleware = Query3WorkerMiddleware()

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
            journey = (flight.origin, flight.destiny)
            if journey in self.results:
                self.results[journey].update(flight)
            else:
                self.results[journey] = ResultQ3(flight)

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
            new_eof = make_eof(closed_peers + 1)
            self.middleware.resend_eof(new_eof)
        else:
            # All my peers are closed, send EOF to ResultQueue
            logging.info(f'action: recv EOF | result: in_progress | peers = {self.peers} | closed_peers: {closed_peers}')
            last_eof = make_eof(0)
            self.middleware.publish_results(last_eof)

    def recv_eof(self, eof):
        self.send_results()
        self.handle_eof(eof)
        return False

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | signal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')
