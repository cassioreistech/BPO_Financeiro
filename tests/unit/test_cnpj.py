"""Testes unitarios para o value object CNPJ."""

import pytest

from domain.value_objects.cnpj import CNPJ


class TestCNPJValido:
    """Casos de sucesso para CNPJ."""

    def test_cnpj_valido(self) -> None:
        cnpj = CNPJ("11222333000181")
        assert cnpj.valor == "11222333000181"

    def test_cnpj_formatado(self) -> None:
        cnpj = CNPJ("11222333000181")
        assert cnpj.formatted() == "11.222.333/0001-81"

    def test_cnpj_str_retorna_formatado(self) -> None:
        cnpj = CNPJ("11222333000181")
        assert str(cnpj) == "11.222.333/0001-81"

    def test_cnpj_remove_formatacao(self) -> None:
        cnpj = CNPJ("11.222.333/0001-81")
        assert cnpj.valor == "11222333000181"


class TestCNPJInvalido:
    """Casos de falha para CNPJ."""

    def test_cnpj_muito_curto(self) -> None:
        with pytest.raises(ValueError, match="14 digitos"):
            CNPJ("1234567890123")

    def test_cnpj_muito_longo(self) -> None:
        with pytest.raises(ValueError, match="14 digitos"):
            CNPJ("123456789012345")

    def test_cnpj_digitos_repetidos(self) -> None:
        with pytest.raises(ValueError, match="repetidos"):
            CNPJ("00000000000000")

    def test_cnpj_digitos_verificadores_errados(self) -> None:
        with pytest.raises(ValueError, match="digitos verificadores"):
            CNPJ("11222333000180")

    def test_cnpj_so_letras(self) -> None:
        with pytest.raises(ValueError):
            CNPJ("abcdefghijklmnop")
