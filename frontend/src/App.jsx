import { useState, useEffect } from 'react'
import { io } from 'socket.io-client'
import Mesa from './components/Mesa'
import './index.css'

// Conexão com o futuro servidor Python
const socket = io('http://localhost:5000', { autoConnect: false })

function App() {
  const [conectado, setConectado] = useState(false)

  useEffect(() => {
    socket.connect()

    socket.on('connect', () => {
      setConectado(true)
      console.log('Conectado ao servidor de Poker!')
    })

    socket.on('disconnect', () => {
      setConectado(false)
    })

    return () => {
      socket.disconnect()
    }
  }, [])

  return (
    <>
      {conectado ? (
        <Mesa socket={socket} />
      ) : (
        <div style={{ textAlign: 'center' }}>
          <h1>Cassino Offline 🚫</h1>
          <p>Aguardando o servidor Python (Backend) iniciar...</p>
        </div>
      )}
    </>
  )
}

export default App
