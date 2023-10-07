import socket 
import signal
import logging

from utils.TCPHandler import SocketBroken
from utils.protocol import make_airport_eof, make_flight_eof
from utils.airportSerializer import AirportSerializer
from utils.flightSerializer import FlightSerializer
from utils.flightQ1Serializer import FlightQ1Serializer
from utils.flightQ2Serializer import FlightQ2Serializer
from utils.protocolHandler import ProtocolHandler

from common.clientHandlerMiddleware import ClientHandlerMiddleware

class ClientHandler:
    def __init__(self, port):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(1)
        self._server_on = True
        signal.signal(signal.SIGTERM, self.__handle_signal)

        self.airport_serializer = AirportSerializer()
        self.flight_serializer = FlightSerializer()
        self.flight_q1_serializer = FlightQ1Serializer()
        self.flight_q2_serializer = FlightQ2Serializer()
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
            if client_sock:
                self.__handle_client_connection(client_sock)

        self._server_socket.close()
        logging.info(f'action: release_socket | result: success')
        self.middleware.stop()
        logging.info(f'action: release_rabbitmq_conn | result: success')

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            protocolHandler = ProtocolHandler(client_sock)
            keep_reading = True
            while keep_reading:
                t, value = protocolHandler.read()

                if protocolHandler.is_airport_eof(t):
                    keep_reading = self.__handle_airport_eof()

                if protocolHandler.is_flight_eof(t):
                    keep_reading = self.__handle_flight_eof()

                if protocolHandler.is_airports(t):
                    keep_reading = self.__handle_airports(value)

                if protocolHandler.is_flights(t):
                    keep_reading = self.__handle_flights(value)

                protocolHandler.ack()
        
        except (SocketBroken,OSError) as e:
            logging.error(f'action: receive_message | result: fail | error: {e}')
        finally:
            if client_sock:
                logging.info(f'action: release_client_socket | result: success')
                client_sock.close()
                logging.info(f'action: finishing | result: success')
    
    def __handle_airport_eof(self):
        eof = make_airport_eof()
        self.middleware.send_airport(eof)

        logging.info(f'action: send_airports | value: EOF | result: success')
        return True

    def __handle_airports(self, value):
        data = self.airport_serializer.to_bytes(value)
        self.middleware.send_airport(data)

        logging.debug(f'action: send_airports | len(value): {len(value)} | result: success')
        return True

    def __handle_flight_eof(self):
        logging.info(f'action: read flight_eof | result: success')
        eof = make_flight_eof(0)
        self.middleware.send_eof(eof)
        return False
        
    def __handle_flights(self, flights):
        #  It's responsible for separating the relevant 
        #  fields for each query and sending them to different queues.
        logging.info(f'action: recived flights | result: success | N: {len(flights)}')

        # Q1:
        data = self.flight_q1_serializer.to_bytes(flights)
        self.middleware.send_flightsQ1(data)

        # Q2:
        data = self.flight_q2_serializer.to_bytes(flights)
        self.middleware.send_flightsQ2(data)

        # Q3:

        # Q4:

        return True

    def __accept_new_connection(self):
        """
        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """
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