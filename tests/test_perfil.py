import unittest
import os
import tempfile
from core.perfil import GerenciadorPerfil

class TestGerenciadorPerfil(unittest.TestCase):
    def setUp(self):
        # Cria banco de dados temporário para isolamento absoluto dos testes
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.gerenciador = GerenciadorPerfil(db_path=self.temp_db.name)

    def tearDown(self):
        # Remove o banco temporário
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except PermissionError:
                pass

    def test_inicializacao_perfil_padrao(self):
        perfil = self.gerenciador.obter_perfil("Você")
        self.assertEqual(perfil["nome"], "Você")
        self.assertEqual(perfil["bankroll"], 100000)
        self.assertEqual(perfil["maos_jogadas"], 0)
        self.assertEqual(perfil["vitorias"], 0)

    def test_debitar_bankroll_sucesso_e_insuficiente(self):
        # Débito válido
        sucesso = self.gerenciador.debitar_bankroll(20000, "Você")
        self.assertTrue(sucesso)
        perfil = self.gerenciador.obter_perfil("Você")
        self.assertEqual(perfil["bankroll"], 80000)

        # Tentativa de debitar mais do que possui
        falha = self.gerenciador.debitar_bankroll(90000, "Você")
        self.assertFalse(falha)
        perfil = self.gerenciador.obter_perfil("Você")
        self.assertEqual(perfil["bankroll"], 80000, "Bankroll não deve mudar em caso de falha")

        # Tentativa de débito com valor inválido
        invalido = self.gerenciador.debitar_bankroll(-500, "Você")
        self.assertFalse(invalido)

    def test_creditar_bankroll(self):
        sucesso = self.gerenciador.creditar_bankroll(15000, "Você")
        self.assertTrue(sucesso)
        perfil = self.gerenciador.obter_perfil("Você")
        self.assertEqual(perfil["bankroll"], 115000)

        invalido = self.gerenciador.creditar_bankroll(-100, "Você")
        self.assertFalse(invalido)

    def test_recarregar_fichas(self):
        # Recarga padrão de 10.000
        perfil = self.gerenciador.recarregar_fichas(10000, "Você")
        self.assertEqual(perfil["bankroll"], 110000)
        self.assertIsNotNone(perfil["ultimo_resgate_bonus"])

    def test_cenario_exato_usuario_100k_buyin_rebuy_allin_saida(self):
        """
        Cenário exato solicitado pelo usuário:
        1. Saldo inicial: 100k
        2. Entra no cash game com 10k -> saldo perfil 90k, mesa 10k
        3. Sai sem jogar -> volta para 100k
        4. Entra com 10k (perfil 90k) e perde (mesa 0k)
        5. Faz rebuy de 10k -> perfil fica 80k, mesa 10k
        6. Vai all-in e ganha (mesa 50k)
        7. Ao sair da mesa: 80k + 50k = 130k no perfil!
        """
        # 1. Saldo inicial: 100k
        self.gerenciador.definir_bankroll(100000, "Você")
        self.assertEqual(self.gerenciador.obter_perfil("Você")["bankroll"], 100000)

        # 2. Entra com 10k
        self.assertTrue(self.gerenciador.debitar_bankroll(10000, "Você"))
        self.assertEqual(self.gerenciador.obter_perfil("Você")["bankroll"], 90000)
        stack_mesa = 10000

        # 3. Sai sem jogar nada
        self.assertTrue(self.gerenciador.creditar_bankroll(stack_mesa, "Você"))
        self.assertEqual(self.gerenciador.obter_perfil("Você")["bankroll"], 100000)

        # 4. Entra com 10k e perde tudo
        self.assertTrue(self.gerenciador.debitar_bankroll(10000, "Você"))
        self.assertEqual(self.gerenciador.obter_perfil("Você")["bankroll"], 90000)
        stack_mesa = 0

        # 5. Faz rebuy de 10k
        self.assertTrue(self.gerenciador.debitar_bankroll(10000, "Você"))
        self.assertEqual(self.gerenciador.obter_perfil("Você")["bankroll"], 80000)
        stack_mesa = 10000

        # 6. Ganha all-in na mesa e fica com 50k
        stack_mesa = 50000

        # 7. Sai da mesa: 80k + 50k = 130k
        self.assertTrue(self.gerenciador.creditar_bankroll(stack_mesa, "Você"))
        self.assertEqual(self.gerenciador.obter_perfil("Você")["bankroll"], 130000)

    def test_registrar_maos_e_vitorias(self):
        self.gerenciador.registrar_mao_jogada(venceu=False, nome="Você")
        self.gerenciador.registrar_mao_jogada(venceu=True, nome="Você")
        self.gerenciador.registrar_mao_jogada(venceu=True, nome="Você")

        perfil = self.gerenciador.obter_perfil("Você")
        self.assertEqual(perfil["maos_jogadas"], 3)
        self.assertEqual(perfil["vitorias"], 2)

    def test_conservacao_economica_entrada_saida_mesa(self):
        """
        Garante a lei de conservação de fichas:
        Bankroll inicial == Bankroll restante + Fichas na mesa.
        Ao sair da mesa com lucro ou prejuízo, a soma bate perfeitamente.
        """
        bankroll_inicial = self.gerenciador.obter_perfil("Você")["bankroll"]
        buy_in_mesa = 1500

        # Jogador entra na mesa
        self.assertTrue(self.gerenciador.debitar_bankroll(buy_in_mesa, "Você"))
        stack_mesa = buy_in_mesa
        bankroll_atual = self.gerenciador.obter_perfil("Você")["bankroll"]

        # Invariante durante o jogo:
        self.assertEqual(bankroll_atual + stack_mesa, bankroll_inicial)

        # Jogador ganha um pote na mesa (+500)
        stack_mesa += 500

        # Jogador decide sair da mesa: devolve stack ao bankroll
        self.assertTrue(self.gerenciador.creditar_bankroll(stack_mesa, "Você"))
        bankroll_final = self.gerenciador.obter_perfil("Você")["bankroll"]

        self.assertEqual(bankroll_final, bankroll_inicial + 500)

if __name__ == '__main__':
    unittest.main()

