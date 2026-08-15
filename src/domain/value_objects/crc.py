"""Value object CRC — registro no Conselho Regional de Contabilidade."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CRC:
    """Registro CRC validado (padrao basico brasileiro).

    Formato esperado: XX-XXXXXX/X (ex: 01-123456/O)
    - 2 digitos, hifem, 6 digitos, barra, 1 letra (ou digito)
    """

    valor: str

    def __post_init__(self) -> None:
        normalizado = self.valor.strip().upper()

        padrao = r"^\d{2}-\d{6}/[A-Z0-9]$"
        if not re.match(padrao, normalizado):
            raise ValueError(
                f"CRC invalido: formato esperado XX-XXXXXX/X "
                f"(ex: 01-123456/O), recebido '{self.valor}'."
            )

        object.__setattr__(self, "valor", normalizado)

    def __str__(self) -> str:
        return self.valor
