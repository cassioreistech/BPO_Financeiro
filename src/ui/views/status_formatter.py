"""Formatacao visual de status para a interface do usuario."""

from __future__ import annotations

from datetime import date


def formatar_status_titulo(
    status: str, data_vencimento: date | None = None
) -> str:
    """Traduz status interno do titulo para exibicao ao usuario.

    O enum interno utiliza PAGO para representar titulos quitados.
    Na interface, exibimos QUITADO para maior clareza.

    Quando o titulo esta ABERTO e o vencimento ja passou,
    exibimos VENCIDO para indicar a situacao.
    """
    if status == "ABERTO" and data_vencimento is not None and data_vencimento < date.today():
        return "VENCIDO"
    return {
        "ABERTO": "ABERTO",
        "PAGO": "QUITADO",
        "CANCELADO": "CANCELADO",
    }.get(status, status)
