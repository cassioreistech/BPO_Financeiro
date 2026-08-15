"""Categorias simplificadas para classificacao de titulos."""

from __future__ import annotations

from enum import Enum


class CategoriaTitulo(Enum):
    """Categorias de uso corrente para contas a pagar/receber."""

    BOLETO = "BOLETO"
    IMPOSTO = "IMPOSTO"
    SALARIO = "SALARIO"
    VENDA = "VENDA"
    SERVICO = "SERVICO"
    OUTRO = "OUTRO"
