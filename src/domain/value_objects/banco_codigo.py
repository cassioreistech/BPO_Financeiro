"""Value object BancoCodigo — codigo numerico do banco brasileiro."""

from __future__ import annotations

from dataclasses import dataclass

# Codigos dos bancos mais utilizados no Brasil (FEBRABAN)
CODIGOS_BANCOS_ACEITOS: set[str] = {
    "001",  # Banco do Brasil
    "033",  # Santander
    "041",  # Banrisul
    "070",  # BRB
    "077",  # Banco Inter
    "104",  # Caixa Economica Federal
    "136",  # Unicred
    "197",  # Stone
    "208",  # BTG Pactual
    "212",  # Banco Original
    "237",  # Bradesco
    "246",  # ABC Brasil
    "260",  # Nu Pagamentos (Nubank)
    "290",  # PagSeguro
    "318",  # BMG
    "336",  # C6 Bank
    "341",  # Itau Unibanco
    "389",  # Banco Mercantil
    "394",  # BMC
    "422",  # Safra
    "613",  # Omni
    "623",  # Pan
    "633",  # Rendimento
    "654",  # Banco Digio
    "707",  # Daycoval
    "741",  # Ribeirao Preto
    "745",  # Citibank
    "748",  # Sicredi
    "756",  # Sicoob
}


@dataclass(frozen=True)
class BancoCodigo:
    """Codigo de banco validado (3 digitos, zero-padded).

    Regras:
    - Armazenado com 3 digitos (zfill(3))
    - Validado contra lista de codigos aceitos (FEBRABAN)
    """

    valor: str

    def __post_init__(self) -> None:
        codigo = self.valor.zfill(3)

        if not codigo.isdigit() or len(codigo) != 3:
            raise ValueError(
                f"Codigo de banco invalido: deve conter 3 digitos, "
                f"recebido '{self.valor}'."
            )

        if codigo not in CODIGOS_BANCOS_ACEITOS:
            raise ValueError(
                f"Codigo de banco nao reconhecido: '{codigo}'. "
                f"Codigos aceitos: {sorted(CODIGOS_BANCOS_ACEITOS)}."
            )

        object.__setattr__(self, "valor", codigo)

    def __str__(self) -> str:
        return self.valor
