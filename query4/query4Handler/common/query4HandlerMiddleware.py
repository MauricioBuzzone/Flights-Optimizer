import logging

from middleware.middleware import Middleware

class Query4HandlerMiddleware(Middleware):
    def __init__(self):
        super().__init__()
        
        # Declare flights Q4 queue (producer-consumer)
        self.flights_queue_name = 'Q4-flights'
        self.channel.queue_declare(queue=self.flights_queue_name, durable=True)
        logging.info(f'action: declare_flights_queue | queue: {self.flights_queue_name}')

        # Declare Q4-workers queue (producer-consumer)
        self.flights_workers_queue_name = 'Q4-workers'
        self.channel.queue_declare(queue=self.flights_workers_queue_name, durable=True)
        logging.info(f'action: declare_flights_queue | queue: {self.flights_queue_name}')

    def listen_flights(self, callback):
        self.consuming_queue(callback, self.flights_queue_name)

    def publish_flights(self, flights):
        self.send_msg(routing_key=self.flights_workers_queue_name, data=flights, exchange='')

    def send_eof_to_workers(self, eof):
        self.send_msg(routing_key=self.flights_workers_queue_name, data=eof, exchange='')