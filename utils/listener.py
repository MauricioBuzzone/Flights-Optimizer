import logging
import signal

from middleware.middleware import Middleware
from utils.protocol import is_eof

class Listener():
    def __init__(self, middleware: Middleware):
        signal.signal(signal.SIGTERM, self.__handle_signal)
        self.middleware = middleware

    def recv_raw(self, raw):
        raise RuntimeError("Must be redefined")

    def recv_eof(self, eof):
        raise RuntimeError("Must be redefined")

    def recv(self, raw):
        if is_eof(raw):
            self.recv_eof(raw)
            return False

        self.recv_raw(raw)
        return True

    def run(self):
        logging.info(f'action: listen_flights | result: in_progress')
        self.middleware.listen(self.recv)
        logging.info(f'action: listen_flights | result: success')

        self.middleware.start()

        logging.info(f'action: stop | result: in_progress')
        self.middleware.stop()
        logging.info(f'action: stop | result: success')

    # VOLATIL
    def __handle_signal(self, signum, frame):
        logging.info(f'action: stop_handler | result: in_progress | signal {signum}')
        self.middleware.stop()
        logging.info(f'action: stop_handler | result: success')