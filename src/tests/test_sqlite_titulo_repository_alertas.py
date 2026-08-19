"""Testes do metodo list_alertas do SQLiteTituloRepository."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
                descricao="Vencido A",
                tipo="PAGAR",
                status=StatusTitulo.ABERTO.value,
                valor=Decimal("100.00"),
                data_emissao=hoje - timedelta(days=5),
                data_vencimento=hoje - timedelta(days=1),
                categoria="OUTRO",
                forma_pagamento="OUTRO",
            ),
            TituloModel(
                id=2,
                escritorio_id=1,
                empresa_id=1,
                plano_conta_id=1,
                descricao="Hoje A",
                tipo="PAGAR",
                status=StatusTitulo.ABERTO.value,
                valor=Decimal("200.00"),
                data_emissao=hoje - timedelta(days=5),
                data_vencimento=hoje,
                categoria="OUTRO",
                forma_pagamento="OUTRO",
            ),
            TituloModel(
                id=3,
                escritorio_id=1,
                empresa_id=2,
                plano_conta_id=1,
                descricao="Amanha B",
                tipo="RECEBER",
                status=StatusTitulo.ABERTO.value,
                valor=Decimal("300.00"),
                data_emissao=hoje - timedelta(days=5),
                data_vencimento=hoje + timedelta(days=1),
                numero_documento="DOC-123",
                categoria="OUTRO",
                forma_pagamento="OUTRO",
            ),
            TituloModel(
                id=4,
                escritorio_id=1,
                empresa_id=2,
                plano_conta_id=1,
                descricao="Semana B",
                tipo="RECEBER",
                status=StatusTitulo.ABERTO.value,
                valor=Decimal("400.00"),
                data_emissao=hoje - timedelta(days=5),
                data_vencimento=hoje + timedelta(days=5),
                categoria="OUTRO",
                forma_pagamento="OUTRO",
            ),
            TituloModel(
                id=5,
                escritorio_id=1,
                empresa_id=1,
                plano_conta_id=1,
                descricao="Quitado A",
                tipo="PAGAR",
                status=StatusTitulo.PAGO.value,
                valor=Decimal("500.00"),
                data_emissao=hoje - timedelta(days=5),
                data_vencimento=hoje,
                data_quitacao=hoje,
                valor_pago=Decimal("500.00"),
                categoria="OUTRO",
                forma_pagamento="OUTRO",
            ),
            TituloModel(
                id=6,
                escritorio_id=1,
                empresa_id=1,
                plano_conta_id=1,
                descricao="Fora da janela",
                tipo="PAGAR",
                status=StatusTitulo.ABERTO.value,
                valor=Decimal("600.00"),
                data_emissao=hoje - timedelta(days=5),
                data_vencimento=hoje + timedelta(days=10),
                categoria="OUTRO",
                forma_pagamento="OUTRO",
            ),
        ]
        session.add_all(titulos)
        session.commit()

    return SQLiteTituloRepository(session_factory)


class TestSQLiteTituloRepositoryAlertas:
    def test_list_alertas_consolidado(self, repo: SQLiteTituloRepository) -> None:
        hoje = date(2026, 8, 15)
        alertas = repo.list_alertas(
            escritorio_id=1,
            empresa_id=None,
            data_referencia=hoje,
            incluir_vencidos=True,
        )

        assert len(alertas) == 4
        assert sum(a.valor for a in alertas) == Decimal("1000.00")

    def test_list_alertas_filtra_por_empresa(
        self, repo: SQLiteTituloRepository
    ) -> None:
        hoje = date(2026, 8, 15)
        alertas = repo.list_alertas(
            escritorio_id=1,
            empresa_id=2,
            data_referencia=hoje,
            incluir_vencidos=True,
        )

        assert len(alertas) == 2
        assert all(a.empresa_id == 2 for a in alertas)
        assert alertas[0].numero_documento == "DOC-123"

    def test_list_alertas_exclui_pagos_e_fora_da_janela(
        self, repo: SQLiteTituloRepository
    ) -> None:
        hoje = date(2026, 8, 15)
        alertas = repo.list_alertas(
            escritorio_id=1,
            empresa_id=None,
            data_referencia=hoje,
            incluir_vencidos=True,
        )

        descricoes = {a.descricao for a in alertas}
        assert "Quitado A" not in descricoes
        assert "Fora da janela" not in descricoes

    def test_list_alertas_ordenacao(
        self, repo: SQLiteTituloRepository
    ) -> None:
        hoje = date(2026, 8, 15)
        alertas = repo.list_alertas(
            escritorio_id=1,
            empresa_id=None,
            data_referencia=hoje,
            incluir_vencidos=True,
        )

        datas = [a.data_vencimento for a in alertas]
        assert datas == sorted(datas)

    def test_list_alertas_nome_da_empresa(
        self, repo: SQLiteTituloRepository
    ) -> None:
        hoje = date(2026, 8, 15)
        alertas = repo.list_alertas(
            escritorio_id=1,
            empresa_id=None,
            data_referencia=hoje,
            incluir_vencidos=True,
        )

        empresa_a = next(a for a in alertas if a.empresa_id == 1)
        empresa_b = next(a for a in alertas if a.empresa_id == 2)
        assert empresa_a.empresa_nome == "Empresa A"
        assert empresa_b.empresa_nome == "Empresa B"

    def test_list_alertas_exclui_vencidos_quando_configurado(
        self, repo: SQLiteTituloRepository
    ) -> None:
        hoje = date(2026, 8, 15)
        alertas = repo.list_alertas(
            escritorio_id=1,
            empresa_id=None,
            data_referencia=hoje,
            incluir_vencidos=False,
        )

        descricoes = {a.descricao for a in alertas}
        assert "Vencido A" not in descricoes
        assert "Hoje A" in descricoes
