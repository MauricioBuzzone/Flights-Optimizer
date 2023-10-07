import pika
import logging

HOST = 'rabbitmq'

class ChannelAlreadyConsuming(Exception):
    pass

class Middleware:
    def __init__(self):
        self.connection = pika.BlockingConnection(
                               pika.ConnectionParameters(host=HOST))
        self.channel = self.connection.channel()
        self.active_connection = True
        self.active_channel = False
        self.callback_func = self.__no_callback

    def start(self):
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        keep_going = self.callback_func(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        if not keep_going:
            self.stop()

    def stop(self):
        logging.info(f"action: stop_middleware | result: in_progress")
        if self.active_channel:
            logging.info(f"action: stop_middleware | close channel")
            self.active_channel = False
            self.channel.stop_consuming()

        if self.active_connection:
            logging.info(f"action: stop_middleware | close connection")
            self.active_connection = False
            self.connection.close()

        logging.info(f"action: stop_middleware | result: success")

    def send_msg(self, routing_key, data, exchange=''):
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=data,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ))

    def consuming_queue(self, callback, queue_consume):
        if self.active_channel:
            raise ChannelAlreadyConsuming()

        self.active_channel = True
        self.callback_func = callback
        logging.info(f"action: consuming_queue | queue: {queue_consume}")
        self.channel.basic_consume(queue=queue_consume, 
                                   on_message_callback=self.callback)

    def __no_callback(self, body):
        logging.error("No callback set")

    def stop_receiving(self):
        if self.active_channel:
            self.active_channel = False
            self.channel.stop_consuming()

    def __del__(self):
        try:
            if self.active_connection:
                self.connection.close()
        except OSError as e:
            logging.error(f"action: del_middleware | result: fail | error: {str(e)}")