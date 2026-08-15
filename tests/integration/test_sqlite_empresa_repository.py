"""Testes de integracao do SQLiteEmpresaRepository."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from domain.entities.empresa import Empresa
from domain.enums.regime_tributario import RegimeTributario
from domain.enums.status_empresa import StatusEmpresa
from domain.value_objects.cnpj import CNPJ
from infrastructure.database.repositories.sqlite_empresa_repository import (
    SQLiteEmpresaRepository,
)
from infrastructure.database.repositories.sqlite_escritorio_repository import (
    SQLiteEscritorioRepository,
)
from tests.integration.conftest import (
    CNPJ_VALIDO_1,
    CNPJ_VALIDO_2,
    CNPJ_VALIDO_3,
    criar_empresa,
    criar_escritorio,
)


def test_criar_e_buscar_por_id(
    escritorio_repo: SQLiteEscritorioRepository,
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Cria uma empresa e a recupera pelo id."""
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None

    criada = criar_empresa(empresa_repo, escritorio_id=escritorio.id)

    assert criada.id is not None
    encontrada = empresa_repo.get_by_id(criada.id)
    assert encontrada is not None
    assert encontrada.id == criada.id
    assert encontrada.escritorio_id == escritorio.id
    assert encontrada.cnpj.valor == CNPJ_VALIDO_1
    assert encontrada.regime_tributario == RegimeTributario.SIMPLES
    assert encontrada.ativo == StatusEmpresa.ATIVA


def test_buscar_por_id_inexistente(
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Buscar por id inexistente retorna None."""
    assert empresa_repo.get_by_id(9999) is None


def test_buscar_por_cnpj(
    escritorio_repo: SQLiteEscritorioRepository,
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Busca empresa por CNPJ normalizado (somente digitos)."""
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None
    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_1)

    encontrada = empresa_repo.get_by_cnpj(CNPJ_VALIDO_1)
    assert encontrada is not None
    assert encontrada.cnpj.valor == CNPJ_VALIDO_1


def test_buscar_por_cnpj_inexistente(
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Buscar por CNPJ inexistente retorna None."""
    assert empresa_repo.get_by_cnpj("00000000000000") is None


def test_listar_empresas_por_escritorio(
    escritorio_repo: SQLiteEscritorioRepository,
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Filtra empresas pelo escritorio responsavel."""
    esc_1 = criar_escritorio(escritorio_repo, cnpj_cpf=CNPJ_VALIDO_1)
    esc_2 = criar_escritorio(escritorio_repo, cnpj_cpf=CNPJ_VALIDO_2)
    assert esc_1.id is not None
    assert esc_2.id is not None

    criar_empresa(empresa_repo, escritorio_id=esc_1.id, cnpj=CNPJ_VALIDO_1)
    criar_empresa(empresa_repo, escritorio_id=esc_1.id, cnpj=CNPJ_VALIDO_2)
    criar_empresa(empresa_repo, escritorio_id=esc_2.id, cnpj=CNPJ_VALIDO_3)

    do_esc_1 = empresa_repo.list_all(escritorio_id=esc_1.id)
    assert len(do_esc_1) == 2
    assert all(e.escritorio_id == esc_1.id for e in do_esc_1)


def test_listar_empresas_por_contador(
    escritorio_repo: SQLiteEscritorioRepository,
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Filtra empresas pelo contador responsavel."""
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None

    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_1, contador_id=10)
    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_2, contador_id=10)
    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_3)

    do_contador = empresa_repo.list_all(contador_id=10)
    assert len(do_contador) == 2
    assert all(e.contador_id == 10 for e in do_contador)


def test_listar_empresas_por_ativo(
    escritorio_repo: SQLiteEscritorioRepository,
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Filtra empresas pelo status ativo/inativo."""
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None

    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_1, ativo=True)
    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_2, ativo=True)
    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_3, ativo=False)

    ativas = empresa_repo.list_all(ativo=True)
    inativas = empresa_repo.list_all(ativo=False)

    assert len(ativas) == 2
    assert all(e.ativo == StatusEmpresa.ATIVA for e in ativas)
    assert len(inativas) == 1
    assert inativas[0].ativo == StatusEmpresa.INATIVA


def test_listar_empresas_com_paginacao(
    escritorio_repo: SQLiteEscritorioRepository,
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Lista respeita skip e limit."""
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None

    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_1)
    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_2)

    pagina = empresa_repo.list_all(skip=1, limit=1)
    assert len(pagina) == 1
    assert pagina[0].cnpj.valor == CNPJ_VALIDO_2


def test_atualizar_empresa(
    escritorio_repo: SQLiteEscritorioRepository,
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Atualiza os campos de uma empresa existente."""
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None

    criada = criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_1)
    assert criada.id is not None

    atualizada = Empresa(
        id=criada.id,
        escritorio_id=escritorio.id,
        contador_id=7,
        cnpj=CNPJ(CNPJ_VALIDO_2),
        razao_social="Razao Nova",
        nome_fantasia="Fantasia Nova",
        regime_tributario=RegimeTributario.LUCRO_REAL,
        email_financeiro=None,
        telefone_financeiro=None,
        ativo=StatusEmpresa.INATIVA,
    )
    salva = empresa_repo.update(atualizada)

    assert salva.razao_social == "Razao Nova"
    assert salva.regime_tributario == RegimeTributario.LUCRO_REAL
    assert salva.ativo == StatusEmpresa.INATIVA
    assert salva.email_financeiro is None

    encontrada = empresa_repo.get_by_id(criada.id)
    assert encontrada is not None
    assert encontrada.cnpj.valor == CNPJ_VALIDO_2
    assert encontrada.contador_id == 7


def test_atualizar_empresa_inexistente_raise(
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Atualizar empresa inexistente levanta ValueError."""
    alvo = Empresa(
        id=9999,
        escritorio_id=1,
        cnpj=CNPJ(CNPJ_VALIDO_1),
        razao_social="X",
        nome_fantasia="Y",
        regime_tributario=RegimeTributario.SIMPLES,
    )
    with pytest.raises(ValueError, match="nao encontrada"):
        empresa_repo.update(alvo)


def test_deletar_empresa(
    escritorio_repo: SQLiteEscritorioRepository,
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Remove uma empresa persistida."""
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None

    criada = criar_empresa(empresa_repo, escritorio_id=escritorio.id)
    assert criada.id is not None

    empresa_repo.delete(criada.id)

    assert empresa_repo.get_by_id(criada.id) is None
    assert empresa_repo.list_all() == []


def test_deletar_empresa_inexistente_nao_levanta(
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """Deletar id inexistente e um no-op sem erro."""
    empresa_repo.delete(9999)


def test_cnpj_duplicado_levanta_integrity_error(
    escritorio_repo: SQLiteEscritorioRepository,
    empresa_repo: SQLiteEmpresaRepository,
) -> None:
    """CNPJ unico: duplicar gera IntegrityError no banco."""
    escritorio = criar_escritorio(escritorio_repo)
    assert escritorio.id is not None
    criar_empresa(empresa_repo, escritorio_id=escritorio.id, cnpj=CNPJ_VALIDO_1)

    duplicada = Empresa(
        escritorio_id=escritorio.id,
        cnpj=CNPJ(CNPJ_VALIDO_1),
        razao_social="Outra",
        nome_fantasia="Outra",
        regime_tributario=RegimeTributario.SIMPLES,
    )
    with pytest.raises(IntegrityError):
        empresa_repo.create(duplicada)
