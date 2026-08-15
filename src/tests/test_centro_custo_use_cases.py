"""Testes dos use cases de CentroCusto."""

from __future__ import annotations

import pytest

from application.dto.centro_custo_dto import (
    CadastrarCentroCustoDTO,
    EditarCentroCustoDTO,
)
from application.ports.centro_custo_repository import CentroCustoRepository
from application.use_cases.centro_custo_use_cases import (
    CadastrarCentroCustoUseCase,
    DesativarCentroCustoUseCase,
    EditarCentroCustoUseCase,
    ListarCentroCustoUseCase,
    ObterCentroCustoUseCase,
)
from domain.entities.centro_custo import CentroCusto


class FakeCentroCustoRepository(CentroCustoRepository):
    """Repositorio fake para testes."""

    def __init__(self) -> None:
        self._centros: dict[int, CentroCusto] = {}
        self._proximo_id = 1

    def create(self, centro: CentroCusto) -> CentroCusto:
        centro.id = self._proximo_id
        self._centros[self._proximo_id] = centro
        self._proximo_id += 1
        return centro

    def get_by_id(self, id: int) -> CentroCusto | None:
        return self._centros.get(id)

    def get_by_codigo(self, empresa_id: int, codigo: str) -> CentroCusto | None:
        for centro in self._centros.values():
            if centro.empresa_id == empresa_id and centro.codigo == codigo:
                return centro
        return None

    def update(self, centro: CentroCusto) -> CentroCusto:
        if centro.id is None:
            raise ValueError("ID do centro de custo nao pode ser None.")
        self._centros[centro.id] = centro
        return centro

    def delete(self, id: int) -> None:
        self._centros.pop(id, None)

    def list_by_empresa(
        self,
        empresa_id: int,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CentroCusto]:
        items = [
            c for c in self._centros.values() if c.empresa_id == empresa_id
        ]
        if ativo is not None:
            items = [c for c in items if c.ativo == ativo]
        return items[skip : skip + limit]


@pytest.fixture
def repo() -> FakeCentroCustoRepository:
    return FakeCentroCustoRepository()


@pytest.fixture
def cadastrar_uc(repo: FakeCentroCustoRepository) -> CadastrarCentroCustoUseCase:
    return CadastrarCentroCustoUseCase(repo)


@pytest.fixture
def editar_uc(repo: FakeCentroCustoRepository) -> EditarCentroCustoUseCase:
    return EditarCentroCustoUseCase(repo)


@pytest.fixture
def listar_uc(repo: FakeCentroCustoRepository) -> ListarCentroCustoUseCase:
    return ListarCentroCustoUseCase(repo)


@pytest.fixture
def obter_uc(repo: FakeCentroCustoRepository) -> ObterCentroCustoUseCase:
    return ObterCentroCustoUseCase(repo)


@pytest.fixture
def desativar_uc(
    repo: FakeCentroCustoRepository,
) -> DesativarCentroCustoUseCase:
    return DesativarCentroCustoUseCase(repo)


class TestCadastrarCentroCusto:
    def test_cadastrar_sucesso(
        self, cadastrar_uc: CadastrarCentroCustoUseCase
    ) -> None:
        dto = CadastrarCentroCustoDTO(
            empresa_id=1, codigo="CC001", nome="Administrativo"
        )
        resultado = cadastrar_uc.execute(dto)
        assert resultado.codigo == "CC001"
        assert resultado.nome == "Administrativo"
        assert resultado.empresa_id == 1

    def test_cadastrar_codigo_vazio(
        self, cadastrar_uc: CadastrarCentroCustoUseCase
    ) -> None:
        dto = CadastrarCentroCustoDTO(empresa_id=1, codigo="", nome="Teste")
        with pytest.raises(ValueError, match="vazio"):
            cadastrar_uc.execute(dto)

    def test_cadastrar_codigo_duplicado(
        self, cadastrar_uc: CadastrarCentroCustoUseCase
    ) -> None:
        dto = CadastrarCentroCustoDTO(
            empresa_id=1, codigo="CC001", nome="Administrativo"
        )
        cadastrar_uc.execute(dto)
        dto2 = CadastrarCentroCustoDTO(
            empresa_id=1, codigo="CC001", nome="Outro"
        )
        with pytest.raises(ValueError, match="Ja existe"):
            cadastrar_uc.execute(dto2)


class TestListarCentroCusto:
    def test_listar_vazio(
        self, listar_uc: ListarCentroCustoUseCase
    ) -> None:
        resultado = listar_uc.execute(empresa_id=1)
        assert resultado == []

    def test_listar_filtra_por_empresa(
        self,
        cadastrar_uc: CadastrarCentroCustoUseCase,
        listar_uc: ListarCentroCustoUseCase,
    ) -> None:
        cadastrar_uc.execute(
            CadastrarCentroCustoDTO(
                empresa_id=1, codigo="A", nome="Centro A"
            )
        )
        cadastrar_uc.execute(
            CadastrarCentroCustoDTO(
                empresa_id=2, codigo="B", nome="Centro B"
            )
        )
        resultado = listar_uc.execute(empresa_id=1)
        assert len(resultado) == 1
        assert resultado[0].empresa_id == 1


class TestEditarCentroCusto:
    def test_editar_sucesso(
        self,
        cadastrar_uc: CadastrarCentroCustoUseCase,
        editar_uc: EditarCentroCustoUseCase,
    ) -> None:
        criado = cadastrar_uc.execute(
            CadastrarCentroCustoDTO(
                empresa_id=1, codigo="CC001", nome="Antigo"
            )
        )
        dto = EditarCentroCustoDTO(
            id=criado.id,
            empresa_id=1,
            codigo="CC001",
            nome="Novo",
        )
        editado = editar_uc.execute(dto)
        assert editado.nome == "Novo"


class TestDesativarCentroCusto:
    def test_desativar_sucesso(
        self,
        cadastrar_uc: CadastrarCentroCustoUseCase,
        desativar_uc: DesativarCentroCustoUseCase,
    ) -> None:
        criado = cadastrar_uc.execute(
            CadastrarCentroCustoDTO(
                empresa_id=1, codigo="CC001", nome="Ativo"
            )
        )
        desativado = desativar_uc.execute(criado.id)
        assert desativado.ativo is False
