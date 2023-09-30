import pika

class RabbitMQ:
    def __init__(self, host, port, user, password):
        self._credentials = pika.PlainCredentials(user, password)
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=self._credentials
        ))
        self._channel = self._connection.channel()

    def consume_messages(self, queue_name, callback):
        print(f"Consuming messages from queue: {queue_name}")
        self._channel.queue_declare(queue=queue_name, durable=True)
        self._channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
        self._channel.start_consuming()

    def acknowledge_message(self, method):
        self._channel.basic_ack(delivery_tag=method.delivery_tag)

    def publish_message(self, queue_name, message):
        self._channel.queue_declare(queue=queue_name, durable=True)
        self._channel.basic_publish(exchange='', routing_key=queue_name, body=message)

    def close_connection(self):
        self._connection.close()