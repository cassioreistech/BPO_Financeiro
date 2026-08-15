"""Testes do mecanismo de upgrade incremental do schema SQLite."""

from __future__ import annotations

import pytest
from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from infrastructure.database import Base
from infrastructure.database.schema_upgrade import upgrade_database


@pytest.fixture
def engine() -> Engine:
    return create_engine("sqlite:///:memory:")


def _criar_titulos_sem_colunas_quitacao(engine: Engine) -> None:
    """Cria a tabela titulos sem as colunas de quitacao."""
    with engine.begin() as conn:
        conn.exec_driver_sql(
            """
            CREATE TABLE titulos (
                id INTEGER PRIMARY KEY,
                escritorio_id INTEGER NOT NULL,
                empresa_id INTEGER,
                plano_conta_id INTEGER NOT NULL,
                descricao VARCHAR(255) NOT NULL,
                tipo VARCHAR(10) NOT NULL,
                status VARCHAR(15) NOT NULL DEFAULT 'ABERTO',
                valor NUMERIC(15, 2) NOT NULL,
                data_emissao DATE NOT NULL,
                data_vencimento DATE NOT NULL,
                observacao VARCHAR(500),
                numero_documento VARCHAR(50),
                codigo_barras VARCHAR(100),
                categoria VARCHAR(20) NOT NULL DEFAULT 'OUTRO'
            )
            """
        )


class TestUpgradeDatabase:
    def test_adiciona_colunas_faltantes_de_quitacao(
        self, engine: Engine
    ) -> None:
        _criar_titulos_sem_colunas_quitacao(engine)

        upgrade_database(engine)

        colunas = {
            col["name"] for col in inspect(engine).get_columns("titulos")
        }
        assert "data_quitacao" in colunas
        assert "valor_pago" in colunas
        assert "conta_bancaria_id" in colunas
        assert "forma_pagamento" in colunas
        assert "observacao_quitacao" in colunas

    def test_upgrade_eh_idempotente(self, engine: Engine) -> None:
        _criar_titulos_sem_colunas_quitacao(engine)

        upgrade_database(engine)
        upgrade_database(engine)

        colunas = {
            col["name"] for col in inspect(engine).get_columns("titulos")
        }
        assert "observacao_quitacao" in colunas

    def test_nao_falha_se_tabela_nao_existe(self, engine: Engine) -> None:
        Base.metadata.create_all(engine)
        upgrade_database(engine)

        colunas = {
            col["name"] for col in inspect(engine).get_columns("titulos")
        }
        assert "observacao_quitacao" in colunas

    def test_preserva_dados_existentes(self, engine: Engine) -> None:
        _criar_titulos_sem_colunas_quitacao(engine)

        with engine.begin() as conn:
            conn.exec_driver_sql(
                """
                INSERT INTO titulos (
                    id, escritorio_id, empresa_id, plano_conta_id,
                    descricao, tipo, status, valor,
                    data_emissao, data_vencimento
                ) VALUES (
                    1, 1, 1, 1, 'Titulo existente', 'PAGAR',
                    'ABERTO', 100.00, '2026-08-01', '2026-08-20'
                )
                """
            )

        upgrade_database(engine)

        Session = sessionmaker(bind=engine)
        with Session() as session:
            resultado = session.execute(
                text("SELECT descricao FROM titulos WHERE id = 1")
            ).scalar()
            assert resultado == "Titulo existente"
