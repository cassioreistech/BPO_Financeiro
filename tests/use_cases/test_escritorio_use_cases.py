"""Testes para os use cases de Escritorio."""

import pytest
from tests.use_cases.fake_repositories import FakeEscritorioRepository

from application.dto.escritorio_dto import CriarEscritorioDTO, EditarEscritorioDTO
from application.use_cases.escritorio_use_cases import (
    CriarEscritorioUseCase,
    EditarEscritorioUseCase,
    ListarEscritoriosUseCase,
    ObterEscritorioUseCase,
)


@pytest.fixture
def repo() -> FakeEscritorioRepository:
    return FakeEscritorioRepository()


class TestCriarEscritorio:
    def test_criar_com_sucesso(self, repo: FakeEscritorioRepository) -> None:
        uc = CriarEscritorioUseCase(repo)
        dto = CriarEscritorioDTO(
            nome="Escritorio ABC",
            cnpj_cpf="12345678901234",
            email="contato@abc.com",
            telefone="11999998888",
        )
        resultado = uc.execute(dto)

        assert resultado.nome == "Escritorio ABC"
        assert resultado.cnpj_cpf == "12345678901234"
        assert resultado.email == "contato@abc.com"
        assert resultado.telefone == "(11) 99999-8888"
        assert resultado.id > 0

    def test_criar_sem_email_telefone(self, repo: FakeEscritorioRepository) -> None:
        uc = CriarEscritorioUseCase(repo)
        dto = CriarEscritorioDTO(
            nome="Escritorio Sem Contato",
            cnpj_cpf="12345678901234",
        )
        resultado = uc.execute(dto)

        assert resultado.email is None
        assert resultado.telefone is None

    def test_criar_nome_vazio_erro(self, repo: FakeEscritorioRepository) -> None:
        uc = CriarEscritorioUseCase(repo)
        dto = CriarEscritorioDTO(nome="", cnpj_cpf="12345678901234")

        with pytest.raises(ValueError, match="Nome do escritorio nao pode ser vazio"):
            uc.execute(dto)

    def test_criar_cnpj_duplicado_erro(self, repo: FakeEscritorioRepository) -> None:
        uc = CriarEscritorioUseCase(repo)
        dto1 = CriarEscritorioDTO(nome="Escritorio 1", cnpj_cpf="12345678901234")
        uc.execute(dto1)

        dto2 = CriarEscritorioDTO(nome="Escritorio 2", cnpj_cpf="12345678901234")
        with pytest.raises(ValueError, match="Ja existe escritorio com CNPJ/CPF"):
            uc.execute(dto2)

    def test_criar_normaliza_cnpj(self, repo: FakeEscritorioRepository) -> None:
        uc = CriarEscritorioUseCase(repo)
        dto = CriarEscritorioDTO(
            nome="Escritorio ABC",
            cnpj_cpf="12.345.678/9012-34",
        )
        resultado = uc.execute(dto)

        assert resultado.cnpj_cpf == "12345678901234"


class TestEditarEscritorio:
    def test_editar_com_sucesso(self, repo: FakeEscritorioRepository) -> None:
        uc_criar = CriarEscritorioUseCase(repo)
        dto_criar = CriarEscritorioDTO(
            nome="Escritorio Original",
            cnpj_cpf="12345678901234",
        )
        criado = uc_criar.execute(dto_criar)

        uc_editar = EditarEscritorioUseCase(repo)
        dto_editar = EditarEscritorioDTO(
            id=criado.id,
            nome="Escritorio Atualizado",
            cnpj_cpf="12345678901234",
        )
        resultado = uc_editar.execute(dto_editar)

        assert resultado.nome == "Escritorio Atualizado"

    def test_editar_inexistente_erro(self, repo: FakeEscritorioRepository) -> None:
        uc = EditarEscritorioUseCase(repo)
        dto = EditarEscritorioDTO(
            id=999,
            nome="Nao Existe",
            cnpj_cpf="12345678901234",
        )

        with pytest.raises(ValueError, match="nao encontrado"):
            uc.execute(dto)

    def test_editar_cnpj_duplicado_erro(self, repo: FakeEscritorioRepository) -> None:
        uc_criar = CriarEscritorioUseCase(repo)
        uc_criar.execute(
            CriarEscritorioDTO(nome="Escritorio 1", cnpj_cpf="11111111111111")
        )
        criado2 = uc_criar.execute(
            CriarEscritorioDTO(nome="Escritorio 2", cnpj_cpf="22222222222222")
        )

        uc_editar = EditarEscritorioUseCase(repo)
        dto = EditarEscritorioDTO(
            id=criado2.id,
            nome="Escritorio 2",
            cnpj_cpf="11111111111111",
        )
        with pytest.raises(ValueError, match="Ja existe escritorio com CNPJ/CPF"):
            uc_editar.execute(dto)


class TestListarObterEscritorios:
    def test_listar(self, repo: FakeEscritorioRepository) -> None:
        uc_criar = CriarEscritorioUseCase(repo)
        uc_criar.execute(CriarEscritorioDTO(nome="Esc 1", cnpj_cpf="11111111111111"))
        uc_criar.execute(CriarEscritorioDTO(nome="Esc 2", cnpj_cpf="22222222222222"))

        uc_listar = ListarEscritoriosUseCase(repo)
        resultado = uc_listar.execute()

        assert len(resultado) == 2

    def test_obter_por_id(self, repo: FakeEscritorioRepository) -> None:
        uc_criar = CriarEscritorioUseCase(repo)
        criado = uc_criar.execute(
            CriarEscritorioDTO(nome="Escritorio X", cnpj_cpf="12345678901234")
        )

        uc_obter = ObterEscritorioUseCase(repo)
        resultado = uc_obter.execute(criado.id)

        assert resultado.nome == "Escritorio X"

    def test_obter_inexistente_erro(self, repo: FakeEscritorioRepository) -> None:
        uc = ObterEscritorioUseCase(repo)

        with pytest.raises(ValueError, match="nao encontrado"):
            uc.execute(999)
