"""Testes de integracao dos filtros avancados no SQLiteTituloRepository."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.dto.titulo_dto import FiltroTitulosDTO
from domain.enums.situacao_vencimento import SituacaoVencimento
from domain.enums.status_titulo import StatusTitulo
from infrastructure.database import Base
from infrastructure.database.models.empresa_model import EmpresaModel
from infrastructure.database.models.escritorio_model import EscritorioModel
from infrastructure.database.models.plano_conta_model import PlanoContaModel
from infrastructure.database.models.titulo_model import TituloModel
from infrastructure.database.repositories.sqlite_titulo_repository import (
    SQLiteTituloRepository,
)


@pytest.fixture
def repo() -> SQLiteTituloRepository:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    with session_factory() as session:
        escritorio = EscritorioModel(
            id=1,
            nome="Escritorio Teste",
            cnpj_cpf="00000000000191",
            email="teste@teste.com",
            telefone="11999999999",
        )
        empresa_a = EmpresaModel(
            id=1,
            escritorio_id=1,
            cnpj="11111111000109",
            razao_social="Empresa A LTDA",
            nome_fantasia="Empresa A",
            regime_tributario="SIMPLES",
            ativo=True,
        )
        empresa_b = EmpresaModel(
            id=2,
            escritorio_id=1,
            cnpj="22222222000109",
            razao_social="Empresa B LTDA",
            nome_fantasia="Empresa B",
            regime_tributario="LUCRO_REAL",
            ativo=True,
        )
        plano = PlanoContaModel(
            id=1,
            escritorio_id=1,
            codigo="1",
            nome="Despesas",
            tipo="DESPESA",
        )
        session.add_all([escritorio, empresa_a, empresa_b, plano])

        hoje = date(2026, 8, 15)
        titulos = [
            TituloModel(
                id=1,
                escritorio_id=1,
                empresa_id=1,
                plano_conta_id=1,
                descricao="Aluguel agosto",
                tipo="PAGAR",
                status=StatusTitulo.ABERTO.value,
                valor=Decimal("1500.00"),
                data_emissao=hoje - timedelta(days=10),
                data_vencimento=hoje - timedelta(days=5),
                categoria="OUTRO",
                numero_documento="NF-001",
                forma_pagamento="OUTRO",
            ),
            TituloModel(
                id=2,
                escritorio_id=1,
                empresa_id=1,
                plano_conta_id=1,
                descricao="Servico de consultoria",
                tipo="RECEBER",
                status=StatusTitulo.ABERTO.value,
                valor=Decimal("3000.00"),
                data_emissao=hoje - timedelta(days=10),
                data_vencimento=hoje,
                categoria="SERVICO",
                numero_documento="NF-002",
                forma_pagamento="OUTRO",
            ),
            TituloModel(
                id=3,
                escritorio_id=1,
                empresa_id=1,
                plano_conta_id=1,
                descricao="Material de escritorio",
                tipo="PAGAR",
                status=StatusTitulo.PAGO.value,
                valor=Decimal("250.00"),
                data_emissao=hoje - timedelta(days=10),
                data_vencimento=hoje + timedelta(days=3),
                categoria="OUTRO",
                numero_documento=None,
                forma_pagamento="PIX",
                data_quitacao=hoje,
                valor_pago=Decimal("250.00"),
            ),
            TituloModel(
                id=4,
                escritorio_id=1,
                empresa_id=2,
                plano_conta_id=1,
                descricao="Recebimento cliente B",
                tipo="RECEBER",
                status=StatusTitulo.ABERTO.value,
                valor=Decimal("1200.00"),
                data_emissao=hoje - timedelta(days=10),
                data_vencimento=hoje - timedelta(days=1),
                categoria="VENDA",
                numero_documento=None,
                forma_pagamento="OUTRO",
            ),
        ]
        session.add_all(titulos)
        session.commit()

    return SQLiteTituloRepository(session_factory)


class TestSQLiteTituloRepositoryFiltros:
    def test_filtro_por_texto_descricao(self, repo: SQLiteTituloRepository) -> None:
        filtro = FiltroTitulosDTO(empresa_id=1, texto="aluguel")
        resultado = repo.list_filtered(escritorio_id=1, filtro=filtro)
        assert len(resultado) == 1
        assert resultado[0].descricao == "Aluguel agosto"

    def test_filtro_por_numero_documento(self, repo: SQLiteTituloRepository) -> None:
        filtro = FiltroTitulosDTO(empresa_id=1, texto="NF-002")
        resultado = repo.list_filtered(escritorio_id=1, filtro=filtro)
        assert len(resultado) == 1
        assert resultado[0].id == 2

    def test_filtro_por_status_quitado(self, repo: SQLiteTituloRepository) -> None:
        filtro = FiltroTitulosDTO(empresa_id=1, status="PAGO")
        resultado = repo.list_filtered(escritorio_id=1, filtro=filtro)
        assert len(resultado) == 1
        assert resultado[0].status == StatusTitulo.PAGO

    def test_filtro_por_tipo_e_categoria(self, repo: SQLiteTituloRepository) -> None:
        filtro = FiltroTitulosDTO(
            empresa_id=1, tipo="PAGAR", categoria="OUTRO"
        )
        resultado = repo.list_filtered(escritorio_id=1, filtro=filtro)
        assert len(resultado) == 2

    def test_isolamento_por_empresa(self, repo: SQLiteTituloRepository) -> None:
        filtro = FiltroTitulosDTO(empresa_id=1)
        resultado = repo.list_filtered(escritorio_id=1, filtro=filtro)
        assert len(resultado) == 3
        assert all(t.empresa_id == 1 for t in resultado)

    def test_filtro_por_intervalo_vencimento(
        self, repo: SQLiteTituloRepository
    ) -> None:
        hoje = date(2026, 8, 15)
        filtro = FiltroTitulosDTO(
            empresa_id=1,
            data_vencimento_inicio=hoje - timedelta(days=2),
            data_vencimento_fim=hoje + timedelta(days=2),
        )
        resultado = repo.list_filtered(escritorio_id=1, filtro=filtro)
        assert len(resultado) == 2
        assert {t.id for t in resultado} == {1, 2}

    def test_filtro_situacao_vencidos(self, repo: SQLiteTituloRepository) -> None:
        filtro = FiltroTitulosDTO(
            empresa_id=1,
            situacao_vencimento=SituacaoVencimento.VENCIDOS.value,
        )
        resultado = repo.list_filtered(escritorio_id=1, filtro=filtro)
        assert len(resultado) == 1
        assert resultado[0].id == 1

    def test_combinacao_texto_periodo_status(
        self, repo: SQLiteTituloRepository
    ) -> None:
        hoje = date(2026, 8, 15)
        filtro = FiltroTitulosDTO(
            empresa_id=1,
            texto="NF",
            status="ABERTO",
            data_vencimento_inicio=hoje - timedelta(days=10),
            data_vencimento_fim=hoje,
        )
        resultado = repo.list_filtered(escritorio_id=1, filtro=filtro)
        assert len(resultado) == 2
        assert {t.id for t in resultado} == {1, 2}

    def test_ordenacao_padrao(self, repo: SQLiteTituloRepository) -> None:
        filtro = FiltroTitulosDTO(empresa_id=1)
        resultado = repo.list_filtered(escritorio_id=1, filtro=filtro)
        datas = [t.data_vencimento for t in resultado]
        assert datas == sorted(datas)
