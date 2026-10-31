# 📋 Plano de Implementação: Menu Principal VIP (Versão Consolidada)

Este documento consolida as decisões tomadas para a construção do **Menu Principal VIP (Opção 1)**, sistema de **Bankroll** e **Seleção de Mesas de Cash Game estilo RallyAces**.

---

## 🗄️ 1. Arquitetura do Banco de Dados: SQLite Unificado

> **Conclusão:** Vamos usar o **mesmo arquivo `historico_partidas.db` com uma nova tabela `perfil`**.

### Por que esta é a melhor abordagem?
1. **Contra JSON:** JSON exige regravar o arquivo inteiro a cada mão para mudar 1 número. Se o jogo for fechado ou travar durante a escrita, o arquivo pode corromper. O SQLite é ACID (transações atômicas, seguro contra quedas de energia ou travamentos).
2. **Mesmo arquivo vs Arquivo separado:**
   - No SQLite, um arquivo `.db` é um banco relacional completo.
   - Manter tudo em `historico_partidas.db` permite que a tabela `perfil` se relacione com as tabelas de mãos (`mao_jogadores`), facilitando relatórios futuros (ex: *"buscar histórico apenas deste usuário"*).
   - Manutenção simples: você só tem 1 arquivo para backup ou versionar.

### Estrutura da nova tabela `perfil`:
```sql
CREATE TABLE IF NOT EXISTS perfil (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE DEFAULT 'Você',
    bankroll INTEGER DEFAULT 10000,
    maos_jogadas INTEGER DEFAULT 0,
    vitorias INTEGER DEFAULT 0,
    ultimo_resgate_bonus DATETIME,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎰 2. Especificação do Menu Principal & Fluxos

### 2.1. Topo (Header VIP)
- **Logo:** *"Python Poker Club"* em dourado metálico.
- **Badge do Jogador:**
  - Avatar circular com borda dourada.
  - Saldo Total: **`$ 10.000`** (com ícone dourado de fichas).
  - Botão de Ação Rápida: **`[+ Recarregar $10.000]`** (ativo livremente para testes; no futuro com cooldown diário).
- **Controles:** Botão de som 🔊/🔇 e selo educacional.

### 2.2. Cards de Modos
- 🪙 **Card 1: CASH GAME (Ativo)**
  - Título, arte com fichas em verde esmeralda e resumo: *"Mesas Contínuas • Blinds de $5/$10 a $50/$100 • Entrada de 10 a 1000 BBs"*.
  - Ao clicar: Abre o **Modal de Seleção de Mesas & Buy-In**.
- 🏆 **Card 2: TORNEIO (Em Breve)**
  - Título, arte dourada com troféu e badge elegante: *"EM BREVE"*.
  - Hover sutil mostrando que o modo está em desenvolvimento.

### 2.3. Modal de Entrada no Cash Game (Estilo RallyAces)
Ao clicar em Cash Game, abre um modal glassmorphism:
1. **Seleção de Stakes (Mesas):**
   - 🟢 *Micro:* Blinds $5 / $10 (Entrada mínima: $100 | Máxima: $10.000)
   - 🟡 *Médio:* Blinds $10 / $20 (Entrada mínima: $200 | Máxima: $20.000)
   - 🔴 *Alto:* Blinds $25 / $50 (Entrada mínima: $500 | Máxima: $50.000)
   - 💎 *VIP:* Blinds $50 / $100 (Entrada mínima: $1.000 | Máxima: $100.000)
2. **Slider de Fichas (10 BB a 1.000 BB):**
   - O jogador arrasta um slider para escolher o valor exato que quer levar para a mesa.
   - O slider respeita o saldo disponível no Bankroll (não deixa selecionar mais do que tem).
   - Botões de atalho: `[Min (10 BB)]` `[Padrão (100 BB)]` `[Max]`.
3. **Botão de Ação:** `[SENTAR NA MESA]`.

### 2.4. Fluxo de "Sair da Mesa"
- Botão discreto e elegante no topo da mesa: `[🚪 Sair para o Menu]`.
- Se a rodada estiver encerrada / entre mãos: Sai instantaneamente, soma o stack restante de volta no bankroll e abre o Menu Principal.
- Se houver uma mão ativa com o jogador disputando:
  - Exibe modal de confirmação: *"Você está disputando esta mão! Se sair agora, você dará FOLD e perderá as apostas já feitas nesta rodada. Deseja sair mesmo assim?"*
  - **Confirmar:** Executa o FOLD no motor, encerra a participação do jogador, devolve o que sobrou para o bankroll e volta para o menu.
  - **Cancelar:** Fecha o modal e a partida continua normalmente.

---

## 🛠️ 3. Fases de Desenvolvimento

1. **Passo 1 (Backend - `core/perfil.py`):**
   - Gerenciamento do perfil no SQLite (`obter_perfil`, `atualizar_bankroll`, `recarregar_fichas`).
   - Testes unitários em `tests/test_perfil.py`.
2. **Passo 2 (Backend - `servidor.py`):**
   - Suporte a iniciar a mesa com blinds customizados ($5/$10, $10/$20, etc.) e stack inicial escolhido.
   - Eventos de WebSocket: `obter_perfil`, `recarregar_saldo`, `iniciar_cash_game`, `sair_da_mesa`.
3. **Passo 3 (Frontend - Componentes React):**
   - Criação de `MenuPrincipal.jsx` e `MenuPrincipal.css` idêntico à imagem.
   - Modal de Seleção de Stakes + Slider de Buy-In.
   - Modal de confirmação ao clicar em "Sair da Mesa".
