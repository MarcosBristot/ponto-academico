from flask import Flask, jsonify, request
from flask_sock import Sock
import redis
from datetime import datetime

app = Flask(__name__)
sock = Sock(app)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Lista de clientes WebSocket conectados
clients = set()

# ======== ROTAS NORMAIS (HTTP) ========

@app.route("/presencas", methods=["GET"])
def listar_presencas():
    hoje = datetime.now().strftime("%Y-%m-%d")
    chave = f"presencas:{hoje}"
    presencas = list(r.smembers(chave))
    return jsonify({"data": hoje, "presencas": presencas})

@app.route("/ws-update", methods=["POST"])
def ws_update():
    data = request.json
    mensagem = f"📢 Nova presença: {data.get('aluno', 'Desconhecido')}"
    print(mensagem)
    broadcast_mensagem(mensagem)
    return jsonify({"status": "ok"}), 200

# ======== WEBSOCKET ========

@sock.route("/ws")
def ws(ws):
    clients.add(ws)
    print("🟢 Novo cliente WebSocket conectado.")
    try:
        while True:
            data = ws.receive()
            if data:
                print(f"Mensagem recebida do cliente: {data}")
    except Exception:
        pass
    finally:
        clients.remove(ws)
        print("🔴 Cliente WebSocket desconectado.")

def broadcast_mensagem(mensagem):
    """Envia mensagem para todos os clientes conectados."""
    for client in list(clients):
        try:
            client.send(mensagem)
        except Exception:
            clients.remove(client)

# ======== EXECUÇÃO ========

if __name__ == "__main__":
    print("🚀 Servidor Flask rodando em http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)
