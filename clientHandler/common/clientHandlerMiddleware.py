import pika
class ClientHandlerMiddleware():
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='airports', exchange_type='fanout')

    def send_airport(self, bytes):
        self.channel.basic_publish(exchange='airports', routing_key='', body=bytes)

    def close(self):
        self.connection.close()