"""Testes unitarios para o value object Email."""

import pytest

from domain.value_objects.email import Email


class TestEmailValido:
    """Casos de sucesso para Email."""

    def test_email_simples(self) -> None:
        email = Email("teste@exemplo.com")
        assert email.valor == "teste@exemplo.com"

    def test_email_com_ponto(self) -> None:
        email = Email("joao.silva@empresa.com.br")
        assert email.valor == "joao.silva@empresa.com.br"

    def test_email_com_subdominio(self) -> None:
        email = Email("contato@financeiro.empresa.com")
        assert email.valor == "contato@financeiro.empresa.com"

    def test_email_normaliza_minusculo(self) -> None:
        email = Email("TESTE@EXEMPLO.COM")
        assert email.valor == "teste@exemplo.com"

    def test_email_remove_espacos(self) -> None:
        email = Email("  teste@exemplo.com  ")
        assert email.valor == "teste@exemplo.com"

    def test_email_str(self) -> None:
        email = Email("teste@exemplo.com")
        assert str(email) == "teste@exemplo.com"


class TestEmailInvalido:
    """Casos de falha para Email."""

    def test_email_vazio(self) -> None:
        with pytest.raises(ValueError, match="não pode ser vazio"):
            Email("")

    def test_email_so_espacos(self) -> None:
        with pytest.raises(ValueError, match="não pode ser vazio"):
            Email("   ")

    def test_email_sem_arroba(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            Email("testeexemplo.com")

    def test_email_sem_dominio(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            Email("teste@")

    def test_email_sem_usuario(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            Email("@exemplo.com")

    def test_email_ponto_faltando(self) -> None:
        with pytest.raises(ValueError, match="invalido"):
            Email("teste@exemplocom")
