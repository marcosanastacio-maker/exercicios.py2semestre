"""
Exercicio 2 - CRUD com PyMongo
Gerenciamento de vulnerabilidades usando MongoDB + pymongo

Nivel intermediario: funcoes separadas por responsabilidade,
tratamento de erro com try/except, filtros e updates com
operadores do Mongo ($set), sem ODM.
"""

from pymongo import MongoClient
from pymongo.errors import PyMongoError


# ------------------------------------------------------------
# Conexao com o banco
# ------------------------------------------------------------
def conectar():
    cliente = MongoClient("mongodb://localhost:27017/")
    db = cliente["seguranca"]
    return cliente, db["vulnerabilidades"]


# ------------------------------------------------------------
# Inserir varias vulnerabilidades
# ------------------------------------------------------------
def inserir_vulnerabilidades(colecao, vulns):
    try:
        resultado = colecao.insert_many(vulns)
        print(f"{len(resultado.inserted_ids)} documentos inseridos.")
    except PyMongoError as e:
        print(f"Erro ao inserir documentos: {e}")


# ------------------------------------------------------------
# Buscar por severidade
# ------------------------------------------------------------
def buscar_por_severidade(colecao, severidade):
    resultados = colecao.find({"severidade": severidade})
    encontrou = False
    for doc in resultados:
        encontrou = True
        print(f"{doc['cve_id']}: {doc['tipo']}")
    if not encontrou:
        print(f"Nenhuma vulnerabilidade com severidade '{severidade}' encontrada.")


# ------------------------------------------------------------
# Atualizar campo 'corrigida' para True, por cve_id
# ------------------------------------------------------------
def marcar_como_corrigida(colecao, cve_id):
    resultado = colecao.update_one(
        {"cve_id": cve_id},
        {"$set": {"corrigida": True}}
    )
    print(f"{resultado.modified_count} documento modificado")


# ------------------------------------------------------------
# Contar quantas vulnerabilidades continuam abertas (corrigida=False)
# ------------------------------------------------------------
def contar_nao_corrigidas(colecao):
    total = colecao.count_documents({"corrigida": False})
    print(f"Vulnerabilidades nao corrigidas: {total}")
    return total


# ------------------------------------------------------------
# Remover vulnerabilidade por cve_id
# ------------------------------------------------------------
def remover_por_cve(colecao, cve_id):
    resultado = colecao.delete_one({"cve_id": cve_id})
    print(f"{resultado.deleted_count} documento removido")


# ------------------------------------------------------------
# Execucao principal
# ------------------------------------------------------------
if __name__ == "__main__":
    vulns = [
        {"cve_id": "CVE-2024-001", "tipo": "SQL Injection",  "severidade": "Alta",    "corrigida": False},
        {"cve_id": "CVE-2024-002", "tipo": "XSS",             "severidade": "Media",   "corrigida": True},
        {"cve_id": "CVE-2024-003", "tipo": "Path Traversal",  "severidade": "Critica", "corrigida": False},
    ]

    cliente = None
    try:
        cliente, colecao = conectar()

        # Limpa a colecao para reexecucoes idempotentes do exercicio
        colecao.delete_many({})

        # 1. Inserir
        inserir_vulnerabilidades(colecao, vulns)

        # 2. Buscar severidade='Alta'
        print("\n--- Buscando severidade='Alta' ---")
        buscar_por_severidade(colecao, "Alta")

        # 3. Atualizar corrigida=True na CVE-2024-001
        print("\n--- Atualizando corrigida=True (CVE-2024-001) ---")
        marcar_como_corrigida(colecao, "CVE-2024-001")

        # 4. Contar corrigida=False (deve sobrar so CVE-2024-003)
        print("\n--- Contando corrigida=False ---")
        contar_nao_corrigidas(colecao)

        # 5. Remover por cve_id (exemplo)
        print("\n--- Removendo CVE-2024-002 ---")
        remover_por_cve(colecao, "CVE-2024-002")

    except PyMongoError as e:
        print(f"Erro ao conectar/operar no MongoDB: {e}")

    finally:
        if cliente is not None:
            cliente.close()
            print("\nConexao encerrada.")
