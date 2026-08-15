"""Formas de pagamento para quitacao de titulos."""

from __future__ import annotations

from enum import Enum


class FormaPagamento(Enum):
    """Formas de pagamento/recebimento aceitas na quitacao."""

    DINHEIRO = "DINHEIRO"
    PIX = "PIX"
    BOLETO = "BOLETO"
    TRANSFERENCIA = "TRANSFERENCIA"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    CHEQUE = "CHEQUE"
    OUTRO = "OUTRO"
