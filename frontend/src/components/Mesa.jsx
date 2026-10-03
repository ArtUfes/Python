import React from 'react'

export default function Mesa({ socket }) {
  return (
    <div className="poker-table">
      <h1>Mesa de Poker (MVP)</h1>
      <p style={{ marginTop: '20px' }}>Aguardando cartas e jogadores...</p>
      
      {/* Aqui entrarão os componentes de Cartas e HUD dos Jogadores no futuro */}
    </div>
  )
}
