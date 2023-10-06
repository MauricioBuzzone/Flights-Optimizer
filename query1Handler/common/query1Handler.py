import io
import logging
import signal

from common.query1HandlerMiddleware import Query1HandlerMiddleware
from utils.flightQ1Serializer import FlightQ1Serializer
from utils.protocol import is_flight_eof, get_closed_peers, make_flight_eof

class Query1Handler():
    def __init__(self, peers):
        signal.signal(signal.SIGTERM, self.__handle_signal)
        self.peers = peers
        self.flightSerializer = FlightQ1Serializer()

        # last thing to do:
        self.middleware = Query1HandlerMiddleware()

    def run(self):
        logging.info(f'action: listen_flights | result: in_progress')
        self.middleware.listen_flights(self.recv_flights)
        logging.info(f'action: listen_flights | result: success')

        self.middleware.start()
        logging.info(f"ESTOY POR CERRAR")
        self.middleware.stop()

    def recv_flights(self, flights_raw):

        if is_flight_eof(flights_raw):
           return self.recv_eof(flights_raw)
           

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

        return True

    def recv_eof(self,eof):
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
            last_eof = make_flight_eof(0)
            self.middleware.publish_results(last_eof)

        return False


    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | singal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')