import pika
import json
import redis
import requests
from datetime import datetime

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "presenca"

# Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

print("🟢 Consumidor aguardando mensagens...")

def salvar_presenca(data):
    hoje = datetime.now().strftime("%Y-%m-%d")
    chave = f"presencas:{hoje}"
    aluno = data.get("aluno", "Desconhecido")
    r.sadd(chave, aluno)
    print(f"💾 Presença salva no Redis: {aluno}")
    # Notificar backend Flask via WebSocket REST-like
    try:
        requests.post("http://localhost:5000/ws-update", json=data)
    except Exception as e:
        print(f"⚠️ Falha ao enviar atualização WebSocket: {e}")

def callback(ch, method, properties, body):
    try:
        mensagem = json.loads(body)
        print(f"📩 Mensagem recebida: {mensagem}")
        salvar_presenca(mensagem)
    except json.JSONDecodeError:
        print("⚠️ Erro ao decodificar mensagem")

channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("\n🔴 Encerrando consumidor...")
    connection.close()
