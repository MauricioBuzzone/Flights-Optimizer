import logging
from middleware.middleware import Middleware

class Query1Middleware(Middleware):
    def __init__(self):
        super().__init__()

        # Declare flights Q1 queue (producer-consumer)
        self.flights_queue_name = 'Q1-flights'
        self.channel.queue_declare(queue=self.flights_queue_name, durable=True)
        logging.info(f"action: declare_flights_queue | queue: {self.flights_queue_name}")

        # Declare results exchange
        self.channel.exchange_declare(exchange='results', exchange_type='direct')
            
    def listen_flights(self, callback):
        self.consuming_queue(callback, self.flights_queue_name)
        
    def resend_eof(self,eof):
        self.send_msg(routing_key='Q1-flights', data=eof, exchange='')

    def publish_results(self, results):
        self.send_msg(routing_key='Q1', data=results, exchange='results')