"""
Exercicio 10 (Desafio) - Mini-pipeline SIEM: log -> MongoDB -> ML

Fluxo:
1. Le o auth.log e normaliza cada linha em um documento.
2. Insere todos os documentos no MongoDB.
3. Para cada IP, calcula via agregacao a contagem de FAILs.
4. Monta um dataset [qtd_fails] e rotula IP como suspeito (1) se
   qtd_fails >= 5, senao 0.
5. Treina um classificador e preve o rotulo de um IP novo com
   8 falhas.
"""

import re

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from sklearn.tree import DecisionTreeClassifier

LINHA_REGEX = re.compile(
    r"^(?P<timestamp>\S+ \S+)\s+(?P<tipo>\S+)\s+usuario=(?P<usuario>\S+)\s+ip=(?P<ip>\S+)$"
)


def conectar():
    cliente = MongoClient("mongodb://localhost:27017/")
    db = cliente["seguranca"]
    return cliente, db["auth_events"]


# ------------------------------------------------------------
# 1. Parsing do auth.log
# ------------------------------------------------------------
def parsear_log(caminho_arquivo):
    eventos = []
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha:
                continue
            match = LINHA_REGEX.match(linha)
            if not match:
                continue
            eventos.append(match.groupdict())
    return eventos


# ------------------------------------------------------------
# 2. Insercao no MongoDB
# ------------------------------------------------------------
def inserir_eventos(colecao, eventos):
    resultado = colecao.insert_many(eventos)
    print(f"Eventos inseridos no MongoDB: {len(resultado.inserted_ids)}")


# ------------------------------------------------------------
# 3. Agregacao: contagem de FAILs por IP
# ------------------------------------------------------------
def contar_fails_por_ip(colecao):
    pipeline = [
        {"$match": {"tipo": "FAIL"}},
        {"$group": {"_id": "$ip", "qtd_fails": {"$sum": 1}}},
        {"$sort": {"qtd_fails": -1}},
    ]
    return list(colecao.aggregate(pipeline))


# ------------------------------------------------------------
# 4. Montagem do dataset rotulado
# ------------------------------------------------------------
def montar_dataset(contagens, limite_suspeito=5):
    X = []
    y = []
    for doc in contagens:
        qtd_fails = doc["qtd_fails"]
        rotulo = 1 if qtd_fails >= limite_suspeito else 0
        X.append([qtd_fails])
        y.append(rotulo)
    return X, y


# ------------------------------------------------------------
# 5. Treinamento e previsao
# ------------------------------------------------------------
def treinar_e_prever(X, y, novo_valor):
    modelo = DecisionTreeClassifier(random_state=42)
    modelo.fit(X, y)
    predicao = modelo.predict([[novo_valor]])[0]
    return predicao


if __name__ == "__main__":
    cliente = None
    try:
        cliente, colecao = conectar()
        colecao.delete_many({})  # reexecucao idempotente

        # 1. Parse
        eventos = parsear_log("auth.log")

        # 2. Insercao
        inserir_eventos(colecao, eventos)

        # 3. Agregacao
        contagens = contar_fails_por_ip(colecao)
        print("\n--- FAILs por IP ---")
        for doc in contagens:
            suspeito = 1 if doc["qtd_fails"] >= 5 else 0
            print(f"{doc['_id']} -> {doc['qtd_fails']} FAILs (suspeito={suspeito})")

        # 4. Dataset
        X, y = montar_dataset(contagens, limite_suspeito=5)
        print(f"\nDataset de treino: {X} rótulos {y}")

        # 5. Previsao para IP novo com 8 falhas
        predicao = treinar_e_prever(X, y, novo_valor=8)
        resultado = "Suspeito (1)" if predicao == 1 else "Normal (0)"
        print(f"Previsão para IP com 8 falhas -> {resultado}")

    except PyMongoError as e:
        print(f"Erro ao conectar/operar no MongoDB: {e}")

    finally:
        if cliente is not None:
            cliente.close()
            print("\nConexão encerrada.")
