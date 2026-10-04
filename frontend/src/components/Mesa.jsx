import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Mesa({ socket }) {
  const [estado, setEstado] = useState(null);
  const [minhaVez, setMinhaVez] = useState(false);
  const [infoAcao, setInfoAcao] = useState(null);
  const [valorRaise, setValorRaise] = useState("");
  const [mensagens, setMensagens] = useState([]);
  const [fichasNaMesa, setFichasNaMesa] = useState([]);
  const chatRef = useRef(null);
  const estadoRef = useRef(estado);

  useEffect(() => {
    estadoRef.current = estado;
  }, [estado]);

  useEffect(() => {
    // Pede ao servidor Python para inicializar as threads assim que renderiza
    socket.emit('iniciar_jogo');

    socket.on('estado_mesa', (dados) => {
      setEstado(dados);
    });

    socket.on('pedir_acao', (dados) => {
      setMinhaVez(true);
      setInfoAcao(dados);
      // Sugere valor de raise como o dobro da maior aposta (padrão de poker)
      setValorRaise(dados.maior_aposta * 2 || 20); 
    });

    socket.on('mensagem', (msg) => {
      setMensagens(prev => [...prev, msg]);
    });

    socket.on('animar_fichas', (data) => {
      if (data.de === 'centro') {
        // Alguém ganhou o pote, as fichas do centro vão para ele
        const to = getPlayerCoordinates(data.para);
        setFichasNaMesa(prev => prev.map(f => {
          if (f.para === 'centro') {
            return { ...f, x: to.x, y: to.y, para: data.para };
          }
          return f;
        }));
        setTimeout(() => setFichasNaMesa([]), 5000);
      } else {
        // Alguém apostou, joga ficha pro centro
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
      socket.off('mensagem');
      socket.off('animar_fichas');
    };
  }, [socket]);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [mensagens]);

  const enviarAcao = (acao) => {
    let valorEnvio = 0;
    if (acao === 'RAISE') valorEnvio = parseInt(valorRaise) || 0;
    else if (acao === 'CALL') valorEnvio = infoAcao.falta_pagar || 0;
    
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

        <div className={`painel-controles ${minhaVez ? 'minha-vez' : 'esperando'}`}>
          {minhaVez ? (
            <>
              <h4>👉 Sua Vez!</h4>
              <p>Falta pagar: ${infoAcao.falta_pagar}</p>
              <div className="botoes-acao">
                <button className="btn-fold" onClick={() => enviarAcao('FOLD')}>❌ Fold</button>
                <button className="btn-call" onClick={() => enviarAcao(infoAcao.falta_pagar > 0 ? 'CALL' : 'CHECK')}>
                  {infoAcao.falta_pagar > 0 ? `🪙 Call ($${infoAcao.falta_pagar})` : '✔️ Check'}
                </button>
              </div>
              <div className="raise-container">
                <div className="raise-inputs">
                  <input 
                    type="range" 
                    min={infoAcao.maior_aposta * 2 || 20} 
                    max={estado.jogadores.find(j => j.nome === 'Você')?.stack || 1000}
                    step="10"
                    value={valorRaise} 
                    onChange={e => setValorRaise(e.target.value)}
                    className="slider-raise"
                  />
                  <div className="valor-raise-display">${valorRaise}</div>
                </div>
                <button className="btn-raise" onClick={() => enviarAcao('RAISE')}>🔥 Raise (${valorRaise})</button>
              </div>
            </>
          ) : (
            <h4>⏳ Aguardando os Bots...</h4>
          )}
        </div>
      </div>
    </div>
  );
}
