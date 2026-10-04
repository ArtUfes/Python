import React, { useState, useEffect, useRef } from 'react';

export default function Mesa({ socket }) {
  const [estado, setEstado] = useState(null);
  const [minhaVez, setMinhaVez] = useState(false);
  const [infoAcao, setInfoAcao] = useState(null);
  const [valorRaise, setValorRaise] = useState("");
  const [mensagens, setMensagens] = useState([]);
  const chatRef = useRef(null);

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

    return () => {
      socket.off('estado_mesa');
      socket.off('pedir_acao');
      socket.off('mensagem');
    };
  }, [socket]);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [mensagens]);

  const enviarAcao = (acao) => {
    socket.emit('enviar_acao', { acao, valor: parseInt(valorRaise) || 0 });
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

  if (!estado) return <div className="poker-table"><h1>Iniciando partida...</h1></div>;

  return (
    <div className="container-jogo">
      {/* MESA PRINCIPAL */}
      <div className="poker-table">
        <div className="painel-central">
          <div className="pote-info">
            Pote Total: <span className="fichas">${estado.pote_total}</span>
          </div>
          <div className="cartas-comunitarias">
            {estado.cartas_na_mesa.length === 0 ? (
              <span style={{color: '#ffffff88'}}>[ Sem Cartas ]</span>
            ) : (
              estado.cartas_na_mesa.map((carta, i) => (
                <img key={i} className="carta-img css-carta" src={getCardImage(carta)} alt={carta} />
              ))
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
            <p className="aposta">💵 {j.aposta > 0 ? j.aposta : ''}</p>
            
            <div className="mao-jogador">
              {j.cartas.map((c, i) => (
                <img key={i} className="carta-img mini-carta" src={getCardImage(c)} alt={c} />
              ))}
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
                <button className="btn-call" onClick={() => enviarAcao('CALL')}>
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
