"""Value object CPF — documento de pessoa fisica brasileiro."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CPF:
    """CPF validado (somente digitos, 11 posicoes).

    Regras de validacao:
    - Exatamente 11 digitos
    - Sequencias invalidas rejeitadas (000...000, 111...111, etc.)
    - Digitos verificadores corretos
    """

    valor: str

    def __post_init__(self) -> None:
        digitos = re.sub(r"\D", "", self.valor)

        if len(digitos) != 11:
            raise ValueError("CPF deve conter exatamente 11 digitos.")

        if len(set(digitos)) == 1:
            raise ValueError("CPF invalido: sequencia de digitos repetidos.")

        if not self._digitos_verificadores_validos(digitos):
            raise ValueError("CPF invalido: digitos verificadores incorretos.")

        object.__setattr__(self, "valor", digitos)

    @staticmethod
    def _digitos_verificadores_validos(cpf: str) -> bool:
        """Valida os dois digitos verificadores do CPF."""
        # Primeiro digito verificador
        pesos_1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cpf[i]) * pesos_1[i] for i in range(9))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto

        if int(cpf[9]) != dv1:
            return False

        # Segundo digito verificador
        pesos_2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cpf[i]) * pesos_2[i] for i in range(10))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto

        return int(cpf[10]) == dv2

    def formatted(self) -> str:
        """Retorna o CPF formatado: XXX.XXX.XXX-XX."""
        v = self.valor
        return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"

    def __str__(self) -> str:
        return self.formatted()