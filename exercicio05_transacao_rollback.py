"""
Exercicio 5 - Transacao com rollback (MySQL)

Simula uma transferencia entre duas contas. Se a segunda operacao
falhar (conta destino inexistente), faz rollback e prova que o saldo
da conta de origem nao mudou.
"""

import mysql.connector
from mysql.connector import Error


def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sua_senha",
        database="banco_lab"
    )


def criar_tabela(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INT PRIMARY KEY,
            titular VARCHAR(100) NOT NULL,
            saldo DECIMAL(10, 2) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()


def popular_contas(conn, contas):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contas")  # reexecucao idempotente
    cursor.executemany(
        "INSERT INTO contas (id, titular, saldo) VALUES (%s, %s, %s)",
        contas
    )
    conn.commit()
    cursor.close()


def consultar_saldo(conn, conta_id):
    cursor = conn.cursor()
    cursor.execute("SELECT saldo FROM contas WHERE id = %s", (conta_id,))
    linha = cursor.fetchone()
    cursor.close()
    return linha[0] if linha else None


def transferir(conn, origem_id, destino_id, valor):
    """
    Executa a transferencia dentro de uma transacao.
    Retorna (sucesso: bool, mensagem: str).
    """
    cursor = conn.cursor()
    try:
        # 1. Verifica se a conta de origem existe e tem saldo suficiente
        cursor.execute("SELECT saldo FROM contas WHERE id = %s FOR UPDATE", (origem_id,))
        origem = cursor.fetchone()
        if origem is None:
            raise ValueError(f"Conta de origem {origem_id} nao existe.")
        if origem[0] < valor:
            raise ValueError(f"Saldo insuficiente na conta {origem_id}.")

        # 2. Verifica se a conta de destino existe
        cursor.execute("SELECT id FROM contas WHERE id = %s FOR UPDATE", (destino_id,))
        destino = cursor.fetchone()
        if destino is None:
            raise ValueError(f"Conta de destino {destino_id} nao existe.")

        # 3. Debita da origem e credita no destino
        cursor.execute(
            "UPDATE contas SET saldo = saldo - %s WHERE id = %s",
            (valor, origem_id)
        )
        cursor.execute(
            "UPDATE contas SET saldo = saldo + %s WHERE id = %s",
            (valor, destino_id)
        )

        conn.commit()
        return True, "commit"

    except (ValueError, Error) as e:
        conn.rollback()
        return False, str(e)

    finally:
        cursor.close()


if __name__ == "__main__":
    contas = [(1, "Alice", 1000), (2, "Bob", 500)]

    conn = None
    try:
        conn = conectar()
        criar_tabela(conn)
        popular_contas(conn, contas)

        # Transferencia 1: Alice -> Bob, 200 (deve funcionar)
        ok, msg = transferir(conn, origem_id=1, destino_id=2, valor=200)
        saldo_alice = consultar_saldo(conn, 1)
        saldo_bob = consultar_saldo(conn, 2)
        if ok:
            print(f"Transferência 1 OK. Alice={saldo_alice}, Bob={saldo_bob}")
        else:
            print(f"Transferência 1 FALHOU: {msg}")

        # Transferencia 2: Alice -> conta 99 (nao existe, deve dar rollback)
        ok, msg = transferir(conn, origem_id=1, destino_id=99, valor=100)
        saldo_alice = consultar_saldo(conn, 1)
        if not ok:
            print(f"Transferência 2 FALHOU (conta destino inexistente). Rollback. Alice={saldo_alice}")
        else:
            print(f"Transferência 2 OK (inesperado). Alice={saldo_alice}")

    except Error as e:
        print(f"Erro ao conectar/operar no MySQL: {e}")

    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            print("\nConexão encerrada.")
