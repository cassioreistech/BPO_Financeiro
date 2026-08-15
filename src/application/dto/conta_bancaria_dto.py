"""DTOs para a entidade ContaBancaria."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CadastrarContaBancariaDTO:
    """DTO para cadastro de conta bancaria."""

    empresa_id: int
    banco_nome: str
    banco_codigo: str
    agencia: str
    conta: str
    tipo: str
    descricao: str


@dataclass(frozen=True)
class EditarContaBancariaDTO:
    """DTO para edicao de conta bancaria."""

    id: int
    empresa_id: int
    banco_nome: str
    banco_codigo: str
    agencia: str
    conta: str
    tipo: str
    descricao: str


@dataclass(frozen=True)
class ContaBancariaResponseDTO:
    """DTO de resposta para conta bancaria."""

    id: int
    empresa_id: int
    banco_nome: str
    banco_codigo: str
    agencia: str
    conta: str
    tipo: str
    descricao: str
    ativo: bool
