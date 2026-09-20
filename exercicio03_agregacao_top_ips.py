"""
Exercicio 3 - Agregacao: Top IPs (MongoDB / PyMongo)

Insere uma lista de eventos e usa um aggregation pipeline para
retornar os 3 IPs com mais eventos do tipo FAIL, em ordem decrescente.
"""

from pymongo import MongoClient
from pymongo.errors import PyMongoError


def conectar():
    cliente = MongoClient("mongodb://localhost:27017/")
    db = cliente["seguranca"]
    return cliente, db["eventos"]


def inserir_eventos(colecao, eventos):
    resultado = colecao.insert_many(eventos)
    print(f"{len(resultado.inserted_ids)} eventos inseridos.")


def top_ips_fail(colecao, limite=3):
    pipeline = [
        {"$match": {"tipo": "FAIL"}},
        {"$group": {"_id": "$ip", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": limite},
    ]
    return list(colecao.aggregate(pipeline))


if __name__ == "__main__":
    eventos = [
        {"tipo": "FAIL", "ip": "185.220.101.1"}, {"tipo": "FAIL", "ip": "185.220.101.1"},
        {"tipo": "OK",   "ip": "192.168.1.10"},  {"tipo": "FAIL", "ip": "91.240.118.172"},
        {"tipo": "FAIL", "ip": "185.220.101.1"}, {"tipo": "FAIL", "ip": "91.240.118.172"},
        {"tipo": "FAIL", "ip": "45.33.32.156"},  {"tipo": "FAIL", "ip": "185.220.101.1"},
    ]

    cliente = None
    try:
        cliente, colecao = conectar()
        colecao.delete_many({})  # reexecucao idempotente

        inserir_eventos(colecao, eventos)

        print("\n--- Top 3 IPs com mais FAILs ---")
        for doc in top_ips_fail(colecao, limite=3):
            print(f"{doc['_id']} -> {doc['total']}")

    except PyMongoError as e:
        print(f"Erro ao conectar/operar no MongoDB: {e}")

    finally:
        if cliente is not None:
            cliente.close()
            print("\nConexao encerrada.")
