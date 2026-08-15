"""Value objects do dominio do sistema BPO Financeiro."""

from domain.value_objects.banco_codigo import BancoCodigo
from domain.value_objects.cnpj import CNPJ
from domain.value_objects.crc import CRC
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone

__all__ = ["BancoCodigo", "CNPJ", "CRC", "Email", "Telefone"]
