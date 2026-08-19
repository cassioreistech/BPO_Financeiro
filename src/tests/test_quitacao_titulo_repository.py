"""Testes de integracao de quitação no SQLiteTituloRepository."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.dto.conta_bancaria_dto import (
    CadastrarContaBancariaDTO,
    ContaBancariaResponseDTO,
)
from application.dto.titulo_dto import (
    CadastrarTituloDTO,
    QuitarTituloDTO,
    TituloResponseDTO,
)
from application.use_cases.conta_bancaria_use_cases import (
    CadastrarContaBancariaUseCase,
    DesativarContaBancariaUseCase,
    ListarContasBancariasUseCase,
)
from application.use_cases.dashboard_use_cases import ResumoFinanceiroUseCase
from application.use_cases.titulo_use_cases import (
    CadastrarTituloUseCase,
    QuitarTituloUseCase,
)
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_conta_bancaria import TipoContaBancaria
from domain.enums.tipo_titulo import TipoTitulo
from infrastructure.database import Base
from infrastructure.database.models.empresa_model import EmpresaModel
from infrastructure.database.models.escritorio_model import EscritorioModel
from infrastructure.database.models.plano_conta_model import PlanoContaModel
from infrastructure.database.repositories.sqlite_conta_bancaria_repository import (
    SQLiteContaBancariaRepository,
)
from infrastructure.database.repositories.sqlite_titulo_repository import (
    SQLiteTituloRepository,
)


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    with factory() as session:
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
        session.commit()

    return factory


@pytest.fixture
def titulo_repo(
    session_factory: sessionmaker[Session],
) -> SQLiteTituloRepository:
    return SQLiteTituloRepository(session_factory)


@pytest.fixture
def conta_repo(
    session_factory: sessionmaker[Session],
) -> SQLiteContaBancariaRepository:
    return SQLiteContaBancariaRepository(session_factory)


@pytest.fixture
def quitar_use_case(
    titulo_repo: SQLiteTituloRepository,
    conta_repo: SQLiteContaBancariaRepository,
) -> QuitarTituloUseCase:
    return QuitarTituloUseCase(titulo_repo, conta_repo)


@pytest.fixture
def criar_titulo_use_case(
    titulo_repo: SQLiteTituloRepository,
) -> CadastrarTituloUseCase:
    return CadastrarTituloUseCase(titulo_repo)


@pytest.fixture
def criar_conta_use_case(
    conta_repo: SQLiteContaBancariaRepository,
) -> CadastrarContaBancariaUseCase:
    return CadastrarContaBancariaUseCase(conta_repo)


@pytest.fixture
def desativar_conta_use_case(
    conta_repo: SQLiteContaBancariaRepository,
) -> DesativarContaBancariaUseCase:
    return DesativarContaBancariaUseCase(conta_repo)


@pytest.fixture
def listar_contas_use_case(
    conta_repo: SQLiteContaBancariaRepository,
) -> ListarContasBancariasUseCase:
    return ListarContasBancariasUseCase(conta_repo)


@pytest.fixture
def resumo_use_case(
    titulo_repo: SQLiteTituloRepository,
) -> ResumoFinanceiroUseCase:
    return ResumoFinanceiroUseCase(titulo_repo)


def _criar_titulo(
    use_case: CadastrarTituloUseCase,
    empresa_id: int = 1,
    valor: Decimal = Decimal("100.00"),
    vencimento: date | None = None,
) -> TituloResponseDTO:
    return use_case.execute(
        CadastrarTituloDTO(
            escritorio_id=1,
            empresa_id=empresa_id,
            plano_conta_id=1,
            descricao="Titulo para quitar",
            tipo=TipoTitulo.PAGAR.value,
            valor=valor,
            data_emissao=date(2026, 8, 1),
            data_vencimento=vencimento or date(2026, 8, 20),
        )
    )


def _criar_conta(
    use_case: CadastrarContaBancariaUseCase,
    empresa_id: int = 1,
) -> ContaBancariaResponseDTO:
    return use_case.execute(
        CadastrarContaBancariaDTO(
            empresa_id=empresa_id,
            banco_nome="Banco Teste",
            banco_codigo="001",
            agencia="0001",
            conta="12345-6",
            tipo=TipoContaBancaria.CORRENTE.value,
            descricao="Conta corrente",
        )
    )


class TestQuitacaoTituloRepository:
    def test_persistir_quitacao(
        self,
        quitar_use_case: QuitarTituloUseCase,
        criar_titulo_use_case: CadastrarTituloUseCase,
        criar_conta_use_case: CadastrarContaBancariaUseCase,
        titulo_repo: SQLiteTituloRepository,
    ) -> None:
        titulo = _criar_titulo(criar_titulo_use_case)
        conta = _criar_conta(criar_conta_use_case)
        hoje = date(2026, 8, 15)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=hoje,
            valor_pago=titulo.valor,
            conta_bancaria_id=conta.id,
            forma_pagamento="PIX",
            observacao_quitacao="Pagamento realizado",
        )

        quitar_use_case.execute(dto)
        atualizado = titulo_repo.get_by_id(titulo.id)

        assert atualizado is not None
        assert atualizado.status == StatusTitulo.PAGO
        assert atualizado.valor_pago == titulo.valor
        assert atualizado.data_quitacao == hoje
        assert atualizado.conta_bancaria_id == conta.id
        assert atualizado.forma_pagamento.value == "PIX"
        assert atualizado.observacao_quitacao == "Pagamento realizado"

    def test_titulo_quitado_nao_aparece_nos_alertas(
        self,
        quitar_use_case: QuitarTituloUseCase,
        criar_titulo_use_case: CadastrarTituloUseCase,
        criar_conta_use_case: CadastrarContaBancariaUseCase,
        titulo_repo: SQLiteTituloRepository,
    ) -> None:
        hoje = date(2026, 8, 15)
        titulo = _criar_titulo(
            criar_titulo_use_case, vencimento=hoje - timedelta(days=1)
        )
        conta = _criar_conta(criar_conta_use_case)
        assert titulo.id is not None
        assert conta.id is not None

        alertas_antes = titulo_repo.list_alertas(
            escritorio_id=1,
            empresa_id=None,
            data_referencia=hoje,
            incluir_vencidos=True,
        )
        assert any(a.titulo_id == titulo.id for a in alertas_antes)

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=hoje,
            valor_pago=titulo.valor,
            conta_bancaria_id=conta.id,
            forma_pagamento="BOLETO",
        )
        quitar_use_case.execute(dto)

        alertas_depois = titulo_repo.list_alertas(
            escritorio_id=1,
            empresa_id=None,
            data_referencia=hoje,
            incluir_vencidos=True,
        )
        assert not any(a.titulo_id == titulo.id for a in alertas_depois)

    def test_rejeita_conta_de_outra_empresa(
        self,
        quitar_use_case: QuitarTituloUseCase,
        criar_titulo_use_case: CadastrarTituloUseCase,
        criar_conta_use_case: CadastrarContaBancariaUseCase,
    ) -> None:
        titulo = _criar_titulo(criar_titulo_use_case, empresa_id=1)
        conta = _criar_conta(criar_conta_use_case, empresa_id=2)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=titulo.valor,
            conta_bancaria_id=conta.id,
        )

        with pytest.raises(ValueError, match="nao pertence a empresa do titulo"):
            quitar_use_case.execute(dto)

    def test_rejeita_conta_inativa(
        self,
        quitar_use_case: QuitarTituloUseCase,
        criar_titulo_use_case: CadastrarTituloUseCase,
        criar_conta_use_case: CadastrarContaBancariaUseCase,
        desativar_conta_use_case: DesativarContaBancariaUseCase,
    ) -> None:
        titulo = _criar_titulo(criar_titulo_use_case, empresa_id=1)
        conta = _criar_conta(criar_conta_use_case, empresa_id=1)
        assert titulo.id is not None
        assert conta.id is not None

        desativar_conta_use_case.execute(conta.id)

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=titulo.valor,
            conta_bancaria_id=conta.id,
        )

        with pytest.raises(ValueError, match="inativa"):
            quitar_use_case.execute(dto)

    def test_isolamento_por_empresa_na_quitacao(
        self,
        quitar_use_case: QuitarTituloUseCase,
        criar_titulo_use_case: CadastrarTituloUseCase,
        criar_conta_use_case: CadastrarContaBancariaUseCase,
    ) -> None:
        titulo_a = _criar_titulo(criar_titulo_use_case, empresa_id=1)
        conta_a = _criar_conta(criar_conta_use_case, empresa_id=1)
        assert titulo_a.id is not None
        assert conta_a.id is not None

        dto = QuitarTituloDTO(
            id=titulo_a.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=titulo_a.valor,
            conta_bancaria_id=conta_a.id,
            empresa_id=1,
        )

        resultado = quitar_use_case.execute(dto)
        assert resultado.empresa_id == 1

        dto_outra_empresa = QuitarTituloDTO(
            id=titulo_a.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=titulo_a.valor,
            conta_bancaria_id=conta_a.id,
            empresa_id=2,
        )

        with pytest.raises(ValueError, match="empresa ativa"):
            quitar_use_case.execute(dto_outra_empresa)

    def test_contas_bancarias_por_empresa(
        self,
        criar_conta_use_case: CadastrarContaBancariaUseCase,
        listar_contas_use_case: ListarContasBancariasUseCase,
    ) -> None:
        _criar_conta(criar_conta_use_case, empresa_id=1)
        _criar_conta(criar_conta_use_case, empresa_id=2)

        contas_a = listar_contas_use_case.execute(empresa_id=1)
        contas_b = listar_contas_use_case.execute(empresa_id=2)

        assert len(contas_a) == 1
        assert len(contas_b) == 1
        assert contas_a[0].empresa_id == 1
        assert contas_b[0].empresa_id == 2

    def test_quitacao_atualiza_resumo_do_dashboard(
        self,
        quitar_use_case: QuitarTituloUseCase,
        criar_titulo_use_case: CadastrarTituloUseCase,
        criar_conta_use_case: CadastrarContaBancariaUseCase,
        resumo_use_case: ResumoFinanceiroUseCase,
    ) -> None:
        titulo = _criar_titulo(criar_titulo_use_case, empresa_id=1)
        conta = _criar_conta(criar_conta_use_case, empresa_id=1)
        assert titulo.id is not None
        assert conta.id is not None

        resumo_antes = resumo_use_case.execute(
            escritorio_id=1, empresa_id=1
        )
        assert resumo_antes.a_pagar == titulo.valor
        assert resumo_antes.pago == Decimal("0")

        quitar_use_case.execute(
            QuitarTituloDTO(
                id=titulo.id,
                data_quitacao=date(2026, 8, 15),
                valor_pago=titulo.valor,
                conta_bancaria_id=conta.id,
            )
        )

        resumo_depois = resumo_use_case.execute(
            escritorio_id=1, empresa_id=1
        )
        assert resumo_depois.a_pagar == Decimal("0")
        assert resumo_depois.pago == titulo.valor
