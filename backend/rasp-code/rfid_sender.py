import pika
import json
import time
from datetime import datetime
from mfrc522 import SimpleMFRC522

# --- Configuração RabbitMQ ---
RABBITMQ_HOST = "10.1.25.81"
QUEUE_NAME = "presenca"

connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

# --- Configuração RFID ---
reader = SimpleMFRC522()

# --- Alunos cadastrados ---
ALUNOS = {
    "219085403461": "Marcos",
    "703695879170": "Raul e Guilherme",
}

print("📡 Aproxime o cartão RFID do leitor...")

try:
    while True:
        id, _ = reader.read()  # Lê UID do cartão
        uid = str(id).strip()
        print(f"🪪 Cartão detectado: {uid}")

        if uid in ALUNOS:
            aluno = ALUNOS[uid]
            data = {
                "aluno": aluno,
                "uid": uid,
                "horario": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            mensagem = json.dumps(data)

            # Envia mensagem via RabbitMQ
            channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=mensagem
            )
            print(f"✅ Presença enviada: {mensagem}")
        else:
            print("⚠️ Cartão não reconhecido!")

        time.sleep(2)

except KeyboardInterrupt:
    print("\n🔴 Encerrando...")
finally:
    connection.close()