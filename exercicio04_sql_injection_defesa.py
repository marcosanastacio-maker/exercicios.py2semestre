"""
Exercicio 4 - Query parametrizada (defesa contra SQL Injection)

Demonstra duas formas de buscar usuario por nome:
- busca_insegura: concatena a entrada diretamente na query (vulneravel)
- busca_segura: usa query parametrizada (%s / placeholder), imune

Nota: aqui o banco usado para a demonstracao real e o sqlite3
(builtin do Python, sem precisar de servidor externo), pois o
comportamento da injecao e identico em qualquer motor SQL.
Para rodar em MySQL de verdade, troque a conexao por
mysql.connector.connect(...) e mantenha os mesmos dois estilos de
query: concatenacao (insegura) vs "%s" com tupla de parametros (segura)
- a API do mysql-connector usa exatamente essa mesma sintaxe de %s.
"""

import sqlite3


def preparar_banco(usuarios):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    cursor.executemany(
        "INSERT INTO usuarios (nome, email) VALUES (?, ?)",
        usuarios
    )
    conn.commit()
    return conn


# ------------------------------------------------------------
# Versao INSEGURA: concatena a entrada direto na string SQL.
# Equivalente em mysql-connector seria:
#   query = f"SELECT * FROM usuarios WHERE nome = '{entrada}'"
#   cursor.execute(query)
# ------------------------------------------------------------
def busca_insegura(conn, entrada):
    cursor = conn.cursor()
    query = f"SELECT * FROM usuarios WHERE nome = '{entrada}'"
    cursor.execute(query)
    return cursor.fetchall()


# ------------------------------------------------------------
# Versao SEGURA: usa placeholder + tupla de parametros.
# Em mysql-connector seria:
#   cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (entrada,))
# ------------------------------------------------------------
def busca_segura(conn, entrada):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nome = ?", (entrada,))
    return cursor.fetchall()


if __name__ == "__main__":
    usuarios = [
        ("admin", "admin@x.com"),
        ("ana", "ana@x.com"),
        ("bruno", "bruno@x.com"),
    ]
    entrada = "' OR '1'='1"

    conn = preparar_banco(usuarios)

    resultado_inseguro = busca_insegura(conn, entrada)
    print(f"[INSEGURO] entrada={entrada}  -> {len(resultado_inseguro)} usuários (VAZAMENTO)")

    resultado_seguro = busca_segura(conn, entrada)
    print(f"[SEGURO]   entrada={entrada}  -> {len(resultado_seguro)} usuários (defesa OK)")

    conn.close()
