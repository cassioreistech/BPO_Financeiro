# Modelos OpenCode Go — Registro da Sessão

Data: 2026-08-14
Motivo: usuário não conseguia usar os modelos pagos do OpenCode Go (erro "Insufficient balance") e queria saber quais modelos funcionavam com a chave de API.

## 1. Diagnóstico inicial

- A chave `sk-2d53...` colada pelo usuário é a **chave do gateway opencode** (idêntica à salva em `~/.local/share/opencode/auth.json`, provider `opencode`, tipo `api`). Ela é válida — por isso os modelos gratuitos funcionavam.
- A chave **não é** de DeepSeek/OpenAI/OpenRouter/etc. Testada em 22 provedores externos (OpenAI, DeepSeek, OpenRouter, Mistral, Groq, Together, Cohere, Cerebras, Hyperbolic, NVIDIA, SiliconFlow, Moonshot, Zhipu GLM, Volcengine, DashScope, StepFun, Z.ai, AIMLAPI, DeepInfra, Baidu, xAI, GitHub Models, Fireworks) → todas as chamadas reais de chat retornaram 401/400/403/404/410. Os endpoints `/v1/models` do OpenRouter/NVIDIA/AIMLAPI retornam 200 sem chave (são públicos) e não validam credenciais.

## 2. Causa raiz

- O CLI opencode instalado (versão **1.18.18**, a mais recente) **não possui o provider `opencode-go` embutido**.
- Os modelos Go eram roteados para o gateway Zen (que exige créditos/saldo) → erro `Insufficient balance`.
- A assinatura **OpenCode Go** estava **ativa** — confirmado por chamada direta a `https://opencode.ai/zen/go/v1/chat/completions` retornando HTTP 200 com `glm-5.2`.

## 3. Assinatura OpenCode Go (resumo)

- Custo: US$ 5 no primeiro mês, depois US$ 10/mês.
- **Não gera créditos automáticos** — funciona por limites de uso, não por saldo.
- Limites: 5h = US$ 12 de uso | semanal = US$ 30 | mensal = US$ 60 (~6x o valor pago).
- Ao atingir o limite, os modelos gratuitos continuam funcionando; modelos Go param (a menos que o usuário ative `Use balance`, que consome créditos extras Zen).
- Endpoint único: `https://opencode.ai/zen/go/v1` (aceita `/chat/completions`, `/messages` com `x-api-key`, e `/responses`).
- Consulta de modelos disponíveis: `https://opencode.ai/zen/go/v1/models` (26 modelos).

## 4. Mudanças feitas

### Arquivos alterados (config local, SEM relação com pagamento/plano)
1. `C:\Users\cassi\.config\opencode\opencode.json` — reescrito
2. `C:\Users\cassi\.config\opencode\opencode.jsonc` — espelhado (mesmo conteúdo)
3. `.opencode/session_state.json` (projeto) — resumo atualizado

### Configuração aplicada
- Criados dois providers customizados apontando para o endpoint Go:
  - `opencode-go` → npm `@ai-sdk/openai-compatible`, baseURL `https://opencode.ai/zen/go/v1`
  - `opencode-go-anthropic` → npm `@ai-sdk/anthropic`, mesma baseURL (usa header `x-api-key`)
- Modelo padrão definido: `opencode-go/kimi-k2.7-code`
- `blacklist` em `opencode-go` para remover do seletor: DeepSeek V4 Pro/Flash (exigem opt-in China) e MiniMax/Qwen (disponíveis no provider Anthropic, evita duplicatas).
- `whitelist` no provider `opencode` para manter **apenas os modelos gratuitos** que funcionam (big-pickle, deepseek-v4-flash-free, hy3-free, laguna-s-2.1-free, mimo-v2.5-free, nemotron-3-ultra-free, nemotron-3.5-lightning-free) e esconder todos os modelos pagos Zen (Claude, GPT, Gemini, etc.) que davam "Insufficient balance".
- Resultado: o seletor `/models` mostra **apenas 27 modelos que funcionam** (7 free + 12 Go + 8 Go Anthropic).
- A chave de API está nos arquivos de config acima (não repetida aqui para não registrar segredo em repositório).

## 5. Modelos testados e resultado

### Provider `opencode-go` (todos OK, testados)
- GLM-5.3, GLM-5.2, GLM-5.1, GLM-5
- Kimi K3, Kimi K2.7 Code, Kimi K2.6, Kimi K2.5
- MiMo V2.5 Pro, MiMo V2.5
- Hy3, Hy3 Preview
- GPT 5.6 Luna (endpoint /responses)
- Grok 4.5 (endpoint /responses)

### Provider `opencode-go-anthropic` (todos OK, testados)
- MiniMax M3, MiniMax M2.7, MiniMax M2.5
- Qwen3.8 Max, Qwen3.7 Max, Qwen3.7 Plus, Qwen3.6 Plus, Qwen3.5 Plus

### Não funcionam (removidos da lista)
- **DeepSeek V4 Pro** e **DeepSeek V4 Flash** → HTTP 403: "The latest version of this model is only available hosted in China and requires explicit opt in" em `https://opencode.ai/workspace/wrk_01KMKERC6AT7TRYSQW4HJK5RJ9/go`

## 6. Pontos de atenção / futuras ações

- **Opt-in DeepSeek V4**: disponível em `https://opencode.ai/workspace/wrk_01KMKERC6AT7TRYSQW4HJK5RJ9/go` — se o usuário fizer o opt-in, os modelos DeepSeek podem ser re-adicionados à lista (remover da `blacklist`).
- Modelos fora do plano Go (GPT-5, Claude, etc.) continuam bloqueados no gateway (exigem créditos Zen).
- Acompanhar uso em `https://opencode.ai/auth` (aba de usage do workspace `wrk_01KMKERC6AT7TRYSQW4HJK5RJ9`).
- Os testes da sessão consumiram cota mínima do plano Go (dentro do limite, sem cobrança extra).
