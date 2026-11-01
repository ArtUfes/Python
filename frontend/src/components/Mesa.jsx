import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import audioEngine from '../audioEngine';

export default function Mesa({ socket, perfil, onVoltarMenu }) {
  const [estado, setEstado] = useState(null);
  const [minhaVez, setMinhaVez] = useState(false);
  const [infoAcao, setInfoAcao] = useState(null);
  const [valorRaise, setValorRaise] = useState("");
  const [mensagens, setMensagens] = useState([]);
  const [fichasNaMesa, setFichasNaMesa] = useState([]);
  const [mutado, setMutado] = useState(audioEngine.isMuted());
  const [metricasJogador, setMetricasJogador] = useState(null);
  const [modalConfirmarSaida, setModalConfirmarSaida] = useState(null);
  const [modalConfirmarLevantar, setModalConfirmarLevantar] = useState(null);
  const [modalSentar, setModalSentar] = useState(false);
  const [valorSentar, setValorSentar] = useState(1000);
  const [dadosRebuy, setDadosRebuy] = useState(null);
  const [valorRebuy, setValorRebuy] = useState(1000);
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

    socket.on('confirmar_levantar', (data) => {
      console.log("Recebeu 'confirmar_levantar':", data);
      setModalConfirmarLevantar(data.mensagem);
    });

    socket.on('jogador_sentou', () => {
      setModalSentar(false);
    });

    socket.on('erro_sentar', (err) => {
      alert(err.mensagem || "Erro ao sentar na mesa.");
    });

    socket.on('sessao_encerrada', (data) => {
      if (onVoltarMenu) {
        onVoltarMenu(data.perfil);
      }
    });

    socket.on('jogador_zerou_fichas', (data) => {
      setDadosRebuy(data);
      const defVal = Math.min(data.max_rebuy, Math.max(data.min_rebuy, data.default_rebuy || data.min_rebuy));
      setValorRebuy(defVal);
    });

    socket.on('perfil_atualizado', (novoPerfil) => {
      setDadosRebuy(prev => prev ? { ...prev, bankroll: novoPerfil.bankroll } : null);
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
      socket.off('confirmar_levantar');
      socket.off('jogador_sentou');
      socket.off('erro_sentar');
      socket.off('sessao_encerrada');
      socket.off('jogador_zerou_fichas');
      socket.off('perfil_atualizado');
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

  const handlePedirLevantar = () => {
    audioEngine.playChipBet();
    console.log("Clicou em Levantar da Mesa. Emitindo 'levantar_da_mesa'...");
    socket.emit('levantar_da_mesa');
  };

  const handleConfirmarLevantarForcado = () => {
    audioEngine.playChipBet();
    setModalConfirmarLevantar(null);
    socket.emit('levantar_da_mesa', { forcar: true });
  };

  const handleAbrirModalSentar = () => {
    audioEngine.playChipBet();
    const bb = estado?.big_blind || 20;
    const minVal = bb * 10;
    const maxVal = Math.min(bb * 1000, perfil?.bankroll || minVal);
    const defVal = Math.min(bb * 100, Math.max(minVal, maxVal));
    setValorSentar(defVal);
    setModalSentar(true);
  };

  const handleConfirmarSentar = () => {
    audioEngine.playChipBet();
    socket.emit('sentar_na_mesa', { valor: valorSentar });
    setModalSentar(false);
  };

  const handleConfirmarRebuy = () => {
    audioEngine.playChipBet();
    socket.emit('confirmar_rebuy_mesa', { valor: valorRebuy });
    setDadosRebuy(null);
  };

  const handleRecusarRebuy = () => {
    audioEngine.playChipBet();
    socket.emit('recusar_rebuy_mesa');
    setDadosRebuy(null);
  };

  const handleRecarregarNoModal = () => {
    audioEngine.playChipBet();
    socket.emit('recarregar_fichas', { valor: 10000 });
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
        {/* TOPO ESQUERDO: SAIR, LEVANTAR OU BADGE ESPECTADOR */}
        <div style={{ position: 'absolute', top: 20, left: 20, display: 'flex', alignItems: 'center', gap: 10, zIndex: 100 }}>
          <button 
            className="btn-sair-mesa"
            onClick={handlePedirSaida}
            title="Voltar ao Menu Principal"
          >
            ← Sair para o Menu
          </button>

          {!estado.humano_espectador ? (
            <button 
              className="btn-levantar-mesa"
              onClick={handlePedirLevantar}
              title="Levantar e assistir como espectador (devolve suas fichas da mesa)"
            >
              ⬆ Levantar
            </button>
          ) : (
            <div className="badge-modo-espectador" title="Você está assistindo como espectador. Clique no lugar livre para sentar!">
              👁️ Modo Espectador
            </div>
          )}
        </div>

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
        {estado.jogadores.map((j, idx) => {
          if (j.nome === 'Você' && (estado.humano_espectador || j.espectador)) {
            return (
              <div
                key={idx}
                className="jogador-box pos-0 assento-livre-box"
                onClick={handleAbrirModalSentar}
                title="Clique para sentar e escolher suas fichas"
              >
                <motion.div 
                  className="seta-sentar"
                  animate={{ y: [0, -6, 0] }}
                  transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
                >
                  ⬇
                </motion.div>
                <span className="assento-titulo">LUGAR LIVRE</span>
                <span className="assento-subtitulo">Clique para Sentar</span>
              </div>
            );
          }

          return (
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
          );
        })}

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

      {/* MODAL DE REBUY (QUANDO AS FICHAS NA MESA ACABAM) */}
      <AnimatePresence>
        {dadosRebuy && (
          <div className="modal-overlay" style={{ zIndex: 10000 }}>
            <motion.div 
              className="modal-dialog" 
              style={{ 
                maxWidth: 520, 
                background: '#0b1120', 
                border: '1px solid rgba(234, 179, 8, 0.4)', 
                boxShadow: '0 20px 50px rgba(0,0,0,0.8), 0 0 30px rgba(234, 179, 8, 0.2)' 
              }}
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
            >
              <div className="modal-header" style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', padding: '18px 24px' }}>
                <h3 style={{ margin: 0, color: '#fde047', fontSize: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  🪙 Suas Fichas na Mesa Acabaram!
                </h3>
              </div>
              <div className="modal-body" style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <p style={{ color: '#94a3b8', fontSize: '14px', margin: 0, lineHeight: 1.5 }}>
                  Você zerou seu stack nesta mão de Cash Game. Deseja fazer um <strong>Rebuy</strong> para continuar na mesa ou prefere voltar ao menu?
                </p>

                {/* Exibição do Bankroll */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.8)', padding: '12px 16px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <span style={{ fontSize: '13px', color: '#cbd5e1' }}>Saldo Disponível no Bankroll:</span>
                  <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#fef08a' }}>
                    ${dadosRebuy.bankroll.toLocaleString('en-US')}
                  </span>
                </div>

                {dadosRebuy.bankroll < dadosRebuy.min_rebuy ? (
                  <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', padding: '14px', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <span style={{ color: '#fca5a5', fontSize: '13px' }}>
                      ⚠️ Seu Bankroll (${dadosRebuy.bankroll}) é menor que a entrada mínima da mesa (${dadosRebuy.min_rebuy}). Recarregue fichas para continuar!
                    </span>
                    <button 
                      onClick={handleRecarregarNoModal}
                      style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: '#fff', border: 'none', padding: '10px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' }}
                    >
                      + Recarregar $10.000 no Bankroll
                    </button>
                  </div>
                ) : (
                  <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '13px', fontWeight: 'bold', color: '#cbd5e1' }}>Valor do Rebuy:</span>
                      <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                        <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#fde047' }}>
                          ${valorRebuy.toLocaleString('en-US')}
                        </span>
                        <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                          ({Math.round(valorRebuy / dadosRebuy.big_blind)} BBs)
                        </span>
                      </div>
                    </div>

                    <input 
                      type="range"
                      min={dadosRebuy.min_rebuy}
                      max={Math.min(dadosRebuy.max_rebuy, dadosRebuy.bankroll)}
                      step={dadosRebuy.big_blind}
                      value={Math.min(Math.min(dadosRebuy.max_rebuy, dadosRebuy.bankroll), Math.max(dadosRebuy.min_rebuy, valorRebuy))}
                      onChange={e => setValorRebuy(parseInt(e.target.value))}
                      style={{ width: '100%', accentColor: '#eab308', cursor: 'pointer' }}
                    />

                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button 
                        onClick={() => setValorRebuy(dadosRebuy.min_rebuy)}
                        style={{ flex: 1, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#cbd5e1', padding: '6px', borderRadius: '6px', fontSize: '11px', cursor: 'pointer' }}
                      >
                        Mínimo (${dadosRebuy.min_rebuy})
                      </button>
                      <button 
                        onClick={() => setValorRebuy(Math.min(Math.min(dadosRebuy.max_rebuy, dadosRebuy.bankroll), dadosRebuy.big_blind * 100))}
                        style={{ flex: 1, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#cbd5e1', padding: '6px', borderRadius: '6px', fontSize: '11px', cursor: 'pointer' }}
                      >
                        Padrão (100 BB)
                      </button>
                      <button 
                        onClick={() => setValorRebuy(Math.min(dadosRebuy.max_rebuy, dadosRebuy.bankroll))}
                        style={{ flex: 1, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#cbd5e1', padding: '6px', borderRadius: '6px', fontSize: '11px', cursor: 'pointer' }}
                      >
                        Máximo (${Math.min(dadosRebuy.max_rebuy, dadosRebuy.bankroll)})
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <div className="modal-footer" style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)', padding: '16px 24px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button 
                  className="btn-secundario" 
                  onClick={handleRecusarRebuy}
                  style={{ background: 'rgba(30, 41, 59, 0.8)', border: '1px solid rgba(255, 255, 255, 0.15)', color: '#cbd5e1', padding: '10px 18px', borderRadius: '10px', fontSize: '13px', fontWeight: 'bold', cursor: 'pointer' }}
                >
                  Voltar ao Menu
                </button>
                <button 
                  className="btn-primario-ouro" 
                  onClick={handleConfirmarRebuy}
                  disabled={dadosRebuy.bankroll < dadosRebuy.min_rebuy}
                  style={{ background: 'linear-gradient(135deg, #eab308 0%, #ca8a04 100%)', color: '#0f172a', border: 'none', padding: '10px 22px', borderRadius: '10px', fontSize: '13px', fontWeight: '800', cursor: dadosRebuy.bankroll < dadosRebuy.min_rebuy ? 'not-allowed' : 'pointer' }}
                >
                  FAZER REBUY ▶
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* MODAL CONFIRMAR LEVANTAR DA MESA (DURANTE MÃO ATIVA) */}
      <AnimatePresence>
        {modalConfirmarLevantar && (
          <div className="modal-overlay">
            <motion.div 
              className="modal-dialog alert-dialog"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
            >
              <div className="modal-header">
                <h3 style={{ color: '#f59e0b', margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                  ⚠️ Mão em Andamento!
                </h3>
              </div>
              <div className="modal-body" style={{ padding: '20px 24px' }}>
                <p style={{ color: '#e2e8f0', fontSize: '14px', lineHeight: 1.6, margin: 0 }}>
                  {modalConfirmarLevantar}
                </p>
              </div>
              <div className="modal-footer" style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)', padding: '16px 24px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button 
                  className="btn-secundario" 
                  onClick={() => setModalConfirmarLevantar(null)}
                  style={{ background: 'rgba(30, 41, 59, 0.8)', border: '1px solid rgba(255, 255, 255, 0.15)', color: '#cbd5e1', padding: '10px 18px', borderRadius: '10px', fontSize: '13px', fontWeight: 'bold', cursor: 'pointer' }}
                >
                  Continuar Jogando
                </button>
                <button 
                  className="btn-perigo-fold" 
                  onClick={handleConfirmarLevantarForcado}
                  style={{ background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '10px', fontSize: '13px', fontWeight: 'bold', cursor: 'pointer' }}
                >
                  Sim, Levantar
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* MODAL SENTAR NA MESA (MODO ESPECTADOR -> JOGADOR) */}
      <AnimatePresence>
        {modalSentar && (
          <div className="modal-overlay" onClick={() => setModalSentar(false)}>
            <motion.div 
              className="modal-dialog rebuy-dialog"
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="modal-header">
                <div>
                  <h3 style={{ margin: 0, color: '#fef08a', fontSize: '18px' }}>
                    🎰 Sentar na Mesa
                  </h3>
                  <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                    Escolha o valor de fichas para entrar na próxima rodada
                  </span>
                </div>
                <button className="btn-close-modal" onClick={() => setModalSentar(false)}>✕</button>
              </div>

              <div className="modal-body" style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.8)', padding: '12px 16px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <span style={{ fontSize: '13px', color: '#cbd5e1' }}>Saldo Disponível no Bankroll:</span>
                  <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#fef08a' }}>
                    ${perfil?.bankroll?.toLocaleString('en-US') || 0}
                  </span>
                </div>

                {perfil?.bankroll < (estado.big_blind || 20) * 10 ? (
                  <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', padding: '14px', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <span style={{ color: '#fca5a5', fontSize: '13px' }}>
                      ⚠️ Seu Bankroll é menor que a entrada mínima (${(estado.big_blind || 20) * 10}). Recarregue fichas para sentar!
                    </span>
                    <button 
                      onClick={handleRecarregarNoModal}
                      style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: '#fff', border: 'none', padding: '10px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', fontSize: '13px' }}
                    >
                      + Recarregar $10.000 no Bankroll
                    </button>
                  </div>
                ) : (
                  <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '13px', fontWeight: 'bold', color: '#cbd5e1' }}>Valor de Entrada:</span>
                      <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                        <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#fde047' }}>
                          ${valorSentar.toLocaleString('en-US')}
                        </span>
                        <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                          ({Math.round(valorSentar / (estado.big_blind || 20))} BBs)
                        </span>
                      </div>
                    </div>

                    <input 
                      type="range"
                      min={(estado.big_blind || 20) * 10}
                      max={Math.min((estado.big_blind || 20) * 1000, perfil?.bankroll || (estado.big_blind || 20) * 10)}
                      step={estado.big_blind || 20}
                      value={valorSentar}
                      onChange={e => setValorSentar(parseInt(e.target.value))}
                      style={{ width: '100%', accentColor: '#eab308', cursor: 'pointer' }}
                    />

                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button 
                        onClick={() => setValorSentar((estado.big_blind || 20) * 10)}
                        style={{ flex: 1, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#cbd5e1', padding: '6px', borderRadius: '6px', fontSize: '11px', cursor: 'pointer' }}
                      >
                        Mínimo (${(estado.big_blind || 20) * 10})
                      </button>
                      <button 
                        onClick={() => setValorSentar(Math.min((estado.big_blind || 20) * 100, perfil?.bankroll || 0))}
                        style={{ flex: 1, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#cbd5e1', padding: '6px', borderRadius: '6px', fontSize: '11px', cursor: 'pointer' }}
                      >
                        Padrão (100 BB)
                      </button>
                      <button 
                        onClick={() => setValorSentar(Math.min((estado.big_blind || 20) * 1000, perfil?.bankroll || 0))}
                        style={{ flex: 1, background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', color: '#cbd5e1', padding: '6px', borderRadius: '6px', fontSize: '11px', cursor: 'pointer' }}
                      >
                        Máximo (${Math.min((estado.big_blind || 20) * 1000, perfil?.bankroll || 0)})
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="modal-footer" style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)', padding: '16px 24px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button 
                  className="btn-secundario" 
                  onClick={() => setModalSentar(false)}
                  style={{ background: 'rgba(30, 41, 59, 0.8)', border: '1px solid rgba(255, 255, 255, 0.15)', color: '#cbd5e1', padding: '10px 18px', borderRadius: '10px', fontSize: '13px', fontWeight: 'bold', cursor: 'pointer' }}
                >
                  Cancelar
                </button>
                <button 
                  className="btn-primario-ouro" 
                  onClick={handleConfirmarSentar}
                  disabled={perfil?.bankroll < (estado.big_blind || 20) * 10}
                  style={{ background: 'linear-gradient(135deg, #eab308 0%, #ca8a04 100%)', color: '#0f172a', border: 'none', padding: '10px 22px', borderRadius: '10px', fontSize: '13px', fontWeight: '800', cursor: perfil?.bankroll < (estado.big_blind || 20) * 10 ? 'not-allowed' : 'pointer' }}
                >
                  SENTAR NA MESA ▶
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
