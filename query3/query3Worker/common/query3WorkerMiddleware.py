import logging
from middleware.middleware import Middleware

class Query3WorkerMiddleware(Middleware):
    def __init__(self):
        super().__init__()
        # Declare Q4-workers queue
        self.flights_workers_queue_name = 'Q3-workers'
        self.channel.queue_declare(queue=self.flights_workers_queue_name, durable=True)
        logging.info(f'action: declare_workers_queue | queue: {self.flights_workers_queue_name}')

        # Declare Q3-sync queue
        self.sync_queue_name = 'Q3-sync'
        self.channel.queue_declare(queue=self.sync_queue_name, durable=True)
        logging.info(f'action: declare_sync_queue | queue: {self.sync_queue_name}')

    def listen_flights(self, callback):
        self.consuming_queue(callback, self.flights_workers_queue_name)

    def publish_results(self, results):
        self.send_msg(routing_key=self.sync_queue_name, data=results, exchange='')

    def resend_eof(self, eof):
        self.send_msg(routing_key=self.flights_workers_queue_name, data=eof, exchange='')