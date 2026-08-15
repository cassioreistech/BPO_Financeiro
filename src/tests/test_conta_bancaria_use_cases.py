"""Testes dos use cases de ContaBancaria."""

from __future__ import annotations

import pytest

from application.dto.conta_bancaria_dto import (
    CadastrarContaBancariaDTO,
    EditarContaBancariaDTO,
)
from application.ports.conta_bancaria_repository import ContaBancariaRepository
from application.use_cases.conta_bancaria_use_cases import (
    CadastrarContaBancariaUseCase,
    DesativarContaBancariaUseCase,
    EditarContaBancariaUseCase,
    ListarContasBancariasUseCase,
    ObterContaBancariaUseCase,
)
from domain.entities.conta_bancaria import ContaBancaria


class FakeContaBancariaRepository(ContaBancariaRepository):
    """Repositorio fake para testes."""

    def __init__(self) -> None:
        self._contas: dict[int, ContaBancaria] = {}
        self._proximo_id = 1

    def create(self, conta: ContaBancaria) -> ContaBancaria:
        conta.id = self._proximo_id
        self._contas[self._proximo_id] = conta
        self._proximo_id += 1
        return conta

    def get_by_id(self, id: int) -> ContaBancaria | None:
        return self._contas.get(id)

    def update(self, conta: ContaBancaria) -> ContaBancaria:
        if conta.id is None:
            raise ValueError("ID da conta nao pode ser None.")
        self._contas[conta.id] = conta
        return conta

    def delete(self, id: int) -> None:
        self._contas.pop(id, None)

    def list_all(
        self, empresa_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[ContaBancaria]:
        items = list(self._contas.values())
        if empresa_id is not None:
            items = [c for c in items if c.empresa_id == empresa_id]
        return items[skip : skip + limit]


@pytest.fixture
def repo() -> FakeContaBancariaRepository:
    return FakeContaBancariaRepository()


@pytest.fixture
def cadastrar_uc(repo: FakeContaBancariaRepository) -> CadastrarContaBancariaUseCase:
    return CadastrarContaBancariaUseCase(repo)


@pytest.fixture
def editar_uc(repo: FakeContaBancariaRepository) -> EditarContaBancariaUseCase:
    return EditarContaBancariaUseCase(repo)


@pytest.fixture
def listar_uc(repo: FakeContaBancariaRepository) -> ListarContasBancariasUseCase:
    return ListarContasBancariasUseCase(repo)


@pytest.fixture
def obter_uc(repo: FakeContaBancariaRepository) -> ObterContaBancariaUseCase:
    return ObterContaBancariaUseCase(repo)


@pytest.fixture
def desativar_uc(repo: FakeContaBancariaRepository) -> DesativarContaBancariaUseCase:
    return DesativarContaBancariaUseCase(repo)


class TestCadastrarContaBancaria:
    def test_cadastrar_sucesso(
        self, cadastrar_uc: CadastrarContaBancariaUseCase
    ) -> None:
        dto = CadastrarContaBancariaDTO(
            empresa_id=1,
            banco_nome="Banco do Brasil",
            banco_codigo="001",
            agencia="1234",
            conta="56789-0",
            tipo="CORRENTE",
            descricao="Conta principal",
        )
        resultado = cadastrar_uc.execute(dto)
        assert resultado.banco_nome == "Banco do Brasil"
        assert resultado.banco_codigo == "001"
        assert resultado.ativo is True

    def test_cadastrar_banco_vazio(
        self, cadastrar_uc: CadastrarContaBancariaUseCase
    ) -> None:
        dto = CadastrarContaBancariaDTO(
            empresa_id=1,
            banco_nome="",
            banco_codigo="001",
            agencia="1234",
            conta="56789",
            tipo="CORRENTE",
            descricao="Conta",
        )
        with pytest.raises(ValueError, match="vazio"):
            cadastrar_uc.execute(dto)

    def test_cadastrar_tipo_invalido(
        self, cadastrar_uc: CadastrarContaBancariaUseCase
    ) -> None:
        dto = CadastrarContaBancariaDTO(
            empresa_id=1,
            banco_nome="BB",
            banco_codigo="001",
            agencia="1234",
            conta="56789",
            tipo="INVALIDO",
            descricao="Conta",
        )
        with pytest.raises(ValueError, match="invalido"):
            cadastrar_uc.execute(dto)


class TestEditarContaBancaria:
    def test_editar_sucesso(
        self,
        cadastrar_uc: CadastrarContaBancariaUseCase,
        editar_uc: EditarContaBancariaUseCase,
    ) -> None:
        dto = CadastrarContaBancariaDTO(
            empresa_id=1,
            banco_nome="BB",
            banco_codigo="001",
            agencia="1234",
            conta="56789",
            tipo="CORRENTE",
            descricao="Antiga",
        )
        criado = cadastrar_uc.execute(dto)

        dto_editar = EditarContaBancariaDTO(
            id=criado.id,
            empresa_id=1,
            banco_nome="Banco do Brasil",
            banco_codigo="001",
            agencia="1234",
            conta="56789-0",
            tipo="CORRENTE",
            descricao="Conta principal",
        )
        editado = editar_uc.execute(dto_editar)
        assert editado.descricao == "Conta principal"

    def test_editar_inexistente(self, editar_uc: EditarContaBancariaUseCase) -> None:
        dto = EditarContaBancariaDTO(
            id=999,
            empresa_id=1,
            banco_nome="BB",
            banco_codigo="001",
            agencia="1234",
            conta="56789",
            tipo="CORRENTE",
            descricao="Conta",
        )
        with pytest.raises(ValueError, match="nao encontrada"):
            editar_uc.execute(dto)


class TestDesativarContaBancaria:
    def test_desativar_sucesso(
        self,
        cadastrar_uc: CadastrarContaBancariaUseCase,
        desativar_uc: DesativarContaBancariaUseCase,
    ) -> None:
        dto = CadastrarContaBancariaDTO(
            empresa_id=1,
            banco_nome="BB",
            banco_codigo="001",
            agencia="1234",
            conta="56789",
            tipo="CORRENTE",
            descricao="Conta",
        )
        criado = cadastrar_uc.execute(dto)
        desativado = desativar_uc.execute(criado.id)
        assert desativado.ativo is False

    def test_desativar_inexistente(
        self, desativar_uc: DesativarContaBancariaUseCase
    ) -> None:
        with pytest.raises(ValueError, match="nao encontrada"):
            desativar_uc.execute(999)


class TestListarContasBancarias:
    def test_listar_vazio(self, listar_uc: ListarContasBancariasUseCase) -> None:
        resultado = listar_uc.execute()
        assert resultado == []

    def test_listar_com_dados(
        self,
        cadastrar_uc: CadastrarContaBancariaUseCase,
        listar_uc: ListarContasBancariasUseCase,
    ) -> None:
        cadastrar_uc.execute(
            CadastrarContaBancariaDTO(
                empresa_id=1,
                banco_nome="BB",
                banco_codigo="001",
                agencia="1234",
                conta="1111",
                tipo="CORRENTE",
                descricao="Conta 1",
            )
        )
        cadastrar_uc.execute(
            CadastrarContaBancariaDTO(
                empresa_id=1,
                banco_nome="Itau",
                banco_codigo="341",
                agencia="5678",
                conta="2222",
                tipo="POUPANCA",
                descricao="Conta 2",
            )
        )
        resultado = listar_uc.execute()
        assert len(resultado) == 2

    def test_listar_filtra_por_empresa(
        self,
        cadastrar_uc: CadastrarContaBancariaUseCase,
        listar_uc: ListarContasBancariasUseCase,
    ) -> None:
        cadastrar_uc.execute(
            CadastrarContaBancariaDTO(
                empresa_id=1,
                banco_nome="BB",
                banco_codigo="001",
                agencia="1234",
                conta="1111",
                tipo="CORRENTE",
                descricao="Conta A",
            )
        )
        cadastrar_uc.execute(
            CadastrarContaBancariaDTO(
                empresa_id=2,
                banco_nome="Itau",
                banco_codigo="341",
                agencia="5678",
                conta="2222",
                tipo="CORRENTE",
                descricao="Conta B",
            )
        )
        resultado = listar_uc.execute(empresa_id=1)
        assert len(resultado) == 1
        assert resultado[0].empresa_id == 1
