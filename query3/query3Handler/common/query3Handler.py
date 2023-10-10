import io
import logging
import signal
from utils.protocol import is_eof, make_eof 
from common.query3HandlerMiddleware import Query3HandlerMiddleware

class Query3Handler():
    def __init__(self, chunk_size):
        signal.signal(signal.SIGTERM, self.__handle_signal)
        self.chunk_size = chunk_size

        # last thing to do:
        self.middleware = Query3HandlerMiddleware()

    def run(self):
        logging.info(f'action: listen_flights | result: in_progress')
        self.middleware.listen_flights(self.recv_flights)
        logging.info(f'action: listen_flights | result: success')

        self.middleware.start()

        self.middleware.stop()

    def recv_flights(self, flights_raw):
        if is_eof(flights_raw):
           return self.recv_eof(flights_raw)

        self.middleware.publish_flights(flights_raw)
        return True

    def recv_eof(self, eof):
        eof = make_eof(0)
        self.middleware.send_eof_to_workers(eof)
        return False

    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | singal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')