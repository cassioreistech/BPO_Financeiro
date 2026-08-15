"""DTOs do dominio do sistema BPO Financeiro."""

from application.dto.empresa_dto import (
    CadastrarEmpresaDTO,
    EditarEmpresaDTO,
    EmpresaResponseDTO,
)
from application.dto.escritorio_dto import (
    CriarEscritorioDTO,
    EditarEscritorioDTO,
    EscritorioResponseDTO,
)

__all__ = [
    "CadastrarEmpresaDTO",
    "CriarEscritorioDTO",
    "EditarEmpresaDTO",
    "EditarEscritorioDTO",
    "EmpresaResponseDTO",
    "EscritorioResponseDTO",
]
