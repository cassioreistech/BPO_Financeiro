"""Testes de integracao do repository de ContaBancaria."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session, sessionmaker

from domain.entities.conta_bancaria import ContaBancaria
from domain.enums.tipo_conta_bancaria import TipoContaBancaria
from domain.value_objects.banco_codigo import BancoCodigo
from infrastructure.database.repositories.sqlite_conta_bancaria_repository import (
    SQLiteContaBancariaRepository,
)
from infrastructure.database.repositories.sqlite_empresa_repository import (
    SQLiteEmpresaRepository,
)
from infrastructure.database.repositories.sqlite_escritorio_repository import (
    SQLiteEscritorioRepository,
)
from tests.integration.conftest import (
    criar_conta_bancaria,
    criar_empresa,
    criar_escritorio,
)


@pytest.fixture()
def repo(session_factory: sessionmaker[Session]) -> SQLiteContaBancariaRepository:
    return SQLiteContaBancariaRepository(session_factory)


class TestCreateContaBancaria:
    def test_criar_conta(
        self,
        repo: SQLiteContaBancariaRepository,
        escritorio_repo: SQLiteEscritorioRepository,
        empresa_repo: SQLiteEmpresaRepository,
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        emp = criar_empresa(empresa_repo, esc.id)
        assert emp.id is not None
        conta = ContaBancaria(
            empresa_id=emp.id,
            banco_nome="Banco do Brasil",
            banco_codigo=BancoCodigo("001"),
            agencia="1234",
            conta="56789-0",
            tipo=TipoContaBancaria.CORRENTE,
            descricao="Conta principal",
        )
        resultado = repo.create(conta)
        assert resultado.id is not None
        assert resultado.banco_nome == "Banco do Brasil"
        assert resultado.ativo is True


class TestGetByIdContaBancaria:
    def test_obter_por_id(
        self,
        repo: SQLiteContaBancariaRepository,
        escritorio_repo: SQLiteEscritorioRepository,
        empresa_repo: SQLiteEmpresaRepository,
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        emp = criar_empresa(empresa_repo, esc.id)
        assert emp.id is not None
        criado = criar_conta_bancaria(repo, emp.id)
        assert criado.id is not None
        obtido = repo.get_by_id(criado.id)
        assert obtido is not None
        assert obtido.banco_nome == "Banco do Brasil"

    def test_obter_inexistente(self, repo: SQLiteContaBancariaRepository) -> None:
        assert repo.get_by_id(999) is None


class TestUpdateContaBancaria:
    def test_atualizar(
        self,
        repo: SQLiteContaBancariaRepository,
        escritorio_repo: SQLiteEscritorioRepository,
        empresa_repo: SQLiteEmpresaRepository,
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        emp = criar_empresa(empresa_repo, esc.id)
        assert emp.id is not None
        criado = criar_conta_bancaria(repo, emp.id, descricao="Original")
        criado.descricao = "Atualizado"
        atualizado = repo.update(criado)
        assert atualizado.descricao == "Atualizado"


class TestDesativarContaBancaria:
    def test_desativar(
        self,
        repo: SQLiteContaBancariaRepository,
        escritorio_repo: SQLiteEscritorioRepository,
        empresa_repo: SQLiteEmpresaRepository,
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        emp = criar_empresa(empresa_repo, esc.id)
        assert emp.id is not None
        criado = criar_conta_bancaria(repo, emp.id)
        criado.ativo = False
        desativado = repo.update(criado)
        assert desativado.ativo is False


class TestListContasBancarias:
    def test_listar(
        self,
        repo: SQLiteContaBancariaRepository,
        escritorio_repo: SQLiteEscritorioRepository,
        empresa_repo: SQLiteEmpresaRepository,
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        emp = criar_empresa(empresa_repo, esc.id)
        assert emp.id is not None
        criar_conta_bancaria(repo, emp.id, banco_nome="BB")
        criar_conta_bancaria(repo, emp.id, banco_nome="Itau")
        resultado = repo.list_all()
        assert len(resultado) == 2

    def test_listar_por_empresa(
        self,
        repo: SQLiteContaBancariaRepository,
        escritorio_repo: SQLiteEscritorioRepository,
        empresa_repo: SQLiteEmpresaRepository,
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        emp1 = criar_empresa(empresa_repo, esc.id, cnpj="11222333000181")
        emp2 = criar_empresa(empresa_repo, esc.id, cnpj="00000000000191")
        assert emp1.id is not None
        assert emp2.id is not None
        criar_conta_bancaria(repo, emp1.id, banco_nome="BB")
        criar_conta_bancaria(repo, emp2.id, banco_nome="Itau")
        resultado = repo.list_all(empresa_id=emp1.id)
        assert len(resultado) == 1
        assert resultado[0].banco_nome == "BB"
