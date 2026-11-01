import unittest
from servidor import app, socketio, gerenciador_perfil

class TestServidorRotas(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_endpoint_perfil(self):
        resposta = self.app.get('/api/perfil')
        self.assertEqual(resposta.status_code, 200)
        dados = resposta.get_json()
        self.assertEqual(dados['nome'], 'Você')
        self.assertIn('bankroll', dados)
        self.assertGreaterEqual(dados['bankroll'], 0)

    def test_socket_obter_perfil_e_recarregar(self):
        client = socketio.test_client(app)
        self.assertTrue(client.is_connected())

        # Obter perfil via socket
        client.emit('obter_perfil')
        recebidos = client.get_received()
        nomes_eventos = [evt['name'] for evt in recebidos]
        self.assertIn('perfil_atualizado', nomes_eventos)

        # Recarregar fichas via socket
        client.emit('recarregar_fichas', {'valor': 5000})
        recebidos = client.get_received()
        perfil_evento = next(e for e in recebidos if e['name'] == 'perfil_atualizado')
        self.assertGreaterEqual(perfil_evento['args'][0]['bankroll'], 5000)

        client.disconnect()

    def test_iniciar_cash_game_saldo_insuficiente(self):
        client = socketio.test_client(app)
        # Tenta entrar com um buy-in absurdo maior que o bankroll
        client.emit('iniciar_cash_game', {
            'small_blind': 10,
            'big_blind': 20,
            'buy_in': 99999999
        })
        recebidos = client.get_received()
        nomes_eventos = [evt['name'] for evt in recebidos]
        self.assertIn('erro_entrada', nomes_eventos)
        client.disconnect()

    def test_socket_rebuy_eventos(self):
        client = socketio.test_client(app)
        gerenciador_perfil.creditar_bankroll(2000, "Você")
        saldo_antes = gerenciador_perfil.obter_perfil("Você")['bankroll']

        # Testa confirmação de rebuy debitando do bankroll
        client.emit('confirmar_rebuy_mesa', {'valor': 1000})
        saldo_depois = gerenciador_perfil.obter_perfil("Você")['bankroll']
        self.assertEqual(saldo_depois, saldo_antes - 1000)

        # Testa recusa de rebuy
        client.emit('recusar_rebuy_mesa')
        client.disconnect()

    def test_sair_da_mesa_credita_stack(self):
        import servidor
        client = socketio.test_client(app)
        gerenciador_perfil.definir_bankroll(100000, "Você")
        
        # Simula jogador com 15000 fichas na mesa
        servidor.humano = servidor.Jogador("Você", stack=15000)
        servidor.jogo_rodando = True
        
        # Jogador pede saída
        client.emit('sair_da_mesa', {'forcar': True})
        
        perfil_depois = gerenciador_perfil.obter_perfil("Você")
        # 100000 + 15000 = 115000
        self.assertEqual(perfil_depois['bankroll'], 115000)
        self.assertEqual(servidor.humano.stack, 0)
        client.disconnect()

    def test_levantar_e_sentar_modo_espectador(self):
        import servidor
        client = socketio.test_client(app)
        gerenciador_perfil.definir_bankroll(100000, "Você")

        # 1. Simula jogador sentado com 10000 fichas
        servidor.humano = servidor.Jogador("Você", stack=10000)
        servidor.humano.espectador = False
        servidor.mesa = servidor.Mesa(small_blind=10, big_blind=20)
        servidor.jogo_rodando = True

        # 2. Jogador se levanta
        client.emit('levantar_da_mesa', {'forcar': True})
        
        perfil_depois_levantar = gerenciador_perfil.obter_perfil("Você")
        self.assertEqual(perfil_depois_levantar['bankroll'], 110000) # 100k + 10k da mesa
        self.assertEqual(servidor.humano.stack, 0)
        self.assertTrue(servidor.humano.espectador)

        # 3. Jogador no modo espectador clica para sentar novamente com 15000
        client.emit('sentar_na_mesa', {'valor': 15000})

        perfil_depois_sentar = gerenciador_perfil.obter_perfil("Você")
        self.assertEqual(perfil_depois_sentar['bankroll'], 95000) # 110k - 15k
        self.assertEqual(servidor.humano.stack, 15000)
        self.assertFalse(servidor.humano.espectador)

        client.disconnect()

if __name__ == '__main__':
    unittest.main()

