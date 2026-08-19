#!/bin/bash
# setup-ecc-project.sh
# Inicializa projeto novo com ECC (rules, skills, agents, hooks)
# Uso: ./setup-ecc-project.sh [--stack python|typescript|go|rust|java]

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_err() { echo -e "${RED}[ERR]${NC} $1"; }

# Config
STACK="python"
ECC_CONFIG_DIR="${HOME}/.config/opencode"
PROJECT_DIR="$(pwd)"

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --stack)
            STACK="$2"
            shift 2
            ;;
        -h|--help)
            echo "Uso: $0 [--stack python|typescript|go|rust|java]"
            exit 0
            ;;
        *)
            log_err "Opção desconhecida: $1"
            exit 1
            ;;
    esac
done

log_info "Inicializando projeto ECC em: $PROJECT_DIR"
log_info "Stack: $STACK"

# 1. Verifica se ECC está instalado globalmente
if [[ ! -d "$ECC_CONFIG_DIR/rules/ecc" ]]; then
    log_err "ECC não encontrado em $ECC_CONFIG_DIR/rules/ecc"
    log_err "Execute primeiro a instalação global do ECC"
    exit 1
fi

# 2. Cria estrutura .claude
log_info "Criando estrutura .claude/"
mkdir -p .claude/rules/ecc
mkdir -p .claude/agents
mkdir -p .claude/commands
mkdir -p .claude/hooks
mkdir -p .claude/skills

# 3. Copia rules (common + stack)
log_info "Copiando rules (common + $STACK)..."
cp -r "$ECC_CONFIG_DIR/rules/ecc/common" .claude/rules/ecc/
if [[ -d "$ECC_CONFIG_DIR/rules/ecc/$STACK" ]]; then
    cp -r "$ECC_CONFIG_DIR/rules/ecc/$STACK" .claude/rules/ecc/
    log_ok "Rules $STACK copiadas"
else
    log_warn "Stack '$STACK' não encontrada em rules/ecc/, usando apenas common"
fi

# 4. Copia AGENTS.md se existir
if [[ -f "$ECC_CONFIG_DIR/AGENTS.md" ]]; then
    cp "$ECC_CONFIG_DIR/AGENTS.md" .claude/AGENTS.md
    log_ok "AGENTS.md copiado"
fi

# 5. Cria .gitignore para ECC
cat >> .gitignore << 'EOF'

# ECC / OpenCode
.claude/rules/ecc/
.opencode/session_state.json
EOF
log_ok ".gitignore atualizado"

# 6. Cria script de ativação rápida
cat > .claude/activate-ecc.sh << 'ACTIVATE_EOF'
#!/bin/bash
# source .claude/activate-ecc.sh
# Carrega skills essenciais para sessão rápida

echo "=== ECC Skills Disponíveis ==="
ls ~/.config/opencode/skill/ | head -20
echo "... ($(ls ~/.config/opencode/skill/ | wc -l) skills total)"

echo ""
echo "=== Agents Disponíveis ==="
ls ~/.config/opencode/agent/

echo ""
echo "=== Comandos Disponíveis ==="
ls ~/.config/opencode/command/

echo ""
echo "Para usar na conversa:"
echo "  skill(\"nome-da-skill\")"
echo "  agent(\"nome-do-agent\")"
ACTIVATE_EOF
chmod +x .claude/activate-ecc.sh
log_ok "Script de ativação criado: .claude/activate-ecc.sh"

# 7. Cria exemplo de CLAUDE.md do projeto
if [[ ! -f CLAUDE.md ]]; then
    cat > CLAUDE.md << 'CLAUDE_EOF'
# Projeto: {{PROJECT_NAME}}

## Stack
- Language: {{STACK}}
- Framework: 
- Database: 

## ECC Workflow
- Planning: `skill("gsd-plan-phase")` → `agent("planner")`
- TDD: `skill("tdd-workflow")` → `agent("tdd-guide")`
- Review: `skill("code-review")` → `agent("code-reviewer")`
- Security: `skill("security-review")` → `agent("security-reviewer")`

## Commands
- `gsd-next` - Próximo passo inteligente
- `gsd-plan-phase` - Planeja feature
- `gsd-execute-phase` - Executa plano
- `gsd-verify-work` - Valida com UAT

## Hooks (automáticos)
- pre-commit: lint + typecheck + test
- pre-push: full test suite
- commit-msg: conventional commits

## Rules (project-local)
- .claude/rules/ecc/common/
- .claude/rules/ecc/{{STACK}}/
CLAUDE_EOF
    # Substitui placeholders
    sed -i "s/{{PROJECT_NAME}}/$(basename "$PROJECT_DIR")/g" CLAUDE.md
    sed -i "s/{{STACK}}/$STACK/g" CLAUDE.md
    log_ok "CLAUDE.md criado"
fi

# 8. Lista skills/agents disponíveis
log_info "Recursos ECC disponíveis globalmente:"
echo "  Skills:  $(ls "$ECC_CONFIG_DIR/skill/" | wc -l)"
echo "  Agents:  $(ls "$ECC_CONFIG_DIR/agent/" | wc -l)"
echo "  Commands: $(ls "$ECC_CONFIG_DIR/command/" | wc -l)"

log_ok "Projeto inicializado com ECC!"
echo ""
echo "Próximos passos:"
echo "  1. source .claude/activate-ecc.sh  # Ver skills disponíveis"
echo "  2. Na conversa: skill(\"gsd-next\")  # Detecta estado do projeto"
echo "  3. Edite CLAUDE.md com info do seu projeto"
echo ""
echo "Skills recomendadas para começar:"
echo "  - skill(\"gsd-next\")           # Smart entry point"
echo "  - skill(\"gsd-plan-phase\")     # Planejar feature"
echo "  - skill(\"tdd-workflow\")       # TDD workflow"
echo "  - skill(\"ui-ux-pro-max\")      # Design system (se UI)"
echo "  - skill(\"security-review\")    # Security audit"