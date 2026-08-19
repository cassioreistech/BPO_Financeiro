"""Testes unitarios para as entidades do dominio."""

import pytest

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


class TestEscritorio:
    """Testes para a entidade Escritorio."""

    def test_criar_escritorio(self) -> None:
        esc = Escritorio(
            nome="Escritorio Contabil ABC",
            cnpj_cpf="12345678901234",
        )
        assert esc.nome == "Escritorio Contabil ABC"
        assert esc.cnpj_cpf == "12345678901234"
        assert esc.id is None
        assert esc.email is None
        assert esc.telefone is None

    def test_escritorio_com_email_e_telefone(self) -> None:
        esc = Escritorio(
            nome="Escritorio ABC",
            cnpj_cpf="12345678901234",
            email=Email("contato@abc.com"),
            telefone=Telefone("11999998888"),
        )
        assert esc.email is not None
        assert esc.email.valor == "contato@abc.com"
        assert esc.telefone is not None
        assert esc.telefone.valor == "11999998888"

    def test_escritorio_nome_vazio(self) -> None:
        with pytest.raises(ValueError, match="Nome do escritorio não pode ser vazio"):
            Escritorio(nome="", cnpj_cpf="12345678901234")

    def test_escritorio_cnpj_vazio(self) -> None:
        with pytest.raises(ValueError, match="CNPJ/CPF do escritorio não pode ser vazio"):
            Escritorio(nome="Teste", cnpj_cpf="")

    def test_escritorio_strip_nome(self) -> None:
        esc = Escritorio(nome="  Escritorio ABC  ", cnpj_cpf="12345678901234")
        assert esc.nome == "Escritorio ABC"


class TestContador:
    """Testes para a entidade Contador."""

    def test_criar_contador(self) -> None:
        cont = Contador(
            escritorio_id=1,
            nome="Joao Silva",
        )
        assert cont.escritorio_id == 1
        assert cont.nome == "Joao Silva"
        assert cont.id is None
        assert cont.crc is None

    def test_contador_com_crc(self) -> None:
        cont = Contador(
            escritorio_id=1,
            nome="Joao Silva",
            crc=CRC("01-123456/O"),
        )
        assert cont.crc is not None
        assert cont.crc.valor == "01-123456/O"

    def test_contador_nome_vazio(self) -> None:
        with pytest.raises(ValueError, match="Nome do contador não pode ser vazio"):
            Contador(escritorio_id=1, nome="")

    def test_contador_escritorio_invalido(self) -> None:
        with pytest.raises(ValueError, match="Escritorio ID deve ser um numero positivo"):
            Contador(escritorio_id=0, nome="Joao")


class TestEmpresa:
    """Testes para a entidade Empresa."""

    def test_criar_empresa(self) -> None:
        emp = Empresa(
            escritorio_id=1,
            cnpj=CNPJ("11222333000181"),
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Teste",
            regime_tributario=RegimeTributario.SIMPLES,
        )
        assert emp.escritorio_id == 1
        assert emp.razao_social == "Empresa Teste LTDA"
        assert emp.ativo == StatusEmpresa.ATIVA

    def test_empresa_por_padrao_ativa(self) -> None:
        emp = Empresa(
            escritorio_id=1,
            cnpj=CNPJ("11222333000181"),
            razao_social="Empresa",
            nome_fantasia="Fantasia",
            regime_tributario=RegimeTributario.LUCRO_PRESUMIDO,
        )
        assert emp.ativo == StatusEmpresa.ATIVA

    def test_empresa_razao_social_vazia(self) -> None:
        with pytest.raises(ValueError, match="Razao social não pode ser vazia"):
            Empresa(
                escritorio_id=1,
                cnpj=CNPJ("11222333000181"),
                razao_social="",
                nome_fantasia="Fantasia",
                regime_tributario=RegimeTributario.SIMPLES,
            )

    def test_empresa_nome_fantasia_vazio(self) -> None:
        with pytest.raises(ValueError, match="Nome fantasia não pode ser vazio"):
            Empresa(
                escritorio_id=1,
                cnpj=CNPJ("11222333000181"),
                razao_social="Empresa",
                nome_fantasia="",
                regime_tributario=RegimeTributario.SIMPLES,
            )

    def test_empresa_escritorio_invalido(self) -> None:
        with pytest.raises(ValueError, match="Escritorio ID deve ser um numero positivo"):
            Empresa(
                escritorio_id=-1,
                cnpj=CNPJ("11222333000181"),
                razao_social="Empresa",
                nome_fantasia="Fantasia",
                regime_tributario=RegimeTributario.SIMPLES,
            )


class TestContaBancaria:
    """Testes para a entidade ContaBancaria."""

    def test_criar_conta_bancaria(self) -> None:
        conta = ContaBancaria(
            empresa_id=1,
            banco_nome="Banco do Brasil",
            banco_codigo=BancoCodigo("001"),
            agencia="1234-5",
            conta="67890-1",
            tipo=TipoContaBancaria.CORRENTE,
            descricao="Conta principal",
        )
        assert conta.empresa_id == 1
        assert conta.banco_codigo is not None
        assert conta.banco_codigo.valor == "001"
        assert conta.ativo is True

    def test_conta_bancaria_por_padrao_ativa(self) -> None:
        conta = ContaBancaria(
            empresa_id=1,
            banco_nome="Itau",
            agencia="0001",
            conta="12345",
            tipo=TipoContaBancaria.POUPANCA,
            descricao="Conta poupanca",
        )
        assert conta.ativo is True

    def test_conta_bancaria_banco_vazio(self) -> None:
        with pytest.raises(ValueError, match="Nome do banco não pode ser vazio"):
            ContaBancaria(
                empresa_id=1,
                banco_nome="",
                agencia="0001",
                conta="12345",
                tipo=TipoContaBancaria.CORRENTE,
                descricao="Conta",
            )

    def test_conta_bancaria_agencia_vazia(self) -> None:
        with pytest.raises(ValueError, match="Agencia não pode ser vazia"):
            ContaBancaria(
                empresa_id=1,
                banco_nome="Itau",
                agencia="",
                conta="12345",
                tipo=TipoContaBancaria.CORRENTE,
                descricao="Conta",
            )

    def test_conta_bancaria_conta_vazia(self) -> None:
        with pytest.raises(ValueError, match="Conta não pode ser vazia"):
            ContaBancaria(
                empresa_id=1,
                banco_nome="Itau",
                agencia="0001",
                conta="",
                tipo=TipoContaBancaria.CORRENTE,
                descricao="Conta",
            )
