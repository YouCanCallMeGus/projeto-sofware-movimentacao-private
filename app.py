from flask import Flask, request, jsonify
from app_service import validar_campos, calcular_valor, criar_objeto_movimentacao
from pymongo import MongoClient
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
DB_URL = os.getenv("DB_URL") 

# "Banco de dados" em memória
client = MongoClient(f"mongodb://{DB_URL}/") 
db = client["movimentacoes"]
movimentacoes_collection = db["movimentacoes"]  


## docker run -p 27017:27017 -d --network=rede --name mongo mongo

# ------------------------
# Rotas
# ------------------------

@app.route("/movimentacoes", methods=["POST"])
def criar_movimentacao():
    data = request.get_json()

    erro = validar_campos(data)
    if erro:
        return jsonify({"erro": erro}), 400

    valor_total, erro = calcular_valor(data["ticker"], data["quantidade"])
    if erro:
        return jsonify({"erro": erro}), 400

    movimentacao = criar_objeto_movimentacao(data, valor_total)

    result = movimentacoes_collection.insert_one(movimentacao)

    movimentacao["_id"] = str(result.inserted_id)
    return jsonify(movimentacao), 201


@app.route("/movimentacoes", methods=["GET"])
def listar_movimentacoes():
    docs = list(movimentacoes_collection.find())
    for d in docs:
        d["_id"] = str(d["_id"])
    return jsonify(docs)


if __name__ == "__main__":
    app.run(debug=True)
