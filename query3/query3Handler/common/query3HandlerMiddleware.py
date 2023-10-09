import logging

from middleware.middleware import Middleware

class Query3HandlerMiddleware(Middleware):
    def __init__(self):
        super().__init__()

        # Declare IN-flights exchange (publisher-subscriber)
        self.channel.exchange_declare(exchange='results', exchange_type='direct')
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.flights_queue_name = result.method.queue
        self.channel.queue_bind(exchange='results', queue=self.flights_queue_name, routing_key=f'Q1')

        # Declare Q3-workers queue (producer-consumer)
        self.flights_workers_queue_name = 'Q3-workers'
        self.channel.queue_declare(queue=self.flights_workers_queue_name, durable=True)
        logging.info(f'action: declare_flights_queue | queue: {self.flights_queue_name}')

    def listen_flights(self, callback):
        self.consuming_queue(callback, self.flights_queue_name)

    def publish_flights(self, flights):
        self.send_msg(routing_key=self.flights_workers_queue_name, data=flights, exchange='')

    def send_eof_to_workers(self, eof):
        self.send_msg(routing_key=self.flights_workers_queue_name, data=eof, exchange='')
