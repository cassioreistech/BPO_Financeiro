"""Testes de integracao do repository de Contador."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session, sessionmaker

from domain.entities.contador import Contador
from domain.value_objects.crc import CRC
from infrastructure.database.repositories.sqlite_contador_repository import (
    SQLiteContadorRepository,
)
from infrastructure.database.repositories.sqlite_escritorio_repository import (
    SQLiteEscritorioRepository,
)
from tests.integration.conftest import criar_contador, criar_escritorio


@pytest.fixture()
def repo(session_factory: sessionmaker[Session]) -> SQLiteContadorRepository:
    return SQLiteContadorRepository(session_factory)


class TestCreateContador:
    def test_criar_contador(
        self, repo: SQLiteContadorRepository, escritorio_repo: SQLiteEscritorioRepository
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        contador = Contador(
            escritorio_id=esc.id,
            nome="Joao Silva",
            crc=CRC("01-123456/O"),
        )
        resultado = repo.create(contador)
        assert resultado.id is not None
        assert resultado.nome == "Joao Silva"
        assert resultado.crc is not None
        assert resultado.crc.valor == "01-123456/O"


class TestGetByIdContador:
    def test_obter_por_id(
        self, repo: SQLiteContadorRepository, escritorio_repo: SQLiteEscritorioRepository
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        criado = criar_contador(repo, esc.id)
        assert criado.id is not None
        obtido = repo.get_by_id(criado.id)
        assert obtido is not None
        assert obtido.nome == "Contador Teste"

    def test_obter_inexistente(self, repo: SQLiteContadorRepository) -> None:
        assert repo.get_by_id(999) is None


class TestUpdateContador:
    def test_atualizar(
        self, repo: SQLiteContadorRepository, escritorio_repo: SQLiteEscritorioRepository
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        criado = criar_contador(repo, esc.id, nome="Original")
        criado.nome = "Atualizado"
        atualizado = repo.update(criado)
        assert atualizado.nome == "Atualizado"


class TestDeleteContador:
    def test_excluir(
        self, repo: SQLiteContadorRepository, escritorio_repo: SQLiteEscritorioRepository
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        criado = criar_contador(repo, esc.id)
        assert criado.id is not None
        repo.delete(criado.id)
        assert repo.get_by_id(criado.id) is None


class TestListContadores:
    def test_listar(
        self, repo: SQLiteContadorRepository, escritorio_repo: SQLiteEscritorioRepository
    ) -> None:
        esc = criar_escritorio(escritorio_repo)
        assert esc.id is not None
        criar_contador(repo, esc.id, nome="Joao")
        criar_contador(repo, esc.id, nome="Maria")
        resultado = repo.list_all()
        assert len(resultado) == 2

    def test_listar_por_escritorio(
        self, repo: SQLiteContadorRepository, escritorio_repo: SQLiteEscritorioRepository
    ) -> None:
        esc1 = criar_escritorio(escritorio_repo, nome="Esc 1", cnpj_cpf="11222333000181")
        esc2 = criar_escritorio(escritorio_repo, nome="Esc 2", cnpj_cpf="00000000000191")
        assert esc1.id is not None
        assert esc2.id is not None
        criar_contador(repo, esc1.id, nome="Joao")
        criar_contador(repo, esc2.id, nome="Maria")
        resultado = repo.list_all(escritorio_id=esc1.id)
        assert len(resultado) == 1
        assert resultado[0].nome == "Joao"
