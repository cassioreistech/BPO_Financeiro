"""Testes do helper de formatacao visual de status."""

from __future__ import annotations

from datetime import date, timedelta

from ui.views.status_formatter import formatar_status_titulo


class TestFormatarStatusTitulo:
    def test_aberto_mantem_texto(self) -> None:
        assert formatar_status_titulo("ABERTO") == "ABERTO"

    def test_pago_traduz_para_quitado(self) -> None:
        assert formatar_status_titulo("PAGO") == "QUITADO"

    def test_cancelado_mantem_texto(self) -> None:
        assert formatar_status_titulo("CANCELADO") == "CANCELADO"

    def test_desconhecido_retorna_valor_original(self) -> None:
        assert formatar_status_titulo("OUTRO") == "OUTRO"

    def test_aberto_com_vencimento_futuro(self) -> None:
        futuro = date.today() + timedelta(days=5)
        assert formatar_status_titulo("ABERTO", futuro) == "ABERTO"

    def test_aberto_com_vencimento_passado(self) -> None:
        passado = date.today() - timedelta(days=1)
        assert formatar_status_titulo("ABERTO", passado) == "VENCIDO"

    def test_aberto_com_vencimento_hoje(self) -> None:
        hoje = date.today()
        assert formatar_status_titulo("ABERTO", hoje) == "ABERTO"

    def test_pago_com_vencimento_passado(self) -> None:
        passado = date.today() - timedelta(days=5)
        assert formatar_status_titulo("PAGO", passado) == "QUITADO"

    def test_cancelado_com_vencimento_passado(self) -> None:
        passado = date.today() - timedelta(days=5)
        assert formatar_status_titulo("CANCELADO", passado) == "CANCELADO"
