"""Testes unitarios para o value object BancoCodigo."""

import pytest

from domain.value_objects.banco_codigo import BancoCodigo


class TestBancoCodigoValido:
    """Casos de sucesso para BancoCodigo."""

    def test_codigo_001_banco_brasil(self) -> None:
        bc = BancoCodigo("001")
        assert bc.valor == "001"

    def test_codigo_260_nubank(self) -> None:
        bc = BancoCodigo("260")
        assert bc.valor == "260"

    def test_codigo_341_itau(self) -> None:
        bc = BancoCodigo("341")
        assert bc.valor == "341"

    def test_codigo_com_zfill(self) -> None:
        bc = BancoCodigo("1")
        assert bc.valor == "001"

    def test_codigo_str(self) -> None:
        bc = BancoCodigo("001")
        assert str(bc) == "001"


class TestBancoCodigoInvalido:
    """Casos de falha para BancoCodigo."""

    def test_codigo_nao_reconhecido(self) -> None:
        with pytest.raises(ValueError, match="nao reconhecido"):
            BancoCodigo("999")

    def test_codigo_muito_longo(self) -> None:
        with pytest.raises(ValueError, match="3 digitos"):
            BancoCodigo("1234")

    def test_codigo_letras(self) -> None:
        with pytest.raises(ValueError, match="3 digitos"):
            BancoCodigo("abc")
