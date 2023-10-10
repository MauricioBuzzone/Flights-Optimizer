import io
import logging
import signal

from utils.querySynchronizer.querySynchronizerMiddleware import QuerySynchronizerMiddleware
from utils.protocol import is_eof, make_eof
from utils.resultQ3Serializer import ResultQ3Serializer


class QuerySynchronizer():
    def __init__(self, chunk_size, in_queue_name: str, in_serializer, tag_out: str, out_serializer):
        signal.signal(signal.SIGTERM, self.__handle_signal)
        
        self.in_serializer = in_serializer
        self.out_serializer = out_serializer
        self.chunk_size = chunk_size

        self.results = {}

        self.middleware = QuerySynchronizerMiddleware(in_queue_name, tag_out)

    def run(self):
        logging.info(f'action: listen_flights | result: in_progress')
        self.middleware.listen(self.recv)
        logging.info(f'action: listen_flights | result: success')

        self.middleware.start()

        self.middleware.stop()

    def work(self, input):
        raise RuntimeError("Must be redefined")

    def recv(self, raw):
        if is_eof(raw):
           return self.recv_eof(raw)

        reader = io.BytesIO(raw)
        input_chunk = self.in_serializer.from_chunk(reader)
        logging.info(f'action: new_chunk | chunck_len: {len(input_chunk)}')

        for input in input_chunk:
            self.work(input)
        return True

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

    def recv_eof(self, eof):
        self.send_results()
        last_eof = make_eof(0)
        self.middleware.publish(last_eof)
        return False

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | signal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')
