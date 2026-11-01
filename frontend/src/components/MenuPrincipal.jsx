import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import audioEngine from '../audioEngine';
import './MenuPrincipal.css';

const MESAS_CASH_GAME = [
  { id: 'micro', nome: 'Micro Stakes', sb: 5, bb: 10, cor: '#10b981', tag: 'Recomendado para Treino' },
  { id: 'medio', nome: 'Médio Stakes', sb: 10, bb: 20, cor: '#06b6d4', tag: 'Clássico VIP' },
  { id: 'alto', nome: 'High Stakes', sb: 25, bb: 50, cor: '#f59e0b', tag: 'Ação Intensa' },
  { id: 'vip', nome: 'VIP High Roller', sb: 50, bb: 100, cor: '#ec4899', tag: 'Desafio Pro' }
];

export default function MenuPrincipal({ socket, perfil, metricas, onEntrarMesa }) {
  const [modalAberto, setModalAberto] = useState(null); // 'CASH_SETUP' | 'STATS' | 'REGRAS'
  const [mesaSelecionada, setMesaSelecionada] = useState(MESAS_CASH_GAME[1]); // Padrão: $10/$20
  const [buyInEscolhido, setBuyInEscolhido] = useState(1000);
  const [mutado, setMutado] = useState(audioEngine.isMuted());

  const bankroll = typeof perfil?.bankroll === 'number' ? perfil.bankroll : 100000;
  const minBuyIn = mesaSelecionada.bb * 10;
  const maxBuyInPossivel = Math.min(mesaSelecionada.bb * 1000, bankroll);

  const handleToggleMute = () => {
    const novoStatus = audioEngine.toggleMute();
    setMutado(novoStatus);
  };

  const handleRecarregar = () => {
    audioEngine.playChipBet();
    socket.emit('recarregar_fichas', { valor: 10000 });
  };

  const handleAbrirSetupCash = () => {
    audioEngine.playChipBet();
    // Ajusta o buy-in inicial para 100 BBs respeitando o bankroll
    const defaultBuyIn = Math.min(mesaSelecionada.bb * 100, Math.max(minBuyIn, bankroll));
    setBuyInEscolhido(defaultBuyIn);
    setModalAberto('CASH_SETUP');
  };

  const handleMudarMesa = (mesa) => {
    audioEngine.playChipBet();
    setMesaSelecionada(mesa);
    const novoMin = mesa.bb * 10;
    const novoMax = Math.min(mesa.bb * 1000, bankroll);
    setBuyInEscolhido(Math.min(mesa.bb * 100, Math.max(novoMin, novoMax)));
  };

  const handleConfirmarEntrada = () => {
    if (buyInEscolhido > bankroll || buyInEscolhido < minBuyIn) return;
    audioEngine.playChipBet();
    onEntrarMesa({
      small_blind: mesaSelecionada.sb,
      big_blind: mesaSelecionada.bb,
      buy_in: buyInEscolhido
    });
  };

  return (
    <div className="menu-container">
      {/* Background Glows */}
      <div className="glow-emerald"></div>
      <div className="glow-gold"></div>

      {/* HEADER VIP */}
      <header className="menu-header">
        <div className="header-brand">
          <div className="brand-logo">
            <span className="logo-icon">♠️</span>
            <div>
              <h1 className="logo-text">PYTHON POKER CLUB</h1>
            </div>
          </div>
          <div className="compliance-badge">
            <span className="pulse-dot"></span>
            PROJETO EDUCACIONAL • SIMULAÇÃO DE IA • SEM DINHEIRO REAL
          </div>
        </div>

        <div className="header-user-panel">
          <button 
            className="btn-audio-mute" 
            onClick={handleToggleMute} 
            title={mutado ? "Ativar Áudio" : "Mutar Áudio"}
          >
            {mutado ? '🔇' : '🔊'}
          </button>

          <div className="user-profile-card">
            <div className="avatar-circle">👤</div>
            <div className="user-info">
              <span className="user-name">{perfil?.nome || 'Você'}</span>
              <div className="user-bankroll">
                <span className="coin-icon">🪙</span>
                <span className="bankroll-value">${bankroll.toLocaleString('en-US')}</span>
              </div>
            </div>
            <button 
              className="btn-recarregar" 
              onClick={handleRecarregar}
              title="Adicionar +$10.000 para testes"
            >
              + Recarregar $10k
            </button>
          </div>
        </div>
      </header>

      {/* MAIN CARDS SELECTION (OPÇÃO 1) */}
      <main className="menu-main">
        <div className="cards-selection-grid">
          {/* CARD 1: CASH GAME */}
          <motion.div 
            className="game-mode-card card-cash-game"
            whileHover={{ y: -8, scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleAbrirSetupCash}
          >
            <div className="card-badge badge-active">🟢 DISPONÍVEL</div>
            <div className="card-illustration">
              <div className="chip-stack-art">🪙</div>
              <div className="aura-effect emerald-aura"></div>
            </div>
            <h2 className="card-title">CASH GAME</h2>
            <p className="card-description">
              Mesa Contínua com Blinds Dinâmicos ($5/$10 a $50/$100) e Entradas de 10 a 1000 BBs.
            </p>
            <ul className="card-features">
              <li>✔️ Escolha o nível de blind que deseja jogar</li>
              <li>✔️ Slider interativo de Buy-In flexível</li>
              <li>✔️ Rebuys automáticos e saída a qualquer momento</li>
            </ul>
            <button className="btn-card-action btn-play-cash">
              JOGAR AGORA <span>▶</span>
            </button>
          </motion.div>

          {/* CARD 2: TORNEIO (EM BREVE) */}
          <motion.div 
            className="game-mode-card card-torneio"
            whileHover={{ y: -4 }}
          >
            <div className="card-badge badge-soon">⏳ EM BREVE</div>
            <div className="card-illustration">
              <div className="trophy-art">🏆</div>
              <div className="aura-effect gold-aura"></div>
            </div>
            <h2 className="card-title">TORNEIO</h2>
            <p className="card-description">
              Competição Sit & Go Mata-Mata com Subida Periódica de Blinds e Disputa pelo Troféu.
            </p>
            <ul className="card-features">
              <li>⚡ Buy-In único com stack idêntico para todos</li>
              <li>⚡ Eliminação direta ao zerar as fichas (sem rebuy)</li>
              <li>⚡ Premiação e pódio para os sobreviventes</li>
            </ul>
            <button className="btn-card-action btn-soon" disabled>
              EM DESENVOLVIMENTO 🔒
            </button>
          </motion.div>
        </div>
      </main>

      {/* FOOTER UTILITY BAR */}
      <footer className="menu-footer">
        <button className="btn-footer-util" onClick={() => setModalAberto('STATS')}>
          📊 Minhas Estatísticas & HUD
        </button>
        <a 
          href="http://localhost:5000/api/historico-txt" 
          download="historico_pokerstars.txt"
          className="btn-footer-util"
          onClick={() => audioEngine.playChipBet()}
        >
          📜 Baixar Histórico (.txt)
        </a>
        <button className="btn-footer-util" onClick={() => setModalAberto('REGRAS')}>
          📖 Regras do Jogo
        </button>
      </footer>

      {/* MODAL SETUP CASH GAME (ESTILO RALLYACES) */}
      <AnimatePresence>
        {modalAberto === 'CASH_SETUP' && (
          <div className="modal-overlay" onClick={() => setModalAberto(null)}>
            <motion.div 
              className="modal-dialog setup-dialog"
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="modal-header">
                <h3>Configurar Entrada no Cash Game</h3>
                <button className="btn-close-modal" onClick={() => setModalAberto(null)}>✕</button>
              </div>

              <div className="modal-body">
                {/* 1. Escolha da Mesa */}
                <label className="section-label">1. Escolha os Blinds da Mesa:</label>
                <div className="mesas-grid">
                  {MESAS_CASH_GAME.map(m => (
                    <div 
                      key={m.id}
                      className={`mesa-card-opt ${mesaSelecionada.id === m.id ? 'selecionada' : ''}`}
                      onClick={() => handleMudarMesa(m)}
                      style={{ '--cor-tema': m.cor }}
                    >
                      <div className="mesa-opt-topo">
                        <span className="mesa-opt-nome">{m.nome}</span>
                        <span className="mesa-opt-blinds">${m.sb} / ${m.bb}</span>
                      </div>
                      <span className="mesa-opt-tag">{m.tag}</span>
                      <span className="mesa-opt-faixa">Entrada: ${m.bb * 10} a ${m.bb * 1000}</span>
                    </div>
                  ))}
                </div>

                {/* 2. Slider de Buy-In */}
                <div className="buyin-section">
                  <div className="buyin-header">
                    <label className="section-label">2. Escolha o valor do Buy-In:</label>
                    <div className="buyin-val-destaque">
                      <span className="valor">${buyInEscolhido.toLocaleString('en-US')}</span>
                      <span className="bbs">({Math.round(buyInEscolhido / mesaSelecionada.bb)} BBs)</span>
                    </div>
                  </div>

                  {bankroll < minBuyIn ? (
                    <div className="alerta-sem-saldo">
                      ⚠️ Seu saldo no Bankroll (${bankroll}) é menor que a entrada mínima desta mesa (${minBuyIn}). Recarregue fichas no menu ou escolha uma mesa menor.
                    </div>
                  ) : (
                    <>
                      <input 
                        type="range"
                        className="slider-buyin"
                        min={minBuyIn}
                        max={maxBuyInPossivel}
                        step={mesaSelecionada.bb}
                        value={buyInEscolhido}
                        onChange={e => setBuyInEscolhido(parseInt(e.target.value))}
                      />

                      <div className="preset-buttons">
                        <button 
                          className="btn-preset" 
                          onClick={() => setBuyInEscolhido(minBuyIn)}
                        >
                          Mínimo (10 BB - ${minBuyIn})
                        </button>
                        <button 
                          className="btn-preset" 
                          onClick={() => setBuyInEscolhido(Math.min(mesaSelecionada.bb * 100, maxBuyInPossivel))}
                        >
                          Padrão (100 BB - ${mesaSelecionada.bb * 100})
                        </button>
                        <button 
                          className="btn-preset" 
                          onClick={() => setBuyInEscolhido(maxBuyInPossivel)}
                        >
                          Máximo (${maxBuyInPossivel})
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>

              <div className="modal-footer">
                <button className="btn-secundario" onClick={() => setModalAberto(null)}>Cancelar</button>
                <button 
                  className="btn-primario-ouro" 
                  onClick={handleConfirmarEntrada}
                  disabled={bankroll < minBuyIn}
                >
                  SENTAR NA MESA ▶
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* MODAL ESTATÍSTICAS & HUD */}
      <AnimatePresence>
        {modalAberto === 'STATS' && (
          <div className="modal-overlay" onClick={() => setModalAberto(null)}>
            <motion.div 
              className="modal-dialog stats-dialog"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="modal-header">
                <h3>📊 Carreira e Indicadores de Jogo</h3>
                <button className="btn-close-modal" onClick={() => setModalAberto(null)}>✕</button>
              </div>
              <div className="modal-body stats-grid-body">
                <div className="stat-box">
                  <span className="stat-label">Mãos Disputadas</span>
                  <span className="stat-number">{metricas?.total_maos ?? perfil?.maos_jogadas ?? 0}</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Vitórias</span>
                  <span className="stat-number">{perfil?.vitorias ?? 0}</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Taxa de Vitória</span>
                  <span className="stat-number">
                    {(metricas?.total_maos || perfil?.maos_jogadas) 
                      ? `${Math.round(((perfil?.vitorias || 0) / (metricas?.total_maos || perfil?.maos_jogadas || 1)) * 100)}%` 
                      : '0%'}
                  </span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">VPIP %</span>
                  <span className="stat-number">{metricas?.vpip != null ? `${metricas.vpip}%` : '0%'}</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">PFR %</span>
                  <span className="stat-number">{metricas?.pfr != null ? `${metricas.pfr}%` : '0%'}</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Fator Agressividade (AF)</span>
                  <span className="stat-number">{metricas?.af != null ? metricas.af : '0.00'}</span>
                </div>
                <div className="stat-box" style={{ gridColumn: 'span 3' }}>
                  <span className="stat-label">Perfil de Jogo (Arquétipo)</span>
                  <span className="stat-number" style={{ fontSize: '18px', color: '#2ecc71' }}>
                    {metricas?.arquetipo || 'Iniciante'}
                  </span>
                </div>
              </div>
              <div className="modal-footer">
                <button className="btn-primario-ouro" onClick={() => setModalAberto(null)}>Fechar</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* MODAL REGRAS DO JOGO */}
      <AnimatePresence>
        {modalAberto === 'REGRAS' && (
          <div className="modal-overlay" onClick={() => setModalAberto(null)}>
            <motion.div 
              className="modal-dialog regras-dialog"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="modal-header">
                <h3>📖 Regras Básicas do Texas Hold'em</h3>
                <button className="btn-close-modal" onClick={() => setModalAberto(null)}>✕</button>
              </div>
              <div className="modal-body regras-text">
                <p><strong>1. Objetivo:</strong> Formar a melhor mão de 5 cartas usando suas 2 cartas fechadas e as 5 cartas comunitárias da mesa.</p>
                <p><strong>2. Rodadas de Aposta:</strong></p>
                <ul>
                  <li><strong>Pré-Flop:</strong> Cada jogador recebe 2 cartas e ocorrem as apostas iniciais (Small e Big Blind).</li>
                  <li><strong>Flop:</strong> 3 cartas comunitárias são abertas.</li>
                  <li><strong>Turn:</strong> 4ª carta comunitária é aberta.</li>
                  <li><strong>River:</strong> 5ª e última carta comunitária é revelada.</li>
                  <li><strong>Showdown:</strong> Revelação das cartas e entrega do pote à melhor mão.</li>
                </ul>
                <p><strong>3. Ranking de Mãos (do mais forte ao mais fraco):</strong></p>
                <p className="ranking-pills">
                  Royal Flush &gt; Straight Flush &gt; Quadra &gt; Full House &gt; Flush &gt; Sequência &gt; Trinca &gt; Dois Pares &gt; Par &gt; Carta Alta.
                </p>
              </div>
              <div className="modal-footer">
                <button className="btn-primario-ouro" onClick={() => setModalAberto(null)}>Entendi</button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

