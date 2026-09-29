import streamlit as st
import time
from core.carta import Carta
from core.jogador import Jogador
from core.baralho import Baralho
from core.avaliador_de_maos import AvaliadorDeMaos

# ==========================================
# LÓGICA DE SIMULAÇÃO (MONTE CARLO)
# ==========================================
def simular_equidade(carta1_hero, carta2_hero, num_simulations):
    hero_wins = 0
    villain_wins = 0
    ties = 0
    
    hero_cartas = [carta1_hero, carta2_hero]
    
    for _ in range(num_simulations):
        b = Baralho()
        
        # Remove as cartas do Hero do baralho atual para não serem sorteadas
        for i, c in enumerate(b.cartas):
            for hc in hero_cartas:
                if c.valor == hc.valor and c.naipe == hc.naipe:
                    b.cartas_ja_sorteadas.append(i)
        
        # Sorteia as cartas do Vilão (Range Aleatório) e da Mesa
        villain_cartas = [b.sorteia_uma_carta(), b.sorteia_uma_carta()]
        mesa = [b.sorteia_uma_carta() for _ in range(5)]
        
        # Prepara Jogador 1 (Hero)
        j1 = Jogador("Hero")
        j1.mao = sorted(mesa + hero_cartas, key=lambda c: c.valor, reverse=True)
        j1.classificacao_mao = AvaliadorDeMaos.avalia_mao(j1.mao)
        
        # Prepara Jogador 2 (Villain)
        j2 = Jogador("Villain")
        j2.mao = sorted(mesa + villain_cartas, key=lambda c: c.valor, reverse=True)
        j2.classificacao_mao = AvaliadorDeMaos.avalia_mao(j2.mao)
        
        # Avalia Vencedor
        jogadores = [j1, j2]
        melhor_class = max(j.classificacao_mao for j in jogadores)
        empatados = [j for j in jogadores if j.classificacao_mao == melhor_class]
        
        if len(empatados) == 1:
            if empatados[0].nome == "Hero": hero_wins += 1
            else: villain_wins += 1
        else:
            AvaliadorDeMaos.encontra_melhor_mao_jogadores(empatados)
            vencedores = AvaliadorDeMaos.encontra_ganhadores_desempate(empatados)
            if len(vencedores) == 1:
                if vencedores[0].nome == "Hero": hero_wins += 1
                else: villain_wins += 1
            else:
                ties += 1
                
    return hero_wins, villain_wins, ties

# ==========================================
# INTERFACE GRÁFICA (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Poker Lab", page_icon="🃏", layout="centered")

st.title("🃏 Poker Lab: Equidade")
st.write("Simule a força da sua mão contra um oponente aleatório.")

# Opções de Menu
naipes = ['♠️', '♥️', '♦️', '♣️']
valores_opcoes = {
    'A': 14, 'K': 13, 'Q': 12, 'J': 11, '10': 10, 
    '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2
}

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sua Mão (Hero)")
    v1_str = st.selectbox("Carta 1 - Valor", list(valores_opcoes.keys()), key='v1')
    n1 = st.selectbox("Carta 1 - Naipe", naipes, key='n1')
    
    v2_str = st.selectbox("Carta 2 - Valor", list(valores_opcoes.keys()), index=1, key='v2')
    n2 = st.selectbox("Carta 2 - Naipe", naipes, index=1, key='n2')

with col2:
    st.subheader("Oponente (Villain)")
    st.info("🎯 Range: **Aleatório (Any Two)**\n\n*(Futuramente: Rocha, Maníaco)*")
    sims = st.slider("Número de Simulações", min_value=100, max_value=5000, value=1000, step=100)

st.markdown("---")

if st.button("🚀 Simular Probabilidades", use_container_width=True):
    if v1_str == v2_str and n1 == n2:
        st.error("As duas cartas da sua mão não podem ser idênticas!")
    else:
        carta1 = Carta(valores_opcoes[v1_str], n1)
        carta2 = Carta(valores_opcoes[v2_str], n2)
        
        # Desenhando as cartas bonitas na tela (Ignorando o código ANSI do terminal)
        def desenhar_carta(c):
            cor = "#d63031" if c.naipe in ['♥️', '♦️'] else "#2d3436"
            return f"<span style='font-size: 24px; color: {cor}; padding: 10px 15px; border: 2px solid #dfe6e9; border-radius: 8px; margin-right: 10px; background-color: white; font-weight: bold;'>{c.simbolo}{c.naipe}</span>"
        
        st.markdown(f"**Sua Mão:** {desenhar_carta(carta1)} {desenhar_carta(carta2)}", unsafe_allow_html=True)
        st.write("")
        
        # Executa a simulação com uma barra de loading giratória
        with st.spinner(f'Rodando {sims} cenários (Monte Carlo)...'):
            hw, vw, ties = simular_equidade(carta1, carta2, sims)
            
        st.success("Simulação concluída!")
        
        # Exibe as Métricas
        hw_pct = (hw / sims) * 100
        vw_pct = (vw / sims) * 100
        t_pct = (ties / sims) * 100
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🏆 Sua Vitória", f"{hw_pct:.1f}%")
        m2.metric("💀 Vitória do Vilão", f"{vw_pct:.1f}%")
        m3.metric("🤝 Empate", f"{t_pct:.1f}%")
        
        # Gráfico Visual
        st.bar_chart({"Hero (Você)": hw_pct, "Villain (Oponente)": vw_pct, "Empate": t_pct})