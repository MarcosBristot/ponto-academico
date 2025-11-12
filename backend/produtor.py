import pika
import time
import ssl
from config import RABBIT_CONFIG

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

params = pika.URLParameters(RABBIT_CONFIG)
params.ssl_options = pika.SSLOptions(ssl_context)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='fila')

try:
    for i in range(20):
        message = f'Mensagem {i}'
        channel.basic_publish(exchange='', routing_key='fila', body=message)
        print(f'Produtor enviou: {message}')
        time.sleep(0.5)

    connection.close()
except KeyboardInterrupt:
    print(f"[MONITOR] Interrompido por vc.")
