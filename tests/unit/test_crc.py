"""Testes unitarios para o value object CRC."""

import pytest

from domain.value_objects.crc import CRC


class TestCRCValido:
    """Casos de sucesso para CRC."""

    def test_crc_padrao(self) -> None:
        crc = CRC("01-123456/O")
        assert crc.valor == "01-123456/O"

    def test_crc_com_digito(self) -> None:
        crc = CRC("01-123456/0")
        assert crc.valor == "01-123456/0"

    def test_crc_maiusculo(self) -> None:
        crc = CRC("01-123456/o")
        assert crc.valor == "01-123456/O"

    def test_crc_str(self) -> None:
        crc = CRC("01-123456/O")
        assert str(crc) == "01-123456/O"


class TestCRCInvalido:
    """Casos de falha para CRC."""

    def test_crc_formato_errado(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            CRC("123456789")

    def test_crc_sem_hifem(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            CRC("01123456/O")

    def test_crc_sem_barra(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            CRC("01-123456O")

    def test_crc_digitos_errados(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            CRC("1-123456/O")

    def test_crc_sufixo_invalido(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            CRC("01-123456/OP")
