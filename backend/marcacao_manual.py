import pika
import json
import time
from datetime import datetime

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "presenca"

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

print("🟢 Marcação manual da chamada")
print("Digite o nome do aluno e pressione Enter para enviar a presença.\n")

try:
    while True:
        nome = input("Nome do aluno: ").strip()
        if not nome:
            continue
        mensagem = {
            "aluno": nome,
            "uid": "Registro Manual",
            "horario": datetime.now().isoformat()
        }
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=json.dumps(mensagem))
        print(f"✅ Presença enviada: {mensagem}")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nEncerrando simulador...")
    connection.close()