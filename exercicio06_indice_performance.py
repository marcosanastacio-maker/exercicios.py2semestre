"""
Exercicio 6 - Indice e desempenho (MongoDB / PyMongo)

Gera 1000 eventos, cria indice no campo 'ip' e consulta por um IP
especifico.

Comentario (por que o indice importa quando a colecao cresce):
Sem indice, o Mongo faz um COLLSCAN: percorre todos os N documentos
para achar quem bate com o filtro (custo O(n), piora conforme a
colecao cresce). Com indice em 'ip', a busca usa uma estrutura de
arvore (B-tree) e localiza os documentos em O(log n), sem precisar
varrer a colecao inteira - o ganho fica cada vez mais relevante
quanto maior o volume de eventos.
"""

import random

from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError


def conectar():
    cliente = MongoClient("mongodb://localhost:27017/")
    db = cliente["seguranca"]
    return cliente, db["eventos_indexados"]


def gerar_eventos(quantidade=1000):
    ips_possiveis = [
        "185.220.101.1", "91.240.118.172", "45.33.32.156",
        "192.168.1.10", "10.0.0.5",
    ]
    tipos_possiveis = ["OK", "FAIL"]

    eventos = []
    for _ in range(quantidade):
        eventos.append({
            "ip": random.choice(ips_possiveis),
            "tipo": random.choice(tipos_possiveis),
        })
    return eventos


def inserir_eventos(colecao, eventos):
    resultado = colecao.insert_many(eventos)
    print(f"{len(resultado.inserted_ids)} eventos inseridos.")


def criar_indice_ip(colecao):
    colecao.create_index([("ip", ASCENDING)])
    print("Índice criado em 'ip'.")


def contar_por_ip(colecao, ip):
    total = colecao.count_documents({"ip": ip})
    print(f"Eventos do IP {ip}: {total}")
    return total


if __name__ == "__main__":
    random.seed(42)  # reprodutibilidade

    cliente = None
    try:
        cliente, colecao = conectar()
        colecao.drop()  # reexecucao idempotente

        eventos = gerar_eventos(1000)
        inserir_eventos(colecao, eventos)

        criar_indice_ip(colecao)

        contar_por_ip(colecao, "185.220.101.1")

        print("Comentário: sem índice a busca seria O(n) (varre tudo); com índice ~O(log n).")

    except PyMongoError as e:
        print(f"Erro ao conectar/operar no MongoDB: {e}")

    finally:
        if cliente is not None:
            cliente.close()
            print("\nConexão encerrada.")
