import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import audioEngine from '../audioEngine';

export default function Mesa({ socket, onVoltarMenu }) {
  const [estado, setEstado] = useState(null);
  const [minhaVez, setMinhaVez] = useState(false);
  const [infoAcao, setInfoAcao] = useState(null);
  const [valorRaise, setValorRaise] = useState("");
  const [mensagens, setMensagens] = useState([]);
  const [fichasNaMesa, setFichasNaMesa] = useState([]);
  const [mutado, setMutado] = useState(audioEngine.isMuted());
  const [metricasJogador, setMetricasJogador] = useState(null);
  const [modalConfirmarSaida, setModalConfirmarSaida] = useState(null);
  const chatRef = useRef(null);
  const estadoRef = useRef(estado);

  useEffect(() => {
    // Detecta nova rodada (distribuição de cartas) ou cartas comunitárias viradas
    if (estado && estadoRef.current) {
      const prevCartas = estadoRef.current.cartas_na_mesa?.length || 0;
      const curCartas = estado.cartas_na_mesa?.length || 0;
      if (curCartas > prevCartas) {
        audioEngine.playCommunityCard();
      } else if (estado.estado_atual === 'PRE_FLOP' && estadoRef.current.estado_atual !== 'PRE_FLOP') {
        audioEngine.playCardDeal();
      }
    }
    estadoRef.current = estado;
  }, [estado]);

  useEffect(() => {
    socket.on('estado_mesa', (dados) => {
      setEstado(dados);
      if (dados.turno_atual !== 'Você') {
        setMinhaVez(false);
      }
    });

    socket.on('pedir_acao', (dados) => {
      setMinhaVez(true);
      setInfoAcao(dados);
      audioEngine.playTurnAlert();
      setValorRaise(dados.maior_aposta * 2 || (dados?.big_blind || 20)); 
    });

    socket.on('mensagem', (msg) => {
      setMensagens(prev => [...prev, msg]);
    });

    socket.on('metricas_jogador', (dados) => {
      setMetricasJogador(dados);
    });

    socket.on('confirmar_saida', (data) => {
      setModalConfirmarSaida(data.mensagem);
    });

    socket.on('sessao_encerrada', (data) => {
      if (onVoltarMenu) {
        onVoltarMenu(data.perfil);
      }
    });

    socket.on('jogador_falido', (data) => {
      alert(data.mensagem || "Suas fichas na mesa acabaram!");
      if (onVoltarMenu) {
        onVoltarMenu();
      }
    });

    socket.on('acao_executada', (data) => {
      if (data.jogador === 'Você') {
        setMinhaVez(false);
      }
      if (data.acao === 'CHECK') {
        audioEngine.playCheck();
      } else if (data.acao === 'FOLD') {
        audioEngine.playFold();
      }
    });

    socket.on('animar_fichas', (data) => {
      if (data.de === 'centro') {
        audioEngine.playChipWin();
        const to = getPlayerCoordinates(data.para);
        setFichasNaMesa(prev => prev.map(f => {
          if (f.para === 'centro') {
            return { ...f, x: to.x, y: to.y, para: data.para };
          }
          return f;
        }));
        setTimeout(() => setFichasNaMesa([]), 5000);
      } else {
        audioEngine.playChipBet();
        const id = Date.now() + Math.random();
        const from = getPlayerCoordinates(data.de);
        const to = { x: 0, y: -120 }; 
        const newFicha = { 
          id, 
          x: to.x + (Math.random() * 80 - 40),
          y: to.y + (Math.random() * 40 - 20),
          fromX: from.x,
          fromY: from.y,
          para: 'centro'
        };
        setFichasNaMesa(prev => [...prev, newFicha]);
      }
    });

    return () => {
      socket.off('estado_mesa');
      socket.off('pedir_acao');
      socket.off('mensagem');
      socket.off('metricas_jogador');
      socket.off('confirmar_saida');
      socket.off('sessao_encerrada');
      socket.off('jogador_falido');
      socket.off('acao_executada');
      socket.off('animar_fichas');
    };
  }, [socket, onVoltarMenu]);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [mensagens]);

  const toggleMute = () => {
    const novoStatus = audioEngine.toggleMute();
    setMutado(novoStatus);
  };

  const handlePedirSaida = () => {
    audioEngine.playChipBet();
    socket.emit('sair_da_mesa');
  };

  const handleConfirmarSaidaForcada = () => {
    audioEngine.playChipBet();
    setModalConfirmarSaida(null);
    socket.emit('sair_da_mesa', { forcar: true });
  };

  const enviarAcao = (acao) => {
    let valorEnvio = 0;
    if (acao === 'RAISE') {
      valorEnvio = parseInt(valorRaise) || 0;
    } else if (acao === 'CALL') {
      valorEnvio = infoAcao.falta_pagar || 0;
    }
    
    socket.emit('enviar_acao', { acao, valor: valorEnvio });
    setMinhaVez(false);
  };

  const getCardImage = (cartaStr) => {
    if (cartaStr === "?" || cartaStr === "??" || cartaStr.includes("?")) return "https://deckofcardsapi.com/static/img/back.png";
    let valor = cartaStr.replace(/[♠♥️♣♦️]/g, '').trim();
    if (valor === '10') valor = '0';
    let naipe = '';
    if (cartaStr.includes('♥') || cartaStr.includes('♥️')) naipe = 'H';
    else if (cartaStr.includes('♦') || cartaStr.includes('♦️')) naipe = 'D';
    else if (cartaStr.includes('♣')) naipe = 'C';
    else if (cartaStr.includes('♠')) naipe = 'S';
    return `https://deckofcardsapi.com/static/img/${valor}${naipe}.png`;
  };

  const getInitialPosition = (idx) => {
    switch(idx) {
      case 0: return { y: -300, scale: 0, opacity: 0 };
      case 1: return { x: 300, scale: 0, opacity: 0 };
      case 2: return { y: 300, scale: 0, opacity: 0 };
      case 3: return { x: -300, scale: 0, opacity: 0 };
      default: return { scale: 0, opacity: 0 };
    }
  };

  const getPlayerCoordinates = (nome) => {
    if (nome === "centro") return { x: 0, y: 0 };
    if (!estado) return { x: 0, y: 0 };
    const idx = estado.jogadores.findIndex(j => j.nome === nome);
    switch(idx) {
      case 0: return { x: 0, y: 260 };
      case 1: return { x: -420, y: 0 };
      case 2: return { x: 0, y: -260 };
      case 3: return { x: 420, y: 0 };
      default: return { x: 0, y: 0 };
    }
  };

  if (!estado) {
    return (
      <div style={{ textAlign: 'center', marginTop: '100px', color: '#f8fafc' }}>
        <h2>Carregando Mesa...</h2>
      </div>
    );
  }

  return (
    <div className="container-jogo">
      {/* MESA DE POKER */}
      <div className="poker-table">
        {/* BOTÃO DE SAÍDA (CANTO SUPERIOR ESQUERDO) */}
        <button 
          className="btn-sair-mesa"
          onClick={handlePedirSaida}
          title="Voltar ao Menu Principal"
        >
          🚪 Sair para o Menu
        </button>

        {/* BOTÃO DE CONTROLE DE ÁUDIO (CANTO SUPERIOR DIREITO) */}
        <button 
          className="sound-toggle-btn" 
          onClick={toggleMute} 
          title={mutado ? "Ativar Áudio" : "Mutar Áudio"}
        >
          {mutado ? "🔇" : "🔊"}
        </button>

        <div className="painel-central">
          <div className="pote-info">
            Pote Total: <motion.span key={estado.pote_total} initial={{ scale: 1.5, color: '#fff' }} animate={{ scale: 1, color: '#f1c40f' }} className="fichas">${estado.pote_total}</motion.span>
          </div>
          <div className="cartas-comunitarias">
            {estado.cartas_na_mesa.length === 0 ? (
              <span style={{color: '#ffffff88'}}>[ Sem Cartas ]</span>
            ) : (
              <AnimatePresence>
                {estado.cartas_na_mesa.map((carta, i) => (
                  <motion.img 
                    key={carta + i} 
                    initial={{ rotateY: 90, scale: 0.8, opacity: 0 }}
                    animate={{ rotateY: 0, scale: 1, opacity: 1 }}
                    transition={{ duration: 1.2, type: "spring", stiffness: 50 }}
                    className="carta-img css-carta" 
                    src={getCardImage(carta)} 
                    alt={carta} 
                  />
                ))}
              </AnimatePresence>
            )}
          </div>
          <div className="rodada-info">
            Fase: {estado.estado_atual} • Blinds: ${estado.small_blind || 10}/${estado.big_blind || 20}
          </div>
        </div>

        {/* JOGADORES SENTADOS */}
        {estado.jogadores.map((j, idx) => (
          <div key={idx} className={`jogador-box pos-${idx} ${j.ativo ? 'ativo' : 'inativo'} ${estado.turno_atual === j.nome ? 'turno-ativo' : ''}`}>
            {estado.turno_atual === j.nome && <div className="timer-bar"></div>}
            <h3 className="nome">{j.nome}</h3>
            <p className="stack">💰 ${j.stack}</p>
            {j.nome === 'Você' && metricasJogador && metricasJogador.total_maos > 0 && (
              <div className="hud-badge" title={`Mãos: ${metricasJogador.total_maos} | AF: ${metricasJogador.af} | BB/100: ${metricasJogador.bb_100}`}>
                📊 VPIP: {metricasJogador.vpip}% | PFR: {metricasJogador.pfr}%
                <span className="arquetipo-tag">{metricasJogador.arquetipo}</span>
              </div>
            )}
            <motion.p key={j.aposta} initial={{ scale: 1.5, y: -10 }} animate={{ scale: 1, y: 0 }} className="aposta">
              💵 {j.aposta > 0 ? j.aposta : ''}
            </motion.p>
            
            <div className="mao-jogador">
              <AnimatePresence>
                {j.cartas.map((c, i) => (
                  <motion.img 
                    key={c + i} 
                    initial={getInitialPosition(idx)}
                    animate={{ scale: 1, x: 0, y: 0, opacity: 1 }}
                    transition={{ duration: 0.6, delay: i * 0.2, type: "spring", stiffness: 80 }}
                    className="carta-img mini-carta" 
                    src={getCardImage(c)} 
                    alt={c} 
                  />
                ))}
              </AnimatePresence>
            </div>
          </div>
        ))}

        {/* ANIMAÇÃO DE FICHAS EM TEMPO REAL */}
        {fichasNaMesa.map((f) => (
          <motion.div
            key={f.id}
            initial={{ x: f.fromX, y: f.fromY, scale: 0.5, opacity: 0 }}
            animate={{ x: f.x, y: f.y, scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, ease: "easeInOut" }}
            className="ficha-grafica"
            style={{ position: 'absolute', left: '50%', top: '50%' }}
          />
        ))}
      </div>

      {/* PAINEL LATERAL (DISCLAIMER, LOG E BOTÕES) */}
      <div className="painel-lateral">
        <div className="card-disclaimer-lateral">
          <div className="card-disclaimer-header">
            <span className="badge-edu">🎓 PROJETO EDUCACIONAL</span>
          </div>
          <p className="card-disclaimer-desc">
            Simulação de IA em Python • <strong>Sem Dinheiro Real</strong> (Play Money Only)
          </p>
        </div>

        <div className="log-chat" ref={chatRef}>
          <h4>📋 Transmissão</h4>
          <ul>
            {mensagens.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </div>

        {(() => {
          const meuJogador = estado?.jogadores?.find(j => j.nome === 'Você');
          const estaFora = meuJogador && !meuJogador.ativo;
          const podeAgir = minhaVez && estado?.turno_atual === 'Você' && !estaFora;

          const stackAtual = meuJogador?.stack || 0;
          const apostaAtual = meuJogador?.aposta || 0;
          const maxAtingivel = stackAtual + apostaAtual;
          const maiorAposta = infoAcao?.maior_aposta || 0;
          const podeDarRaise = podeAgir && (maxAtingivel > maiorAposta);
          
          const bbAtual = estado?.big_blind || 20;
          const minRaiseCalc = Math.min(maxAtingivel, Math.max(maiorAposta * 2, bbAtual));
          const maxRaiseCalc = maxAtingivel;

          return (
            <div className={`painel-controles ${podeAgir ? 'minha-vez' : (estaFora ? 'fora' : 'esperando')}`}>
              {podeAgir ? (
                <>
                  <h4>👉 Sua Vez!</h4>
                  <p>Falta pagar: ${infoAcao?.falta_pagar || 0}</p>
                  <div className="botoes-acao">
                    <button className="btn-fold" onClick={() => enviarAcao('FOLD')}>❌ Fold</button>
                    <button className="btn-call" onClick={() => enviarAcao(infoAcao?.falta_pagar > 0 ? 'CALL' : 'CHECK')}>
                      {infoAcao?.falta_pagar > 0 
                        ? (infoAcao.falta_pagar >= stackAtual ? `🪙 All-In ($${stackAtual})` : `🪙 Call ($${infoAcao.falta_pagar})`) 
                        : '✔️ Check'}
                    </button>
                  </div>
                  {podeDarRaise && (
                    <div className="raise-container">
                      <div className="raise-inputs">
                        <input 
                          type="range" 
                          min={minRaiseCalc} 
                          max={maxRaiseCalc}
                          step={bbAtual}
                          value={Math.min(maxRaiseCalc, Math.max(minRaiseCalc, parseInt(valorRaise) || minRaiseCalc))} 
                          onChange={e => setValorRaise(e.target.value)}
                          className="slider-raise"
                        />
                        <div className="valor-raise-display">${Math.min(maxRaiseCalc, Math.max(minRaiseCalc, parseInt(valorRaise) || minRaiseCalc))}</div>
                      </div>
                      <button className="btn-raise" onClick={() => enviarAcao('RAISE')}>
                        {parseInt(valorRaise) >= maxRaiseCalc ? `🔥 All-In ($${maxRaiseCalc})` : `🔥 Raise ($${valorRaise})`}
                      </button>
                    </div>
                  )}
                </>
              ) : estaFora ? (
                <div style={{ textAlign: 'center', padding: '15px 0' }}>
                  <h4 style={{ color: '#e74c3c' }}>💤 Você deu Fold</h4>
                  <p style={{ color: '#bdc3c7', fontSize: '13px', marginTop: '8px' }}>
                    Aguardando a conclusão da rodada...
                  </p>
                </div>
              ) : (
                <h4>⏳ Aguardando {estado?.turno_atual ? `${estado.turno_atual}...` : 'os Bots...'}</h4>
              )}
            </div>
          );
        })()}
      </div>

      {/* MODAL DE CONFIRMAÇÃO DE SAÍDA DURANTE A RODADA */}
      <AnimatePresence>
        {modalConfirmarSaida && (
          <div className="modal-overlay" style={{ zIndex: 9999 }}>
            <motion.div 
              className="modal-dialog" 
              style={{ maxWidth: 460 }}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
            >
              <div className="modal-header">
                <h3>⚠️ Confirmar Saída</h3>
                <button className="btn-close-modal" onClick={() => setModalConfirmarSaida(null)}>✕</button>
              </div>
              <div className="modal-body" style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.5 }}>
                <p>{modalConfirmarSaida}</p>
              </div>
              <div className="modal-footer">
                <button className="btn-secundario" onClick={() => setModalConfirmarSaida(null)}>
                  Continuar Jogando
                </button>
                <button 
                  className="btn-primario-ouro" 
                  style={{ background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)', color: '#fff', boxShadow: '0 4px 15px rgba(239, 68, 68, 0.4)' }}
                  onClick={handleConfirmarSaidaForcada}
                >
                  Foldar e Sair
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
