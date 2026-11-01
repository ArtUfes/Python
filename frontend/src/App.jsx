import { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import Mesa from './components/Mesa';
import MenuPrincipal from './components/MenuPrincipal';
import './index.css';

// Conexão com o servidor Python
const socket = io('http://localhost:5000', { autoConnect: false });

function App() {
  const [conectado, setConectado] = useState(false);
  const [telaAtual, setTelaAtual] = useState('MENU'); // 'MENU' | 'MESA'
  const [perfil, setPerfil] = useState({ nome: 'Você', bankroll: 100000, maos_jogadas: 0, vitorias: 0 });
  const [metricas, setMetricas] = useState(null);

  useEffect(() => {
    socket.connect();

    socket.on('connect', () => {
      setConectado(true);
      console.log('Conectado ao servidor de Poker Python!');
      socket.emit('obter_perfil');
    });

    socket.on('disconnect', () => {
      setConectado(false);
      setTelaAtual('MENU');
    });

    socket.on('perfil_atualizado', (dados) => {
      if (dados) setPerfil(dados);
    });

    socket.on('metricas_jogador', (dados) => {
      if (dados) setMetricas(dados);
    });

    socket.on('entrada_autorizada', () => {
      setTelaAtual('MESA');
    });

    socket.on('erro_entrada', (err) => {
      alert(err.mensagem || "Erro ao entrar na mesa.");
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('perfil_atualizado');
      socket.off('metricas_jogador');
      socket.off('entrada_autorizada');
      socket.off('erro_entrada');
      socket.disconnect();
    };
  }, []);

  const handleEntrarMesa = (config) => {
    socket.emit('iniciar_cash_game', config);
  };

  const handleVoltarMenu = (perfilFinal) => {
    if (perfilFinal) setPerfil(perfilFinal);
    socket.emit('obter_perfil');
    setTelaAtual('MENU');
  };

  return (
    <>
      {conectado ? (
        telaAtual === 'MENU' ? (
          <MenuPrincipal 
            socket={socket} 
            perfil={perfil} 
            metricas={metricas}
            onEntrarMesa={handleEntrarMesa} 
          />
        ) : (
          <Mesa 
            socket={socket} 
            perfil={perfil}
            onVoltarMenu={handleVoltarMenu} 
          />
        )
      ) : (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#070b14',
          color: '#f8fafc',
          fontFamily: 'sans-serif',
          gap: '16px'
        }}>
          <h1 style={{
            fontSize: '32px',
            background: 'linear-gradient(135deg, #fff7c2, #eab308)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: 0
          }}>
            PYTHON POKER CLUB
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '15px' }}>
            Aguardando conexão com o Servidor Python (Backend)...
          </p>
          <div style={{
            padding: '8px 16px',
            borderRadius: '999px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            color: '#fca5a5',
            fontSize: '12px'
          }}>
            🔴 Offline (Porta 5000)
          </div>
        </div>
      )}
    </>
  );
}

export default App;
