# Sistema BPO Financeiro

Sistema **desktop** de BPO Financeiro para escritórios de contabilidade no Brasil.

## Objetivo

Auxiliar escritórios contábeis (público inicial: até ~20 empresas clientes) na gestão financeira
dos seus clientes. Fases futuras incluirão empresas, contadores, contas bancárias, contas a pagar
e receber, conciliação bancária, fluxo de caixa de 13 semanas, relatórios e IA.

**Estágio atual:** módulos operacionais implementados e em uso.
Funcionalidades existentes:
- Cadastros de escritório, empresa, contador, conta bancária, plano de contas e centro de custo.
- Lançamento e gestão de títulos (contas a pagar/receber) com quitacao, cancelamento e remocao.
- Filtros avancados de titulos e relatorios PDF (titulos, fluxo de caixa, projecao financeira).
- Dashboard financeiro com resumo, grafico por categoria e tabela de vencidos.
- Contexto global de empresa ativa: o usuario seleciona a empresa no cabecalho e todas as telas operacionais carregam dados dela.
- Alertas de titulos multiempresa (Vencidos / Vence hoje / Vence amanha / Esta semana), com modo consolidado (Todas) ou filtro por empresa ativa.

## Stack

| Tecnologia | Uso |
|---|---|
| Python 3.12+ | Linguagem |
| PySide6 | Interface desktop |
| SQLAlchemy 2.x | ORM / banco de dados |
| Pydantic 2.x | Validação e modelos de dados |
| SQLite | Banco local (caminho futuro: rede/nuvem) |
| Structlog | Logging estruturado |
| Pytest | Testes |
| Ruff | Lint |
| Black | Formatação |
| Mypy | Typecheck |

## Arquitetura

Hexagonal (Ports & Adapters) com estrutura em camadas:

```
src/
├── domain/          → entidades e regras de negócio (não depende de nada interno)
├── application/     → casos de uso e portas (pode usar domain)
├── infrastructure/  → banco, logging, integrações (pode usar application/domain)
└── ui/              → telas PySide6 (pode usar todas as camadas internas)
```

### Regra de dependência

As dependências apontam para dentro: `domain → application → infrastructure → ui`.
Uma camada só importa camadas **internas** a ela. A camada `domain` não importa nada do projeto.

### Convenção crítica: imports flat

Use sempre imports planos, **sem** o prefixo `src.`:

```python
from domain import ...
from application import ...
from infrastructure.database import SessionLocal
from ui.main_window import MainWindow
```

## Como rodar

### 1. Ambiente virtual e dependências

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### 2. Executar o aplicativo

```powershell
python src/main.py
```

### 3. Testes, lint, formatador e typecheck

```powershell
pytest          # testes
ruff check .    # lint
black .         # formatar
mypy            # typecheck
```

## Estrutura de dados

O banco SQLite é criado automaticamente em `data/bpo.db` na primeira execução
(o diretório `data/` também é criado automaticamente).
