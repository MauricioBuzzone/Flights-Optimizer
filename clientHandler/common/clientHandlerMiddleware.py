import pika
from middleware.middleware import Middleware

class ClientHandlerMiddleware(Middleware):
    def __init__(self):
        super().__init__()
        
        # Declare exchange to send airports
        self.channel.exchange_declare(exchange='airports', exchange_type='fanout')

        # Declare exchange to send flights to QUERY2
        self.channel.exchange_declare(exchange='Q2-flights', exchange_type='direct')

    def send_airport(self, bytes):
        self.send_msg(routing_key='', data=bytes, exchange='airports')

    def send_flightsQ2(self, bytes):
        self.send_msg(routing_key='', data=bytes, exchange='Q2-flights')
