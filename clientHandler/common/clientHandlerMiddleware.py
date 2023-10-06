import pika
from middleware.middleware import Middleware

class ClientHandlerMiddleware(Middleware):
    def __init__(self):
        super().__init__()
        
        # Declare exchange to send airports
        self.channel.exchange_declare(exchange='airports', exchange_type='fanout')

        # Declare exchange to send flights to QUERY2
        self.channel.queue_declare(queue='Q2-flights', durable=True)

        # Declare exchange to send flights to QUERY1
        self.channel.queue_declare(queue='Q1-flights', durable=True)

    def send_airport(self, bytes):
        self.send_msg(routing_key='', data=bytes, exchange='airports')

    def send_flightsQ1(self, bytes):
        self.send_msg(routing_key='Q1-flights', data=bytes, exchange='')

    def send_flightsQ2(self, bytes):
        self.send_msg(routing_key='Q2-flights', data=bytes, exchange='')