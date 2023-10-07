import logging

from middleware.middleware import Middleware

class Query2Middleware(Middleware):
    def __init__(self):
        super().__init__()
 
        # Declare airports exchange (publisher-subscriber)

        self.channel.exchange_declare(exchange='airports', exchange_type='fanout')
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.airport_queue_name = result.method.queue 
        logging.info(f"action: declare_airport_queue | queue: {self.airport_queue_name}")

        # Declare flights Q2 queue (producer-consumer)
        self.flights_queue_name = 'Q2-flights'
        self.channel.queue_declare(queue=self.flights_queue_name, durable=True)
        logging.info(f"action: declare_flights_queue | queue: {self.flights_queue_name}")

        self.channel.exchange_declare(exchange='results', exchange_type='direct')

    def listen_airports(self, callback):
        self.consuming_queue(callback, self.airport_queue_name)
        self.channel.queue_bind(exchange='airports', queue=self.airport_queue_name)

    def stop_listen_airports(self):
        self.active_channel = False
        self.channel.queue_unbind(exchange='airports', queue=self.airport_queue_name)

    def listen_flights(self, callback):
        self.consuming_queue(callback, self.flights_queue_name)

    def stop_listen_flights(self):
        # stop consuming from 'Q2-flights' queue
        return

    def recieve_airports(self, callback):
        self.consuming_queue(callback, self.airport_queue_name)

    def receive_flights(self, callback):
        self.channel.basic_qos(prefetch_count=1)
        self.consuming_queue(callback, self.flights_queue_name)

    def resend_eof(self,eof):
        self.send_msg(routing_key='Q2-flights', data=eof, exchange='')

    def publish_results(self, results):
        self.send_msg(routing_key='Q2', data=results, exchange='results')