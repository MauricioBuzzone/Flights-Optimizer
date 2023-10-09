import logging
from middleware.middleware import Middleware

class Query3SynchronizerMiddleware(Middleware):
    def __init__(self):
        super().__init__()

        # Declare Q3-sync queue
        self.sync_queue_name = 'Q3-sync'
        self.channel.queue_declare(queue=self.sync_queue_name, durable=True)
        logging.info(f'action: declare_sync_queue | queue: {self.sync_queue_name}')

        # Declare results exchange
        self.channel.exchange_declare(exchange='results', exchange_type='direct')

    def listen_results(self, callback):
        self.consuming_queue(callback, self.sync_queue_name)

    def publish_results(self, results):
        self.send_msg(routing_key='Q3', data=results, exchange='results')