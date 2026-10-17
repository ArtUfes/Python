import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import audioEngine from '../audioEngine';

export default function Mesa({ socket }) {
  const [estado, setEstado] = useState(null);
  const [minhaVez, setMinhaVez] = useState(false);
  const [infoAcao, setInfoAcao] = useState(null);
  const [valorRaise, setValorRaise] = useState("");
  const [mensagens, setMensagens] = useState([]);
  const [fichasNaMesa, setFichasNaMesa] = useState([]);
  const [mutado, setMutado] = useState(audioEngine.isMuted());
  const [metricasJogador, setMetricasJogador] = useState(null);
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
    // Pede ao servidor Python para inicializar as threads assim que renderiza
    socket.emit('iniciar_jogo');

    socket.on('estado_mesa', (dados) => {
      setEstado(dados);
      if (dados.turno_atual !== 'Você') {
        setMinhaVez(false);
      }
    });

    socket.on('pedir_acao', (dados) => {
      setMinhaVez(true);
      setInfoAcao(dados);
      // Alerta sonoro sutil quando a ação chega para o jogador
      audioEngine.playTurnAlert();
      // Sugere valor de raise como o dobro da maior aposta (padrão de poker)
      setValorRaise(dados.maior_aposta * 2 || 20); 
    });

    socket.on('mensagem', (msg) => {
      setMensagens(prev => [...prev, msg]);
    });

    socket.on('metricas_jogador', (dados) => {
      setMetricasJogador(dados);
    });

    socket.on('acao_executada', (data) => {
      if (data.jogador === 'Você') {
        setMinhaVez(false);
      }
      // Dispara os sons correspondentes para jogadas dos bots e humanos
      if (data.acao === 'CHECK') {
        audioEngine.playCheck();
      } else if (data.acao === 'FOLD') {
        audioEngine.playFold();
      }
    });

    socket.on('animar_fichas', (data) => {
      if (data.de === 'centro') {
        // Alguém ganhou o pote, toca som de vitória/recolher fichas
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
        // Alguém apostou, toca som de aposta de fichas
        audioEngine.playChipBet();
        const id = Date.now() + Math.random();
        const from = getPlayerCoordinates(data.de);
        // Desloca um pouco as fichas para o alto/baixo para não cobrirem o River
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
      socket.off('metricas_jogador');
      socket.off('acao_executada');
      socket.off('mensagem');
      socket.off('animar_fichas');
    };
  }, [socket]);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [mensagens]);

  const toggleMute = () => {
    const novoStatus = !mutado;
    setMutado(novoStatus);
    audioEngine.setMuted(novoStatus);
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
    const currentEstado = estadoRef.current;
    const idx = currentEstado?.jogadores.findIndex(j => j.nome === nome);
    switch(idx) {
      case 0: return { x: 0, y: 300 }; // bottom
      case 1: return { x: -350, y: 0 }; // left
      case 2: return { x: 0, y: -250 }; // top
      case 3: return { x: 350, y: 0 }; // right
      default: return { x: 0, y: 0 };
    }
  };

  if (!estado) return <div className="poker-table"><h1>Iniciando partida...</h1></div>;

  return (
    <div className="container-jogo" style={{position: 'relative'}}>
      <AnimatePresence>
        {fichasNaMesa.map(f => (
          <motion.div 
            key={f.id}
            className="ficha-grafica"
            initial={{ x: f.fromX, y: f.fromY, scale: 0.5, opacity: 0 }}
            animate={{ x: f.x, y: f.y, scale: 1, opacity: 1 }}
            exit={{ opacity: 0, scale: 0 }}
            transition={{ duration: f.para === 'centro' ? 0.5 : 1.5, ease: "easeOut" }}
            style={{ position: 'absolute', top: '50%', left: '50%', zIndex: 100 }}
          />
        ))}
      </AnimatePresence>
      {/* MESA PRINCIPAL */}
      <div className="poker-table">
        {/* DISCLAIMER EDUCACIONAL (CANTO SUPERIOR ESQUERDO) */}
        <div className="disclaimer-topo-esquerdo">
          <span className="disclaimer-badge">🎓 PROJETO EDUCACIONAL / DEVLOG</span>
          <span className="disclaimer-subtext">Simulação de IA em Python • Sem Dinheiro Real</span>
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
          <div className="rodada-info">Fase: {estado.estado_atual}</div>
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
      </div>

      {/* PAINEL LATERAL (LOG E BOTÕES) */}
      <div className="painel-lateral">
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
          
          const minRaiseCalc = Math.min(maxAtingivel, Math.max(maiorAposta * 2, 20));
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
                          step="10"
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
    </div>
  );
}
