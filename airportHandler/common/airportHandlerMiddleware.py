import pika

class AirportHandlerMiddleware():
    def __init__(self, recv_airports_callback):

        self.recv_airports_callback = recv_airports_callback

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

        # publisher-subscribe
        self.channel.exchange_declare(exchange='airports', exchange_type='fanout')

        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='airports', queue=queue_name)

        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.__recv_airport_callback,
            auto_ack=True) # check autoack
        
        self.channel.start_consuming()

    def __recv_airport_callback(self, ch, method, properties, body):
        self.recv_airports_callback(body)

    def close(self):
        self.connection.close()