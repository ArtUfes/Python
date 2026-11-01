# ⏱️ Tempos e Dinâmica de Jogo (Game Pacing & Bot Timings)

Este documento registra de forma centralizada e transparente todas as durações, intervalos e tempos de resposta do Poker Python Club, facilitando ajustes rápidos de ritmo para gravações de vídeos, testes ou partidas mais cadenciadas.

---

## 1. Onde Fica Configurado no Código?

Todos os tempos da mesa são controlados centralmente no dicionário **`CONFIG_TEMPOS`** em:
📄 [`servidor.py`](file:///c:/Users/conta/Documents/programas/poker/Python/servidor.py) (por volta da linha 45)

```python
CONFIG_TEMPOS = {
    "animacao_distribuicao_cartas": 1.5,
    "intervalo_ruas_all_in": 1.8,
    "showdown_revelacao": 3.5,
    "intervalo_entre_maos": 5.0,
    "tempo_decisao_humano": 10.0,
    "bots_distribuicao": [
        {"faixa": "rapido", "prob": 0.83, "min": 1.0, "max": 3.0},   # 83% em 1 a 3 seg
        {"faixa": "pensando", "prob": 0.10, "min": 3.0, "max": 6.0}, # 10% em 3 a 6 seg
        {"faixa": "tanking", "prob": 0.02, "min": 6.0, "max": 9.0},  # 2% em 6 a 9 seg
        {"faixa": "snap", "prob": 0.05, "min": 0.5, "max": 1.0}      # 5% snap em 0.5 a 1.0 seg
    ]
}
```

---

## 2. Tempo de Resposta dos Bots (IA)

Para conferir dinamismo e realismo nas transmissões e no vídeo do YouTube, os bots utilizam uma roleta probabilística a cada decisão:

| Frequência (%) | Categoria | Intervalo de Tempo | Descrição e Propósito no Vídeo |
| :---: | :--- | :---: | :--- |
| **83%** | ⚡ **Rápido (Padrão Dinâmico)** | **1.0 a 3.0 s** | A maior parte das ações ocorre rapidamente, mantendo o vídeo fluido e sem momentos mortos. |
| **10%** | 🤔 **Pensando / Ponderando** | **3.0 a 6.0 s** | Simula o bot avaliando o bordo ou um raise expressivo, gerando expectativa no espectador. |
| **2%** | 🧠 **Tanking (Decisão Difícil)** | **6.0 a 9.0 s** | Raras vezes o bot precisa "queimar tempo" em pots gigantes ou all-ins no river. |
| **5%** | ⚡ **Snap Action (Instantâneo)** | **0.5 a 1.0 s** | Folds óbvios ou checks rápidos imediatos no pre-flop/flop. |

> **Nota:** Quando o jogador clica em `← Sair` ou `⬆ Levantar` enquanto os bots estão pensando, a thread responde em fatias de **0.1s**, garantindo que você nunca fique preso esperando o bot terminar de pensar.

---

## 3. Ritmo e Intervalos da Mesa

| Evento | Duração (s) | Chave no `CONFIG_TEMPOS` | O que acontece na tela |
| :--- | :---: | :--- | :--- |
| **Distribuição Inicial** | `1.5s` | `animacao_distribuicao_cartas` | Pausa para o baralho animar as cartas fechadas voando para cada jogador. |
| **Ruas Comunitárias (All-In)** | `1.8s` | `intervalo_ruas_all_in` | Quando todos estão em All-In, há um intervalo de 1.8s entre Flop, Turn e River para suspense. |
| **Showdown & Entrega do Pote** | `3.5s` | `showdown_revelacao` | Cartas dos bots abertas, destaque do vencedor e animação das fichas recolhidas antes da próxima mão. |
| **Transição entre Mãos** | `5.0s` | `intervalo_entre_maos` | Contagem de 5 segundos (*"Próxima mão em 5s..."*), permitindo tempo de ler o chat. |
| **Vez do Jogador Humano** | `10.0s` | `tempo_decisao_humano` | Barra regressiva animada (verde ➔ amarelo ➔ vermelho). Se esgotar, folda ou dá check automático. |

---

## 4. Presets Prontos para Ajustes Futuros

Basta substituir o bloco de `CONFIG_TEMPOS` em `servidor.py` por qualquer um dos presets abaixo conforme a sua necessidade:

### Preset A: "Gravação de Vídeo / Dinâmico" *(Ativo Atualmente)*
Ideal para YouTube e testes rápidos sem perder a ilusão de IA pensante.
* Bots: 83% em 1-3s | 10% em 3-6s | 2% em 6-9s | 5% em 0.5-1s.
* Showdown: 3.5s | Intervalo entre mãos: 5.0s.

### Preset B: "Modo Turbo / Testes em Massa"
Ideal quando você quiser rodar dezenas de mãos em segundos sem esperar quase nada:
```python
CONFIG_TEMPOS = {
    "animacao_distribuicao_cartas": 0.5,
    "intervalo_ruas_all_in": 0.6,
    "showdown_revelacao": 1.5,
    "intervalo_entre_maos": 2.0,
    "tempo_decisao_humano": 10.0,
    "bots_distribuicao": [
        {"faixa": "turbo", "prob": 0.95, "min": 0.3, "max": 1.0},
        {"faixa": "normal", "prob": 0.05, "min": 1.0, "max": 2.0}
    ]
}
```

### Preset C: "Modo TV Poker Realista / Cadenciado"
Ideal para simular transmissões de TV (WSOP / Triton Poker) com bots jogando com calma e pausas mais longas:
```python
CONFIG_TEMPOS = {
    "animacao_distribuicao_cartas": 2.0,
    "intervalo_ruas_all_in": 2.5,
    "showdown_revelacao": 5.0,
    "intervalo_entre_maos": 7.0,
    "tempo_decisao_humano": 15.0,
    "bots_distribuicao": [
        {"faixa": "normal", "prob": 0.70, "min": 3.0, "max": 7.0},
        {"faixa": "pensando", "prob": 0.20, "min": 7.0, "max": 12.0},
        {"faixa": "tanking", "prob": 0.10, "min": 12.0, "max": 18.0}
    ]
}
```

