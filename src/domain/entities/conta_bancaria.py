"""Entidade ContaBancaria — conta bancaria da empresa."""

from __future__ import annotations

from dataclasses import dataclass

from domain.enums.tipo_conta_bancaria import TipoContaBancaria
from domain.value_objects.banco_codigo import BancoCodigo


@dataclass
class ContaBancaria:
    """Conta bancaria vinculada a uma empresa.

    Atributos:
        id: identificador unico (None antes de persistir)
        empresa_id: FK para a empresa
        banco_nome: nome do banco (ex: "Banco do Brasil")
        banco_codigo: codigo FEBRABAN (opcional)
        agencia: numero da agencia
        conta: numero da conta
        tipo: tipo da conta (CORRENTE, POUPANCA, OUTRO)
        descricao: descricao livre da conta
        ativo: se a conta esta ativa (True por padrao)
    """

    empresa_id: int
    banco_nome: str
    agencia: str
    conta: str
    tipo: TipoContaBancaria
    descricao: str
    id: int | None = None
    banco_codigo: BancoCodigo | None = None
    ativo: bool = True

    def __post_init__(self) -> None:
        if not self.banco_nome or not self.banco_nome.strip():
            raise ValueError("Nome do banco não pode ser vazio.")
        if not self.agencia or not self.agencia.strip():
            raise ValueError("Agencia não pode ser vazia.")
        if not self.conta or not self.conta.strip():
            raise ValueError("Conta não pode ser vazia.")
        if not self.descricao or not self.descricao.strip():
            raise ValueError("Descricao não pode ser vazia.")
        if self.empresa_id is None or self.empresa_id <= 0:
            raise ValueError("Empresa ID deve ser um numero positivo.")

        object.__setattr__(self, "banco_nome", self.banco_nome.strip())
        object.__setattr__(self, "agencia", self.agencia.strip())
        object.__setattr__(self, "conta", self.conta.strip())
        object.__setattr__(self, "descricao", self.descricao.strip())
