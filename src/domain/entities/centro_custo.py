"""Entidade CentroCusto — centro de custo da empresa."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CentroCusto:
    """Centro de custo vinculado a uma empresa.

    Atributos:
        id: identificador unico (None antes de persistir)
        empresa_id: FK para a empresa
        codigo: codigo do centro de custo
        nome: nome do centro de custo
        ativo: se o centro esta ativo (True por padrao)
    """

    empresa_id: int
    codigo: str
    nome: str
    id: int | None = None
    ativo: bool = True

    def __post_init__(self) -> None:
        if not self.codigo or not self.codigo.strip():
            raise ValueError("Codigo do centro de custo não pode ser vazio.")
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do centro de custo não pode ser vazio.")
        if self.empresa_id <= 0:
            raise ValueError("Empresa ID deve ser um numero positivo.")

        object.__setattr__(self, "codigo", self.codigo.strip())
        object.__setattr__(self, "nome", self.nome.strip())
