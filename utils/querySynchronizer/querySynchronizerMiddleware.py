import logging
from middleware.middleware import Middleware

class QuerySynchronizerMiddleware(Middleware):
    def __init__(self, in_queue_name: str, routing_key: str):
        super().__init__()

        # Declare IN-queue
        self.sync_queue_name = in_queue_name
        self.channel.queue_declare(queue=self.sync_queue_name, durable=True)
        logging.info(f'action: declare_sync_queue | queue: {self.sync_queue_name}')

        # Declare results exchange
        self.routing_key = routing_key
        self.channel.exchange_declare(exchange='results', exchange_type='direct')

    def listen(self, callback):
        self.consuming_queue(callback, self.sync_queue_name)

    def publish(self, results):
        self.send_msg(routing_key=self.routing_key, data=results, exchange='results')