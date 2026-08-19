"""Value object Email — endereco de e-mail normalizado."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Endereco de e-mail validado e normalizado (minusculo).

    Regras:
    - Formato basico de e-mail validado
    - Armazenado em minusculo
    - Sem espacos nas bordas
    """

    valor: str

    def __post_init__(self) -> None:
        normalizado = self.valor.strip().lower()

        if not normalizado:
            raise ValueError("Email não pode ser vazio.")

        padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(padrao, normalizado):
            raise ValueError(f"Email invalido: '{self.valor}'.")

        object.__setattr__(self, "valor", normalizado)

    def __str__(self) -> str:
        return self.valor
