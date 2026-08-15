"""Testes de integracao do SQLiteEscritorioRepository."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from domain.entities.escritorio import Escritorio
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone
from infrastructure.database.repositories.sqlite_escritorio_repository import (
    SQLiteEscritorioRepository,
)
from tests.integration.conftest import (
    CNPJ_VALIDO_1,
    CNPJ_VALIDO_2,
    criar_escritorio,
)


def test_criar_e_buscar_por_id(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Cria um escritorio e o recupera pelo id."""
    criado = criar_escritorio(escritorio_repo)

    assert criado.id is not None
    encontrado = escritorio_repo.get_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.id == criado.id
    assert encontrado.nome == "Escritorio Teste"
    assert encontrado.cnpj_cpf == CNPJ_VALIDO_1


def test_buscar_por_id_inexistente(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Buscar por id inexistente retorna None."""
    assert escritorio_repo.get_by_id(9999) is None


def test_buscar_por_cnpj_cpf(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Busca escritorio por CNPJ/CPF normalizado (somente digitos)."""
    criar_escritorio(escritorio_repo, cnpj_cpf=CNPJ_VALIDO_1)

    encontrado = escritorio_repo.get_by_cnpj(CNPJ_VALIDO_1)
    assert encontrado is not None
    assert encontrado.cnpj_cpf == CNPJ_VALIDO_1


def test_buscar_por_cnpj_cpf_inexistente(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Buscar por CNPJ/CPF inexistente retorna None."""
    assert escritorio_repo.get_by_cnpj("00000000000000") is None


def test_listar_escritorios(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Lista todos os escritorios criados."""
    criar_escritorio(escritorio_repo, cnpj_cpf=CNPJ_VALIDO_1)
    criar_escritorio(escritorio_repo, cnpj_cpf=CNPJ_VALIDO_2)

    escritorios = escritorio_repo.list_all()
    assert len(escritorios) == 2


def test_listar_escritorios_com_paginacao(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Lista respeita skip e limit."""
    criar_escritorio(escritorio_repo, cnpj_cpf=CNPJ_VALIDO_1)
    criar_escritorio(escritorio_repo, cnpj_cpf=CNPJ_VALIDO_2)

    pagina = escritorio_repo.list_all(skip=1, limit=1)
    assert len(pagina) == 1
    assert pagina[0].cnpj_cpf == CNPJ_VALIDO_2


def test_atualizar_escritorio(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Atualiza os campos de um escritorio existente."""
    criado = criar_escritorio(
        escritorio_repo,
        email=Email("antigo@teste.com.br"),
        telefone=Telefone("(11) 91234-5678"),
    )
    assert criado.id is not None

    atualizado = Escritorio(
        id=criado.id,
        nome="Novo Nome",
        cnpj_cpf=CNPJ_VALIDO_2,
        email=Email("novo@teste.com.br"),
        telefone=None,
    )
    salvo = escritorio_repo.update(atualizado)

    assert salvo.nome == "Novo Nome"
    assert salvo.cnpj_cpf == CNPJ_VALIDO_2
    assert salvo.email is not None and salvo.email.valor == "novo@teste.com.br"
    assert salvo.telefone is None

    encontrado = escritorio_repo.get_by_id(criado.id)
    assert encontrado is not None
    assert encontrado.nome == "Novo Nome"
    assert encontrado.cnpj_cpf == CNPJ_VALIDO_2


def test_atualizar_escritorio_inexistente_raise(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Atualizar escritorio inexistente levanta ValueError."""
    alvo = Escritorio(id=9999, nome="X", cnpj_cpf=CNPJ_VALIDO_1)
    with pytest.raises(ValueError, match="nao encontrado"):
        escritorio_repo.update(alvo)


def test_atualizar_escritorio_sem_id_raise(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Atualizar escritorio sem id levanta ValueError."""
    alvo = Escritorio(nome="X", cnpj_cpf=CNPJ_VALIDO_1)
    with pytest.raises(ValueError, match="nao pode ser None"):
        escritorio_repo.update(alvo)


def test_deletar_escritorio(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Remove um escritorio persistido."""
    criado = criar_escritorio(escritorio_repo)
    assert criado.id is not None

    escritorio_repo.delete(criado.id)

    assert escritorio_repo.get_by_id(criado.id) is None
    assert escritorio_repo.list_all() == []


def test_deletar_escritorio_inexistente_nao_levanta(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """Deletar id inexistente e um no-op sem erro."""
    escritorio_repo.delete(9999)


def test_cnpj_cpf_duplicado_levanta_integrity_error(
    escritorio_repo: SQLiteEscritorioRepository,
) -> None:
    """CNPJ/CPF unico: duplicar gera IntegrityError no banco."""
    criar_escritorio(escritorio_repo, cnpj_cpf=CNPJ_VALIDO_1)

    duplicado = Escritorio(nome="Outro", cnpj_cpf=CNPJ_VALIDO_1)
    with pytest.raises(IntegrityError):
        escritorio_repo.create(duplicado)
