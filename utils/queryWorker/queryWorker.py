import io
import logging
import signal

from utils.queryWorker.queryWorkerMiddleware import QueryWorkerMiddleware
from utils.protocol import is_eof, get_closed_peers, make_eof

class QueryWorker():
    def __init__(self, peers, chunk_size, in_queue_name: str, in_serializer, out_queue_name: str, out_serializer):
        signal.signal(signal.SIGTERM, self.__handle_signal)

        self.in_serializer = in_serializer
        self.out_serializer = out_serializer

        self.results = {}
        self.peers = peers
        self.chunk_size = chunk_size

        self.middleware = QueryWorkerMiddleware(in_queue_name, out_queue_name)

    def run(self):
        logging.info(f'action: listen_flights | result: in_progress')
        self.middleware.listen(self.recv)
        logging.info(f'action: listen_flights | result: success')

        self.middleware.start()

        self.middleware.stop()

    def work(self, input):
        raise RuntimeError("Must be redefined")

    def handle_eof(self, eof):
        closed_peers = get_closed_peers(eof)
        if closed_peers == -1:
            logging.error(f'action: close | result: fail | e = Error to parse eof')

        if closed_peers < self.peers - 1:
            # Send EOF to other peers.
            logging.info(f'action: recv EOF | result: in_progress | peers = {self.peers} | closed_peers: {closed_peers}')
            new_eof = make_eof(closed_peers + 1)
            self.middleware.resend(new_eof)
        else:
            # All my peers are closed, send EOF to ResultQueue
            logging.info(f'action: recv EOF | result: in_progress | peers = {self.peers} | closed_peers: {closed_peers}')
            last_eof = make_eof(0)
            self.middleware.publish(last_eof)

    def send_results(self):
        chunk = []
        for result in self.results.values():
            logging.info(f'action: publish_result | value: {result}')
            chunk.append(result)
            if len(chunk) >= self.chunk_size:
                data = self.out_serializer.to_bytes(chunk)
                self.middleware.publish(data)
                chunk = []
        if chunk:
            data = self.out_serializer.to_bytes(chunk)
            self.middleware.publish(data)

    def recv(self, raw):
        if is_eof(raw):
           return self.recv_eof(raw)

        reader = io.BytesIO(raw)
        input_chunk = self.in_serializer.from_chunk(reader)
        logging.info(f'action: new_chunk | chunck_len: {len(input_chunk)}')

        for input in input_chunk:
            self.work(input)

        return True

    def recv_eof(self, eof):
        self.send_results()
        self.handle_eof(eof)
        return False

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | signal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')
