"""
Exercicio 1 - Modelagem e CRUD SQL (via Python)
Gerenciamento de ativos de TI usando MySQL + mysql-connector-python

Nivel intermediario: funcoes separadas por responsabilidade,
tratamento de erro com try/except, uso de parametros (%s) para
evitar SQL injection, sem ORM.
"""

import mysql.connector
from mysql.connector import Error


# ------------------------------------------------------------
# Conexao com o banco
# ------------------------------------------------------------
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sua_senha",
        database="inventario"
    )


# ------------------------------------------------------------
# Criacao da tabela
# ------------------------------------------------------------
def criar_tabela(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ativos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            ip VARCHAR(45) NOT NULL UNIQUE,
            tipo VARCHAR(50) NOT NULL,
            criticidade ENUM('baixa', 'media', 'alta') NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'ativo'
        )
    """)
    conn.commit()
    cursor.close()
    print("Tabela 'ativos' criada (ou ja existente).")


# ------------------------------------------------------------
# Inserir ativo (trata IP duplicado - UNIQUE)
# ------------------------------------------------------------
def inserir_ativo(conn, nome, ip, tipo, criticidade, status):
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO ativos (nome, ip, tipo, criticidade, status)
               VALUES (%s, %s, %s, %s, %s)""",
            (nome, ip, tipo, criticidade, status)
        )
        conn.commit()
        print(f"Ativo '{nome}' inserido com sucesso.")
    except mysql.connector.IntegrityError:
        print(f"Erro: IP '{ip}' ja cadastrado (violacao de UNIQUE).")
    finally:
        cursor.close()


# ------------------------------------------------------------
# Listar ativos filtrando por tipo
# ------------------------------------------------------------
def listar_por_tipo(conn, tipo):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, ip, criticidade, status FROM ativos WHERE tipo = %s",
        (tipo,)
    )
    resultados = cursor.fetchall()
    cursor.close()

    if not resultados:
        print(f"Nenhum ativo do tipo '{tipo}' encontrado.")
        return

    for nome, ip, criticidade, status in resultados:
        print(f"{nome} | {ip} | {criticidade} | {status}")


# ------------------------------------------------------------
# Atualizar status de um ativo
# ------------------------------------------------------------
def atualizar_status(conn, nome, novo_status):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE ativos SET status = %s WHERE nome = %s",
        (novo_status, nome)
    )
    conn.commit()
    linhas_afetadas = cursor.rowcount
    cursor.close()
    print(f"{linhas_afetadas} registro atualizado")


# ------------------------------------------------------------
# Remover ativo
# ------------------------------------------------------------
def remover_ativo(conn, nome):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ativos WHERE nome = %s", (nome,))
    conn.commit()
    linhas_afetadas = cursor.rowcount
    cursor.close()
    print(f"{linhas_afetadas} registro removido")


# ------------------------------------------------------------
# Execucao principal
# ------------------------------------------------------------
if __name__ == "__main__":
    ativos = [
        ("SRV-WEB01", "192.168.1.10", "servidor", "alta",  "ativo"),
        ("PC-RH03",   "192.168.1.45", "estacao",  "baixa", "ativo"),
        ("SW-CORE01", "192.168.1.1",  "switch",   "media", "inativo"),
    ]

    conn = None
    try:
        conn = conectar()

        # 1. Criar tabela
        criar_tabela(conn)

        # 2. Inserir dados iniciais
        for nome, ip, tipo, criticidade, status in ativos:
            inserir_ativo(conn, nome, ip, tipo, criticidade, status)

        # 3. Listar filtrando por tipo='servidor'
        print("\n--- Listando tipo='servidor' ---")
        listar_por_tipo(conn, "servidor")

        # 4. Atualizar status de SW-CORE01 para 'ativo'
        print("\n--- Atualizando status ---")
        atualizar_status(conn, "SW-CORE01", "ativo")

        # 5. Tentar inserir IP duplicado (192.168.1.10 ja existe)
        print("\n--- Testando IP duplicado ---")
        inserir_ativo(conn, "SRV-WEB02", "192.168.1.10", "servidor", "media", "ativo")

        # 6. Remover um ativo
        print("\n--- Removendo ativo ---")
        remover_ativo(conn, "PC-RH03")

    except Error as e:
        print(f"Erro ao conectar/operar no MySQL: {e}")

    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            print("\nConexao encerrada.")
