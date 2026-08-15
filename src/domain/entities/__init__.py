"""Entidades do dominio do sistema BPO Financeiro."""

from domain.entities.conta_bancaria import ContaBancaria
from domain.entities.contador import Contador
from domain.entities.empresa import Empresa
from domain.entities.escritorio import Escritorio

__all__ = ["ContaBancaria", "Contador", "Empresa", "Escritorio"]
