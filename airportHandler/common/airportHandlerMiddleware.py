import pika
from middleware.middleware import Middleware

class AirportHandlerMiddleware(Middleware):
    def __init__(self):
        super().__init__()
 
        # Declare airports exchange (publisher-subscribe)
        self.channel.exchange_declare(exchange='airports', exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.airport_queue_name = result.method.queue
        self.channel.queue_bind(exchange='airports', queue=self.airport_queue_name)
 
        # Declare flights exchange (producer-consumer)
        self.channel.exchange_declare(exchange='Q2-flights', exchange_type='direct')
        result = self.channel.queue_declare(queue='', durable=True)
        self.flights_queue_name = result.method.queue
        self.channel.queue_bind(exchange='Q2-flights', queue=self.flights_queue_name)

    
    def recieve_airports(self, callback):
        self.consuming_queue(callback, self.airport_queue_name)
    
    def receive_flights(self, callback):
        self.channel.basic_qos(prefetch_count=1)
        self.consuming_queue(callback, self.flights_queue_name)