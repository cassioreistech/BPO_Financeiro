"""Value object Telefone — numero telefonico brasileiro."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Telefone:
    """Numero telefonico validado (somente digitos, 10 ou 11 posicoes).

    Regras:
    - Aceita DDD + numero (8 ou 9 digitos) = 10 ou 11 digitos total
    - Armazenado somente com digitos
    - Formato brasileiro: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
    """

    valor: str

    def __post_init__(self) -> None:
        digitos = re.sub(r"\D", "", self.valor)

        if len(digitos) not in (10, 11):
            raise ValueError(
                f"Telefone invalido: deve ter 10 ou 11 digitos, "
                f"recebido {len(digitos)} digitos."
            )

        if len(set(digitos)) == 1:
            raise ValueError("Telefone invalido: sequencia de digitos repetidos.")

        object.__setattr__(self, "valor", digitos)

    def formatted(self) -> str:
        """Retorna o telefone formatado no padrao brasileiro."""
        v = self.valor
        ddd = v[:2]
        if len(v) == 11:
            return f"({ddd}) {v[2:7]}-{v[7:]}"
        return f"({ddd}) {v[2:6]}-{v[6:]}"

    def __str__(self) -> str:
        return self.formatted()
