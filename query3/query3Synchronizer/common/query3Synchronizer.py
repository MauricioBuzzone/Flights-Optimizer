import io
import logging
import signal

from common.query3SynchronizerMiddleware import Query3SynchronizerMiddleware
from utils.protocol import is_resultQ3_eof, make_flight_eof
from utils.resultQ3Serializer import ResultQ3Serializer

class Query3Synchronizer():
    def __init__(self, chunk_size):
        signal.signal(signal.SIGTERM, self.__handle_signal)

        self.resultSerializer = ResultQ3Serializer()

        self.chunk_size = chunk_size

        self.results = {}

        # last thing to do:
        self.middleware = Query3SynchronizerMiddleware()

    def run(self):
        logging.info(f'action: listen_flights | result: in_progress')
        self.middleware.listen_results(self.recv_results)
        logging.info(f'action: listen_flights | result: success')

        self.middleware.start()

        self.middleware.stop()

    def recv_results(self, results_raw):
        if is_resultQ3_eof(results_raw):
           return self.recv_eof(results_raw)

        reader = io.BytesIO(results_raw)
        results = self.resultSerializer.from_chunk(reader)
        logging.info(f'action: new_chunk_results | chunck_len: {len(results)}')

        for result in results:
            journey = (result.fastest_flight.origin, result.fastest_flight.destiny)
            if journey in self.results:
                self.results[journey].merge(result)
            else:
                self.results[journey] = result
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

    def recv_eof(self, eof):
        self.send_results()
        # flight eof?
        last_eof = make_flight_eof(0)
        self.middleware.publish_results(last_eof)
        return False

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | signal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')