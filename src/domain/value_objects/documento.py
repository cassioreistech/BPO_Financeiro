"""Value object Documento — CNPJ ou CPF brasileiro."""

from __future__ import annotations

import re
from dataclasses import dataclass

from domain.value_objects.cnpj import CNPJ
from domain.value_objects.cpf import CPF


@dataclass(frozen=True)
class Documento:
    """Documento fiscal brasileiro (CNPJ ou CPF).

    Auto-detecta pelo tamanho:
    - 11 dígitos = CPF
    - 14 dígitos = CNPJ
    - Alfanumérico (até 14) = CNPJ (para legislação futura)
    """

    valor: str
    _tipo: str = "CNPJ"  # "CNPJ" ou "CPF"

    def __post_init__(self) -> None:
        # Remove pontuação
        limpo = re.sub(r"[^A-Za-z0-9]", "", self.valor).upper()

        # Detecta tipo pelo tamanho
        if len(limpo) == 11 and limpo.isdigit():
            # CPF
            cpf_obj = CPF(limpo)
            object.__setattr__(self, "valor", cpf_obj.valor)
            object.__setattr__(self, "_tipo", "CPF")
        else:
            # CNPJ (14 dígitos ou alfanumérico até 14)
            cnpj_obj = CNPJ(limpo)
            object.__setattr__(self, "valor", cnpj_obj.valor)
            object.__setattr__(self, "_tipo", "CNPJ")

    @property
    def tipo(self) -> str:
        return self._tipo

    @property
    def eh_cpf(self) -> bool:
        return self._tipo == "CPF"

    @property
    def eh_cnpj(self) -> bool:
        return self._tipo == "CNPJ"

    def formatted(self) -> str:
        """Retorna formatado conforme o tipo."""
        if self._tipo == "CPF":
            v = self.valor
            return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
        # CNPJ
        v = self.valor
        if len(v) == 14 and v.isdigit():
            return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"
        # Alfanumérico - formatação genérica
        return v

    def __str__(self) -> str:
        return self.formatted()

    def apenas_digitos(self) -> str:
        """Retorna apenas dígitos (para CPF) ou alfanumérico limpo (para CNPJ)."""
        return self.valor