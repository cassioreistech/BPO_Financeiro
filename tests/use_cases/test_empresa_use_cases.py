"""Testes para os use cases de Empresa."""

import pytest
from tests.use_cases.fake_repositories import FakeEmpresaRepository

from application.dto.empresa_dto import CadastrarEmpresaDTO, EditarEmpresaDTO
from application.use_cases.empresa_use_cases import (
    CadastrarEmpresaUseCase,
    DesativarEmpresaUseCase,
    EditarEmpresaUseCase,
    ListarEmpresasUseCase,
    ObterEmpresaUseCase,
)


@pytest.fixture
def repo() -> FakeEmpresaRepository:
    return FakeEmpresaRepository()


class TestCadastrarEmpresa:
    def test_cadastrar_com_sucesso(self, repo: FakeEmpresaRepository) -> None:
        uc = CadastrarEmpresaUseCase(repo)
        dto = CadastrarEmpresaDTO(
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Teste",
            regime_tributario="SIMPLES",
        )
        resultado = uc.execute(dto)

        assert resultado.escritorio_id == 1
        assert resultado.razao_social == "Empresa Teste LTDA"
        assert resultado.ativo is True
        assert resultado.id > 0

    def test_cadastrar_com_contato(self, repo: FakeEmpresaRepository) -> None:
        uc = CadastrarEmpresaUseCase(repo)
        dto = CadastrarEmpresaDTO(
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Empresa Teste",
            nome_fantasia="Teste",
            regime_tributario="LUCRO_PRESUMIDO",
            email_financeiro="fin@empresa.com",
            telefone_financeiro="11999998888",
        )
        resultado = uc.execute(dto)

        assert resultado.email_financeiro == "fin@empresa.com"
        assert resultado.telefone_financeiro == "(11) 99999-8888"

    def test_cadastrar_razao_social_vazia_erro(
        self, repo: FakeEmpresaRepository
    ) -> None:
        uc = CadastrarEmpresaUseCase(repo)
        dto = CadastrarEmpresaDTO(
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="",
            nome_fantasia="Teste",
            regime_tributario="SIMPLES",
        )
        with pytest.raises(ValueError, match="Razao social nao pode ser vazia"):
            uc.execute(dto)

    def test_cadastrar_nome_fantasia_vazio_erro(
        self, repo: FakeEmpresaRepository
    ) -> None:
        uc = CadastrarEmpresaUseCase(repo)
        dto = CadastrarEmpresaDTO(
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Empresa",
            nome_fantasia="",
            regime_tributario="SIMPLES",
        )
        with pytest.raises(ValueError, match="Nome fantasia nao pode ser vazio"):
            uc.execute(dto)

    def test_cadastrar_cnpj_duplicado_erro(self, repo: FakeEmpresaRepository) -> None:
        uc = CadastrarEmpresaUseCase(repo)
        dto1 = CadastrarEmpresaDTO(
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Empresa 1",
            nome_fantasia="Emp 1",
            regime_tributario="SIMPLES",
        )
        uc.execute(dto1)

        dto2 = CadastrarEmpresaDTO(
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Empresa 2",
            nome_fantasia="Emp 2",
            regime_tributario="SIMPLES",
        )
        with pytest.raises(ValueError, match="Ja existe empresa com CNPJ"):
            uc.execute(dto2)

    def test_cadastrar_regime_invalido_erro(self, repo: FakeEmpresaRepository) -> None:
        uc = CadastrarEmpresaUseCase(repo)
        dto = CadastrarEmpresaDTO(
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Empresa",
            nome_fantasia="Emp",
            regime_tributario="INVALIDO",
        )
        with pytest.raises(ValueError, match="Regime tributario invalido"):
            uc.execute(dto)


class TestEditarEmpresa:
    def test_editar_com_sucesso(self, repo: FakeEmpresaRepository) -> None:
        uc_cadastrar = CadastrarEmpresaUseCase(repo)
        dto_cadastrar = CadastrarEmpresaDTO(
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Empresa Original",
            nome_fantasia="Original",
            regime_tributario="SIMPLES",
        )
        cadastrada = uc_cadastrar.execute(dto_cadastrar)

        uc_editar = EditarEmpresaUseCase(repo)
        dto_editar = EditarEmpresaDTO(
            id=cadastrada.id,
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Empresa Atualizada",
            nome_fantasia="Atualizada",
            regime_tributario="LUCRO_PRESUMIDO",
        )
        resultado = uc_editar.execute(dto_editar)

        assert resultado.razao_social == "Empresa Atualizada"
        assert resultado.regime_tributario == "LUCRO_PRESUMIDO"

    def test_editar_inexistente_erro(self, repo: FakeEmpresaRepository) -> None:
        uc = EditarEmpresaUseCase(repo)
        dto = EditarEmpresaDTO(
            id=999,
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Nao Existe",
            nome_fantasia="Nao",
            regime_tributario="SIMPLES",
        )
        with pytest.raises(ValueError, match="nao encontrada"):
            uc.execute(dto)

    def test_editar_cnpj_duplicado_erro(self, repo: FakeEmpresaRepository) -> None:
        uc_cadastrar = CadastrarEmpresaUseCase(repo)
        uc_cadastrar.execute(
            CadastrarEmpresaDTO(
                escritorio_id=1,
                cnpj="11222333000181",
                razao_social="Empresa 1",
                nome_fantasia="Emp 1",
                regime_tributario="SIMPLES",
            )
        )
        cadastrada2 =         uc_cadastrar.execute(
            CadastrarEmpresaDTO(
                escritorio_id=1,
                cnpj="33333333000191",
                razao_social="Empresa 2",
                nome_fantasia="Emp 2",
                regime_tributario="SIMPLES",
            )
        )

        uc_editar = EditarEmpresaUseCase(repo)
        dto = EditarEmpresaDTO(
            id=cadastrada2.id,
            escritorio_id=1,
            cnpj="11222333000181",
            razao_social="Empresa 2",
            nome_fantasia="Emp 2",
            regime_tributario="SIMPLES",
        )
        with pytest.raises(ValueError, match="Ja existe empresa com CNPJ"):
            uc_editar.execute(dto)


class TestDesativarEmpresa:
    def test_desativar_com_sucesso(self, repo: FakeEmpresaRepository) -> None:
        uc_cadastrar = CadastrarEmpresaUseCase(repo)
        cadastrada = uc_cadastrar.execute(
            CadastrarEmpresaDTO(
                escritorio_id=1,
                cnpj="11222333000181",
                razao_social="Empresa",
                nome_fantasia="Emp",
                regime_tributario="SIMPLES",
            )
        )

        uc_desativar = DesativarEmpresaUseCase(repo)
        resultado = uc_desativar.execute(cadastrada.id)

        assert resultado.ativo is False

    def test_desativar_inexistente_erro(self, repo: FakeEmpresaRepository) -> None:
        uc = DesativarEmpresaUseCase(repo)
        with pytest.raises(ValueError, match="nao encontrada"):
            uc.execute(999)


class TestListarObterEmpresas:
    def test_listar(self, repo: FakeEmpresaRepository) -> None:
        uc_cadastrar = CadastrarEmpresaUseCase(repo)
        uc_cadastrar.execute(
            CadastrarEmpresaDTO(
                escritorio_id=1,
                cnpj="11222333000181",
                razao_social="Emp 1",
                nome_fantasia="Emp 1",
                regime_tributario="SIMPLES",
            )
        )
        uc_cadastrar.execute(
            CadastrarEmpresaDTO(
                escritorio_id=1,
                cnpj="33333333000191",
                razao_social="Emp 2",
                nome_fantasia="Emp 2",
                regime_tributario="SIMPLES",
            )
        )

        uc_listar = ListarEmpresasUseCase(repo)
        resultado = uc_listar.execute()

        assert len(resultado) == 2

    def test_listar_filtrar_por_escritorio(
        self, repo: FakeEmpresaRepository
    ) -> None:
        uc_cadastrar = CadastrarEmpresaUseCase(repo)
        uc_cadastrar.execute(
            CadastrarEmpresaDTO(
                escritorio_id=1,
                cnpj="11222333000181",
                razao_social="Emp 1",
                nome_fantasia="Emp 1",
                regime_tributario="SIMPLES",
            )
        )
        uc_cadastrar.execute(
            CadastrarEmpresaDTO(
                escritorio_id=2,
                cnpj="33333333000191",
                razao_social="Emp 2",
                nome_fantasia="Emp 2",
                regime_tributario="SIMPLES",
            )
        )

        uc_listar = ListarEmpresasUseCase(repo)
        resultado = uc_listar.execute(escritorio_id=1)

        assert len(resultado) == 1
        assert resultado[0].escritorio_id == 1

    def test_obter_por_id(self, repo: FakeEmpresaRepository) -> None:
        uc_cadastrar = CadastrarEmpresaUseCase(repo)
        cadastrada = uc_cadastrar.execute(
            CadastrarEmpresaDTO(
                escritorio_id=1,
                cnpj="11222333000181",
                razao_social="Empresa X",
                nome_fantasia="X",
                regime_tributario="SIMPLES",
            )
        )

        uc_obter = ObterEmpresaUseCase(repo)
        resultado = uc_obter.execute(cadastrada.id)

        assert resultado.razao_social == "Empresa X"

    def test_obter_inexistente_erro(self, repo: FakeEmpresaRepository) -> None:
        uc = ObterEmpresaUseCase(repo)
        with pytest.raises(ValueError, match="nao encontrada"):
            uc.execute(999)
