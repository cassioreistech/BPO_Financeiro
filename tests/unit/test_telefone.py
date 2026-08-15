"""Testes unitarios para o value object Telefone."""

import pytest

from domain.value_objects.telefone import Telefone


class TestTelefoneValido:
    """Casos de sucesso para Telefone."""

    def test_telefone_10_digitos(self) -> None:
        tel = Telefone("1199998888")
        assert tel.valor == "1199998888"

    def test_telefone_11_digitos(self) -> None:
        tel = Telefone("11999998888")
        assert tel.valor == "11999998888"

    def test_telefone_formatado_10(self) -> None:
        tel = Telefone("1199998888")
        assert tel.formatted() == "(11) 9999-8888"

    def test_telefone_formatado_11(self) -> None:
        tel = Telefone("11999998888")
        assert tel.formatted() == "(11) 99999-8888"

    def test_telefone_remove_formatacao(self) -> None:
        tel = Telefone("(11) 99999-8888")
        assert tel.valor == "11999998888"

    def test_telefone_str(self) -> None:
        tel = Telefone("11999998888")
        assert str(tel) == "(11) 99999-8888"


class TestTelefoneInvalido:
    """Casos de falha para Telefone."""

    def test_telefone_muito_curto(self) -> None:
        with pytest.raises(ValueError, match="10 ou 11 digitos"):
            Telefone("123456789")

    def test_telefone_muito_longo(self) -> None:
        with pytest.raises(ValueError, match="10 ou 11 digitos"):
            Telefone("123456789012")

    def test_telefone_digitos_repetidos(self) -> None:
        with pytest.raises(ValueError, match="repetidos"):
            Telefone("11111111111")
