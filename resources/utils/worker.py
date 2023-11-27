import logging
import io

from utils.listener import Listener
from utils.chunk import Chunk
from utils.protocol import get_closed_peers, make_eof, generate_idempotency_key

class Worker(Listener):
    def __init__(self, middleware, in_serializer, out_serializer, peers, chunk_size):
        super().__init__(middleware)
        self.results = {}
        self.in_serializer = in_serializer
        self.out_serializer = out_serializer
        self.peers = peers
        self.chunk_size = chunk_size

    def do_after_work(self, idempotency_key):
        return 

    def work(self, input, idempotency_key):
        return

    def recv_raw(self, raw):
        reader = io.BytesIO(raw)
        input_chunk = self.in_serializer.from_chunk(reader)
        logging.debug(f'action: new_chunk | chunck_len: {len(input_chunk.values)}')

        for input in input_chunk.values:
            self.work(input, input_chunk.id)
        self.do_after_work(input_chunk.id)

    def recv_eof(self, eof):
        self.send_results()
        self.handle_eof(eof)

    def send_results(self):
        chunk = []
        for result in self.results.values():
            logging.debug(f'action: publish_result | value: {result}')
            chunk.append(result)
            if len(chunk) >= self.chunk_size:
                idempotency_key = generate_idempotency_key()
                _chunk = Chunk(id=idempotency_key, values=chunk)
                data = self.out_serializer.to_bytes(_chunk)
                self.middleware.publish(data)
                chunk = []
        if chunk:
            idempotency_key = generate_idempotency_key()
            _chunk = Chunk(id=idempotency_key, values=chunk)
            data = self.out_serializer.to_bytes(_chunk)
            self.middleware.publish(data)

    def handle_eof(self, eof):
        closed_peers = get_closed_peers(eof)
        if closed_peers == -1:
            logging.error(f'action: close | result: fail | e = Error to parse eof')

        if closed_peers < self.peers - 1:
            # Send EOF to other peers.
            logging.debug(f'action: recv EOF | result: in_progress | peers = {self.peers} | closed_peers: {closed_peers}')
            new_eof = make_eof(closed_peers + 1)
            self.middleware.resend(new_eof)
        else:
            # All my peers are closed, send EOF to ResultQueue
            logging.debug(f'action: recv EOF | result: in_progress | peers = {self.peers} | closed_peers: {closed_peers}')
            last_eof = make_eof(0)
            self.middleware.publish(last_eof)