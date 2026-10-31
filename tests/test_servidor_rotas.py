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

if __name__ == '__main__':
    unittest.main()

