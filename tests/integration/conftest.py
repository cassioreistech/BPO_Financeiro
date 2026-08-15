"""Fixtures compartilhadas para os testes de integracao (SQLite isolado)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from domain.entities.conta_bancaria import ContaBancaria
from domain.entities.contador import Contador
from domain.entities.empresa import Empresa
from domain.entities.escritorio import Escritorio
from domain.enums.regime_tributario import RegimeTributario
from domain.enums.status_empresa import StatusEmpresa
from domain.enums.tipo_conta_bancaria import TipoContaBancaria
from domain.value_objects.banco_codigo import BancoCodigo
from domain.value_objects.cnpj import CNPJ
from domain.value_objects.crc import CRC
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone
from infrastructure.database import Base
from infrastructure.database.models import (  # noqa: F401
    ContaBancariaModel,
    ContadorModel,
    EmpresaModel,
    EscritorioModel,
)
from infrastructure.database.repositories.sqlite_conta_bancaria_repository import (
    SQLiteContaBancariaRepository,
)
from infrastructure.database.repositories.sqlite_contador_repository import (
    SQLiteContadorRepository,
)
from infrastructure.database.repositories.sqlite_empresa_repository import (
    SQLiteEmpresaRepository,
)
from infrastructure.database.repositories.sqlite_escritorio_repository import (
    SQLiteEscritorioRepository,
)

CNPJ_VALIDO_1 = "11222333000181"
CNPJ_VALIDO_2 = "00000000000191"
CNPJ_VALIDO_3 = "17272607000123"
CNPJ_VALIDO_4 = "19688023000169"

EMAIL = "financeiro@teste.com.br"
TELEFONE = "(11) 91234-5678"


@pytest.fixture()
def engine() -> Iterator[Engine]:
    """Engine SQLite em memoria com o schema criado e isolado por teste."""
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Factory de sessoes ligada ao engine de teste."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def escritorio_repo(session_factory: sessionmaker[Session]) -> SQLiteEscritorioRepository:
    """Repository real de escritorio sobre o banco de teste."""
    return SQLiteEscritorioRepository(session_factory)


@pytest.fixture()
def empresa_repo(session_factory: sessionmaker[Session]) -> SQLiteEmpresaRepository:
    """Repository real de empresa sobre o banco de teste."""
    return SQLiteEmpresaRepository(session_factory)


@pytest.fixture()
def contador_repo(session_factory: sessionmaker[Session]) -> SQLiteContadorRepository:
    """Repository real de contador sobre o banco de teste."""
    return SQLiteContadorRepository(session_factory)


@pytest.fixture()
def conta_bancaria_repo(
    session_factory: sessionmaker[Session],
) -> SQLiteContaBancariaRepository:
    """Repository real de conta bancaria sobre o banco de teste."""
    return SQLiteContaBancariaRepository(session_factory)


def criar_escritorio(
    repo: SQLiteEscritorioRepository,
    nome: str = "Escritorio Teste",
    cnpj_cpf: str = CNPJ_VALIDO_1,
    email: Email | None = None,
    telefone: Telefone | None = None,
) -> Escritorio:
    """Cria um escritorio valido usando o repository real."""
    entidade = Escritorio(nome=nome, cnpj_cpf=cnpj_cpf, email=email, telefone=telefone)
    return repo.create(entidade)


def criar_empresa(
    repo: SQLiteEmpresaRepository,
    escritorio_id: int,
    cnpj: str = CNPJ_VALIDO_1,
    contador_id: int | None = None,
    ativo: bool = True,
) -> Empresa:
    """Cria uma empresa valida usando o repository real."""
    entidade = Empresa(
        escritorio_id=escritorio_id,
        contador_id=contador_id,
        cnpj=CNPJ(cnpj),
        razao_social="Razao Social Teste",
        nome_fantasia="Fantasia Teste",
        regime_tributario=RegimeTributario.SIMPLES,
        email_financeiro=Email(EMAIL),
        telefone_financeiro=Telefone(TELEFONE),
        ativo=StatusEmpresa.ATIVA if ativo else StatusEmpresa.INATIVA,
    )
    return repo.create(entidade)


def criar_contador(
    repo: SQLiteContadorRepository,
    escritorio_id: int,
    nome: str = "Contador Teste",
    crc: str | None = "01-123456/O",
) -> Contador:
    """Cria um contador valido usando o repository real."""
    entidade = Contador(
        escritorio_id=escritorio_id,
        nome=nome,
        crc=CRC(crc) if crc else None,
    )
    return repo.create(entidade)


def criar_conta_bancaria(
    repo: SQLiteContaBancariaRepository,
    empresa_id: int,
    banco_nome: str = "Banco do Brasil",
    banco_codigo: str = "001",
    agencia: str = "1234",
    conta: str = "56789-0",
    tipo: TipoContaBancaria = TipoContaBancaria.CORRENTE,
    descricao: str = "Conta teste",
) -> ContaBancaria:
    """Cria uma conta bancaria valida usando o repository real."""
    entidade = ContaBancaria(
        empresa_id=empresa_id,
        banco_nome=banco_nome,
        banco_codigo=BancoCodigo(banco_codigo),
        agencia=agencia,
        conta=conta,
        tipo=tipo,
        descricao=descricao,
    )
    return repo.create(entidade)
