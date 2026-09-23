"""Upgrade incremental do schema SQLite para compatibilidade com models atuais.

Este modulo e responsavel por adicionar colunas e ajustes necessarios em
bancos ja existentes, sem recriar tabelas ou perder dados.
"""

from __future__ import annotations

from sqlalchemy import Engine, inspect


def upgrade_database(engine: Engine) -> None:
    """Executa upgrades incrementais no schema do banco.

    A funcao e segura para ser chamada multiplas vezes: ignora colunas
    que ja existem e indices que ja foram criados.
    """
    _upgrade_titulos(engine)
    _criar_indices(engine)


def _indices() -> dict[str, str]:
    """Indices compostos para as consultas mais frequentes.

    Aplicaveis a bancos existentes: ``CREATE INDEX IF NOT EXISTS`` e
    idempotente e nao altera dados.
    """
    return {
        "ix_titulos_escritorio_status_vencimento": (
            "titulos (escritorio_id, status, data_vencimento)"
        ),
        "ix_centros_custo_empresa_ativo": (
            "centros_custo (empresa_id, ativo)"
        ),
        "ix_contas_bancarias_empresa_ativo": (
            "contas_bancarias (empresa_id, ativo)"
        ),
        "ix_plano_contas_escritorio_tipo": (
            "plano_contas (escritorio_id, tipo)"
        ),
    }


def _criar_indices(engine: Engine) -> None:
    """Cria os indices compostos caso ainda nao existam."""
    inspector = inspect(engine)
    with engine.begin() as conn:
        for nome, colunas in _indices().items():
            tabela = colunas.split("(")[0].strip()
            if not inspector.has_table(tabela):
                continue
            sql = (
                f"CREATE INDEX IF NOT EXISTS {nome} ON {colunas}"
            )
            conn.exec_driver_sql(sql)


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
        "emitente": "VARCHAR(255)",
    }

    with engine.begin() as conn:
        for nome, tipo in colunas_desejadas.items():
            if nome in colunas_existentes:
                continue
            sql = f"ALTER TABLE titulos ADD COLUMN {nome} {tipo}"
            conn.exec_driver_sql(sql)
