"""Upgrade incremental do schema SQLite para compatibilidade com models atuais.

Este modulo e responsavel por adicionar colunas e ajustes necessarios em
bancos ja existentes, sem recriar tabelas ou perder dados.
"""

from __future__ import annotations

from sqlalchemy import Engine, inspect


def upgrade_database(engine: Engine) -> None:
    """Executa upgrades incrementais no schema do banco.

    A funcao e segura para ser chamada multiplas vezes: ignora colunas
    que ja existem.
    """
    _upgrade_titulos(engine)


def _upgrade_titulos(engine: Engine) -> None:
    """Garante que a tabela titulos possua todas as colunas dos models."""
    inspector = inspect(engine)
    if not inspector.has_table("titulos"):
        return

    colunas_existentes = {
        col["name"]
        for col in inspector.get_columns("titulos")
    }

    colunas_desejadas: dict[str, str] = {
        "data_quitacao": "DATE",
        "valor_pago": "NUMERIC(15, 2)",
        "conta_bancaria_id": "INTEGER",
        "forma_pagamento": "VARCHAR(20) DEFAULT 'OUTRO'",
        "observacao_quitacao": "VARCHAR(500)",
    }

    with engine.begin() as conn:
        for nome, tipo in colunas_desejadas.items():
            if nome in colunas_existentes:
                continue
            sql = f"ALTER TABLE titulos ADD COLUMN {nome} {tipo}"
            conn.exec_driver_sql(sql)
