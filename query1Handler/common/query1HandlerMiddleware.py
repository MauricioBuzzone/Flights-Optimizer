import logging
from middleware.middleware import Middleware

class Query1HandlerMiddleware(Middleware):
    def __init__(self):
        super().__init__()

        # Declare flights Q1 queue (producer-consumer)
        self.flights_queue_name = 'Q1-flights'
        self.channel.queue_declare(queue=self.flights_queue_name, durable=True)
        logging.info(f"action: declare_flights_queue | queue: {self.flights_queue_name}")

        # Declare results exchange
        self.channel.exchange_declare(exchange='results', exchange_type='direct')

    def start(self):
        self.channel.start_consuming()

    def callback_flights(self, ch, method, properties, body):
        self._callback_flights(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def listen_flights(self, callback):
        self._callback_flights = callback
        self.channel.basic_consume(queue=self.flights_queue_name, on_message_callback=self.callback_flights)

    def stop_listen_flights(self):
        # stop consuming from 'Q1-flights' queue
        return

    def publish_results(self, results):
        self.send_msg(routing_key='Q1', data=results, exchange='results')