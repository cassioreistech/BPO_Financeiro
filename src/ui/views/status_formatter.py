"""Formatacao visual de status para a interface do usuario."""

from __future__ import annotations


def formatar_status_titulo(status: str) -> str:
    """Traduz status interno do titulo para exibicao ao usuario.

    O enum interno utiliza PAGO para representar titulos quitados.
    Na interface, exibimos QUITADO para maior clareza.
    """
    return {
        "ABERTO": "ABERTO",
        "PAGO": "QUITADO",
        "CANCELADO": "CANCELADO",
    }.get(status, status)
