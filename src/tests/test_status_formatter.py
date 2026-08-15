"""Testes do helper de formatacao visual de status."""

from __future__ import annotations

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
