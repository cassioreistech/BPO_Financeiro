"""Entidade Escritorio — escritorio contabil."""

from __future__ import annotations

from dataclasses import dataclass

from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


@dataclass
class Escritorio:
    """Escritorio contabil que atende empresas clientes.

    Atributos:
        id: identificador unico (None antes de persistir)
        nome: razao social ou nome do escritorio
        cnpj_cpf: documento (CNPJ ou CPF)
        email: email de contato (opcional)
        telefone: telefone de contato (opcional)
    """

    nome: str
    cnpj_cpf: str
    id: int | None = None
    email: Email | None = None
    telefone: Telefone | None = None

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do escritorio não pode ser vazio.")
        if not self.cnpj_cpf or not self.cnpj_cpf.strip():
            raise ValueError("CNPJ/CPF do escritorio não pode ser vazio.")

        object.__setattr__(self, "nome", self.nome.strip())
        object.__setattr__(self, "cnpj_cpf", self.cnpj_cpf.strip())
