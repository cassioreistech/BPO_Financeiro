"""Testes ponta a ponta: use cases reais + repositories SQLite reais."""

from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from application.dto.empresa_dto import CadastrarEmpresaDTO, EditarEmpresaDTO
from application.dto.escritorio_dto import CriarEscritorioDTO
from application.use_cases.empresa_use_cases import (
    CadastrarEmpresaUseCase,
    DesativarEmpresaUseCase,
    EditarEmpresaUseCase,
)
from application.use_cases.escritorio_use_cases import CriarEscritorioUseCase
from infrastructure.database.repositories.sqlite_empresa_repository import (
    SQLiteEmpresaRepository,
)
from infrastructure.database.repositories.sqlite_escritorio_repository import (
    SQLiteEscritorioRepository,
)
from tests.integration.conftest import (
    CNPJ_VALIDO_1,
    CNPJ_VALIDO_2,
    criar_escritorio,
)


def test_criar_escritorio_ponta_a_ponta(
    session_factory: sessionmaker[Session],
) -> None:
    """CriarEscritorioUseCase persiste e permite recuperar via repository real."""
    repo = SQLiteEscritorioRepository(session_factory)
    use_case = CriarEscritorioUseCase(repo)

    dto = CriarEscritorioDTO(
        nome="Escritorio E2E",
        cnpj_cpf=CNPJ_VALIDO_1,
        email="e2e@escritorio.com.br",
        telefone="(11) 91234-5678",
    )
    resposta = use_case.execute(dto)

    assert resposta.id > 0
    assert resposta.nome == "Escritorio E2E"
    assert resposta.email == "e2e@escritorio.com.br"

    recuperado = repo.get_by_id(resposta.id)
    assert recuperado is not None
    assert recuperado.cnpj_cpf == CNPJ_VALIDO_1


def test_cadastrar_empresa_ponta_a_ponta(
    session_factory: sessionmaker[Session],
) -> None:
    """CadastrarEmpresaUseCase persiste empresa ligada ao escritorio real."""
    escritorio_repo = SQLiteEscritorioRepository(session_factory)
    empresa_repo = SQLiteEmpresaRepository(session_factory)
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None

    use_case = CadastrarEmpresaUseCase(empresa_repo)
    dto = CadastrarEmpresaDTO(
        escritorio_id=escritorio.id,
        cnpj=CNPJ_VALIDO_2,
        razao_social="Razao E2E",
        nome_fantasia="Fantasia E2E",
        regime_tributario="SIMPLES",
        email_financeiro="financeiro@e2e.com.br",
        telefone_financeiro="(11) 91234-5678",
    )
    resposta = use_case.execute(dto)

    assert resposta.id > 0
    assert resposta.escritorio_id == escritorio.id
    assert resposta.ativo is True

    recuperada = empresa_repo.get_by_id(resposta.id)
    assert recuperada is not None
    assert recuperada.escritorio_id == escritorio.id


def test_desativar_empresa_ponta_a_ponta(
    session_factory: sessionmaker[Session],
) -> None:
    """DesativarEmpresaUseCase marca a empresa como INATIVA no banco."""
    escritorio_repo = SQLiteEscritorioRepository(session_factory)
    empresa_repo = SQLiteEmpresaRepository(session_factory)
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None

    cadastrar = CadastrarEmpresaUseCase(empresa_repo)
    dto = CadastrarEmpresaDTO(
        escritorio_id=escritorio.id,
        cnpj=CNPJ_VALIDO_1,
        razao_social="Razao E2E",
        nome_fantasia="Fantasia E2E",
        regime_tributario="SIMPLES",
    )
    resposta = cadastrar.execute(dto)

    desativar = DesativarEmpresaUseCase(empresa_repo)
    desativada = desativar.execute(resposta.id)

    assert desativada.ativo is False

    recuperada = empresa_repo.get_by_id(resposta.id)
    assert recuperada is not None
    assert recuperada.ativo.value == "INATIVA"


def test_editar_empresa_ponta_a_ponta(
    session_factory: sessionmaker[Session],
) -> None:
    """EditarEmpresaUseCase persiste alteracoes sem perder o status."""
    escritorio_repo = SQLiteEscritorioRepository(session_factory)
    empresa_repo = SQLiteEmpresaRepository(session_factory)
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None

    cadastrar = CadastrarEmpresaUseCase(empresa_repo)
    criada = cadastrar.execute(
        CadastrarEmpresaDTO(
            escritorio_id=escritorio.id,
            cnpj=CNPJ_VALIDO_1,
            razao_social="Razao Inicial",
            nome_fantasia="Fantasia Inicial",
            regime_tributario="SIMPLES",
        )
    )

    editar = EditarEmpresaUseCase(empresa_repo)
    editada = editar.execute(
        EditarEmpresaDTO(
            id=criada.id,
            escritorio_id=escritorio.id,
            cnpj=CNPJ_VALIDO_2,
            razao_social="Razao Editada",
            nome_fantasia="Fantasia Editada",
            regime_tributario="LUCRO_REAL",
        )
    )

    assert editada.razao_social == "Razao Editada"
    assert editada.regime_tributario == "LUCRO_REAL"

    recuperada = empresa_repo.get_by_id(criada.id)
    assert recuperada is not None
    assert recuperada.cnpj.valor == CNPJ_VALIDO_2
