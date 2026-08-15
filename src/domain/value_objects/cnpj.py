"""Value object CNPJ — documento juridico brasileiro."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CNPJ:
    """CNPJ validado (somente digitos, 14 posicoes).

    Regras de validacao:
    - Exatamente 14 digitos
    - Sequencias invalidas rejeitadas (000...000, 111...111, etc.)
    - Digitos verificadores corretos
    """

    valor: str

    def __post_init__(self) -> None:
        digitos = re.sub(r"\D", "", self.valor)

        if len(digitos) != 14:
            raise ValueError("CNPJ deve conter exatamente 14 digitos.")

        if len(set(digitos)) == 1:
            raise ValueError("CNPJ invalido: sequencia de digitos repetidos.")

        if not self._digitos_verificadores_validos(digitos):
            raise ValueError("CNPJ invalido: digitos verificadores incorretos.")

        object.__setattr__(self, "valor", digitos)

    @staticmethod
    def _digitos_verificadores_validos(cnpj: str) -> bool:
        """Valida os dois digitos verificadores do CNPJ."""
        pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        soma = sum(int(cnpj[i]) * pesos_1[i] for i in range(12))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto

        if int(cnpj[12]) != dv1:
            return False

        soma = sum(int(cnpj[i]) * pesos_2[i] for i in range(13))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto

        return int(cnpj[13]) == dv2

    @staticmethod
    def calcular_digitos_verificadores(cnpj_base_12: str) -> str:
        """Calcula os 2 digitos verificadores para um CNPJ de 12 digitos.

        Args:
            cnpj_base_12: os 12 primeiros digitos do CNPJ.

        Returns:
            Os 2 digitos verificadores como string.
        """
        pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        soma = sum(int(cnpj_base_12[i]) * pesos_1[i] for i in range(12))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto

        base_13 = cnpj_base_12 + str(dv1)
        soma = sum(int(base_13[i]) * pesos_2[i] for i in range(13))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto

        return f"{dv1}{dv2}"

    def formatted(self) -> str:
        """Retorna o CNPJ formatado: XX.XXX.XXX/XXXX-XX."""
        v = self.valor
        return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"

    def __str__(self) -> str:
        return self.formatted()
