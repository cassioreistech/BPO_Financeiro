"""Entidade PlanoConta — item do plano de contas."""

from __future__ import annotations

from dataclasses import dataclass

from domain.enums.tipo_plano_conta import TipoPlanoConta


@dataclass
class PlanoConta:
    """Conta do plano de contas vinculada a um escritorio.

    Atributos:
        id: identificador unico (None antes de persistir)
        escritorio_id: FK para o escritorio
        codigo: codigo da conta (ex: "1.01.001")
        nome: nome da conta
        tipo: tipo da conta (RECEITA, DESPESA, OUTRO)
        nivel: nivel hierarquico (1 = raiz)
        pai_id: FK para a conta pai (None se for raiz)
    """

    escritorio_id: int
    codigo: str
    nome: str
    tipo: TipoPlanoConta
    id: int | None = None
    nivel: int = 1
    pai_id: int | None = None

    def __post_init__(self) -> None:
        if not self.codigo or not self.codigo.strip():
            raise ValueError("Codigo da conta não pode ser vazio.")
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome da conta não pode ser vazio.")
        if self.escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")
        if self.nivel < 1:
            raise ValueError("Nivel deve ser maior ou igual a 1.")

        object.__setattr__(self, "codigo", self.codigo.strip())
        object.__setattr__(self, "nome", self.nome.strip())
