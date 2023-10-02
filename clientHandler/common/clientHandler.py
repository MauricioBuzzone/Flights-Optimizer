import socket 
import signal
import logging
from ProtocolHandler import ProtocolHandler
from common.clientHandlerMiddleware import ClientHandlerMiddleware
from airportSerializer import AirportSerializer
from protocol import make_eof

class ClientHandler:
    def __init__(self, port):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(1)
        self._server_on = True
        signal.signal(signal.SIGTERM, self.__handle_signal)

        self.airport_serializer = AirportSerializer()
        self.middleware = ClientHandlerMiddleware()

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        while self._server_on:
            client_sock = self.__accept_new_connection() 
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        protocolHandler = ProtocolHandler(client_sock)

        keep_reading = True
        while keep_reading:
            logging.info('action: read | result: in_progress')
            t, value = protocolHandler.read()

            if protocolHandler.is_eof(t):
                logging.info(f'action: read | result: success | received: EOF')
                keep_reading = False
                logging.info(f'action: finishing | result: in_progress')
                eof = make_eof()
                self.middleware.send_airport(eof)
            else: # check if airport?
                logging.info(f'action: read | result: success | received: {value}')
                data = self.airport_serializer.to_bytes(value)
                self.middleware.send_airport(data)
                
            protocolHandler.ack()

        logging.info(f'action: finishing | result: success')

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        try:
            logging.info('action: accept_connections | result: in_progress')
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            if self._server_on:
                logging.error(f'action: accept_connections | result: fail')
            else:
                logging.info(f'action: stop_accept_connections | result: success')
            return
        
    def __handle_signal(self, signum, frame):
        """
        Close server socket graceful
        """
        logging.info(f'action: stop_server | result: in_progress | singal {signum}')
        self._server_on = False
        self._server_socket.shutdown(socket.SHUT_RDWR)
        logging.info(f'action: shutdown_socket | result: success')