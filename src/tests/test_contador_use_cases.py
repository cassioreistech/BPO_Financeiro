"""Testes dos use cases de Contador."""

from __future__ import annotations

import pytest

from application.dto.contador_dto import (
    CadastrarContadorDTO,
    EditarContadorDTO,
)
from application.ports.contador_repository import ContadorRepository
from application.use_cases.contador_use_cases import (
    CadastrarContadorUseCase,
    EditarContadorUseCase,
    ExcluirContadorUseCase,
    ListarContadoresUseCase,
    ObterContadorUseCase,
)
from domain.entities.contador import Contador


class FakeContadorRepository(ContadorRepository):
    """Repositorio fake para testes."""

    def __init__(self) -> None:
        self._contadores: dict[int, Contador] = {}
        self._proximo_id = 1

    def create(self, contador: Contador) -> Contador:
        contador.id = self._proximo_id
        self._contadores[self._proximo_id] = contador
        self._proximo_id += 1
        return contador

    def get_by_id(self, id: int) -> Contador | None:
        return self._contadores.get(id)

    def update(self, contador: Contador) -> Contador:
        if contador.id is None:
            raise ValueError("ID do contador nao pode ser None.")
        self._contadores[contador.id] = contador
        return contador

    def delete(self, id: int) -> None:
        self._contadores.pop(id, None)

    def list_all(
        self, escritorio_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[Contador]:
        items = list(self._contadores.values())
        if escritorio_id is not None:
            items = [c for c in items if c.escritorio_id == escritorio_id]
        return items[skip : skip + limit]


@pytest.fixture
def repo() -> FakeContadorRepository:
    return FakeContadorRepository()


@pytest.fixture
def cadastrar_uc(repo: FakeContadorRepository) -> CadastrarContadorUseCase:
    return CadastrarContadorUseCase(repo)


@pytest.fixture
def editar_uc(repo: FakeContadorRepository) -> EditarContadorUseCase:
    return EditarContadorUseCase(repo)


@pytest.fixture
def listar_uc(repo: FakeContadorRepository) -> ListarContadoresUseCase:
    return ListarContadoresUseCase(repo)


@pytest.fixture
def obter_uc(repo: FakeContadorRepository) -> ObterContadorUseCase:
    return ObterContadorUseCase(repo)


@pytest.fixture
def excluir_uc(repo: FakeContadorRepository) -> ExcluirContadorUseCase:
    return ExcluirContadorUseCase(repo)


class TestCadastrarContador:
    def test_cadastrar_contador_sucesso(
        self, cadastrar_uc: CadastrarContadorUseCase
    ) -> None:
        dto = CadastrarContadorDTO(
            escritorio_id=1, nome="Joao Silva", crc="01-123456/O"
        )
        resultado = cadastrar_uc.execute(dto)
        assert resultado.nome == "Joao Silva"
        assert resultado.crc == "01-123456/O"
        assert resultado.id > 0

    def test_cadastrar_contador_sem_crc(
        self, cadastrar_uc: CadastrarContadorUseCase
    ) -> None:
        dto = CadastrarContadorDTO(escritorio_id=1, nome="Maria Santos")
        resultado = cadastrar_uc.execute(dto)
        assert resultado.nome == "Maria Santos"
        assert resultado.crc is None

    def test_cadastrar_contador_nome_vazio(
        self, cadastrar_uc: CadastrarContadorUseCase
    ) -> None:
        dto = CadastrarContadorDTO(escritorio_id=1, nome="")
        with pytest.raises(ValueError, match="vazio"):
            cadastrar_uc.execute(dto)

    def test_cadastrar_contador_escritorio_invalido(
        self, cadastrar_uc: CadastrarContadorUseCase
    ) -> None:
        dto = CadastrarContadorDTO(escritorio_id=0, nome="Teste")
        with pytest.raises(ValueError, match="positivo"):
            cadastrar_uc.execute(dto)


class TestEditarContador:
    def test_editar_contador_sucesso(
        self,
        cadastrar_uc: CadastrarContadorUseCase,
        editar_uc: EditarContadorUseCase,
    ) -> None:
        dto = CadastrarContadorDTO(escritorio_id=1, nome="Joao")
        criado = cadastrar_uc.execute(dto)

        dto_editar = EditarContadorDTO(
            id=criado.id, escritorio_id=1, nome="Joao Silva", crc="01-123456/O"
        )
        editado = editar_uc.execute(dto_editar)
        assert editado.nome == "Joao Silva"
        assert editado.crc == "01-123456/O"

    def test_editar_contador_inexistente(
        self, editar_uc: EditarContadorUseCase
    ) -> None:
        dto = EditarContadorDTO(id=999, escritorio_id=1, nome="Teste")
        with pytest.raises(ValueError, match="nao encontrado"):
            editar_uc.execute(dto)


class TestListarContadores:
    def test_listar_vazio(self, listar_uc: ListarContadoresUseCase) -> None:
        resultado = listar_uc.execute()
        assert resultado == []

    def test_listar_com_dados(
        self, cadastrar_uc: CadastrarContadorUseCase, listar_uc: ListarContadoresUseCase
    ) -> None:
        cadastrar_uc.execute(CadastrarContadorDTO(escritorio_id=1, nome="Joao"))
        cadastrar_uc.execute(CadastrarContadorDTO(escritorio_id=1, nome="Maria"))
        resultado = listar_uc.execute()
        assert len(resultado) == 2


class TestObterContador:
    def test_obter_por_id(
        self, cadastrar_uc: CadastrarContadorUseCase, obter_uc: ObterContadorUseCase
    ) -> None:
        dto = CadastrarContadorDTO(escritorio_id=1, nome="Joao")
        criado = cadastrar_uc.execute(dto)
        obtido = obter_uc.execute(criado.id)
        assert obtido.nome == "Joao"

    def test_obter_inexistente(self, obter_uc: ObterContadorUseCase) -> None:
        with pytest.raises(ValueError, match="nao encontrado"):
            obter_uc.execute(999)


class TestExcluirContador:
    def test_excluir_sucesso(
        self,
        cadastrar_uc: CadastrarContadorUseCase,
        excluir_uc: ExcluirContadorUseCase,
        repo: FakeContadorRepository,
    ) -> None:
        dto = CadastrarContadorDTO(escritorio_id=1, nome="Joao")
        criado = cadastrar_uc.execute(dto)
        excluir_uc.execute(criado.id)
        assert repo.get_by_id(criado.id) is None

    def test_excluir_inexistente(self, excluir_uc: ExcluirContadorUseCase) -> None:
        with pytest.raises(ValueError, match="nao encontrado"):
            excluir_uc.execute(999)
