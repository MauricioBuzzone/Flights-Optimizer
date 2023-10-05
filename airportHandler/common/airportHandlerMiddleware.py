import logging
import pika
from middleware.middleware import Middleware

class AirportHandlerMiddleware(Middleware):
    def __init__(self):
        super().__init__()
 
        # Declare airports exchange (publisher-subscribe)

        self.channel.exchange_declare(exchange='airports', exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.airport_queue_name = result.method.queue 
        logging.info(f"action: declare_airport_queue | queue: {self.airport_queue_name}")

        # Declare flights Q2 queue (producer-consumer)
        self.flights_queue_name = 'Q2-flights'
        self.channel.queue_declare(queue=self.flights_queue_name, durable=True)
        logging.info(f"action: declare_flights_queue | queue: {self.flights_queue_name}")

    def start(self):
        self.channel.start_consuming()

    def callback_airports(self, ch, method, properties, body):
        self._callback_airports(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def listen_airports(self, callback):
        self._callback_airports = callback
        self.channel.basic_consume(queue=self.airport_queue_name, on_message_callback=self.callback_airports)
        self.channel.queue_bind(exchange='airports', queue=self.airport_queue_name)

    def stop_listen_airports(self):
        self.channel.queue_unbind(exchange='airports', queue=self.airport_queue_name)

    def callback_flights(self, ch, method, properties, body):
        self._callback_flights(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def listen_flights(self, callback):
        self._callback_flights = callback
        self.channel.basic_consume(queue=self.flights_queue_name, on_message_callback=self.callback_flights)

    def stop_listen_flights(self):
        # stop consuming from 'Q2-flights' queue
        return

    def recieve_airports(self, callback):
        self.consuming_queue(callback, self.airport_queue_name)

    def receive_flights(self, callback):
        self.channel.basic_qos(prefetch_count=1)
        self.consuming_queue(callback, self.flights_queue_name)