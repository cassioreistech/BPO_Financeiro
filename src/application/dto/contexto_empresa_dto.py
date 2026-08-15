"""DTOs para contexto de empresa ativa."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmpresaAtivaDTO:
    """Informacoes da empresa ativa no contexto global da aplicacao."""

    id: int
    nome_fantasia: str
    razao_social: str
    cnpj: str
