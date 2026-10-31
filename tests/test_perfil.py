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
        self.assertEqual(perfil["bankroll"], 10000)
        self.assertEqual(perfil["maos_jogadas"], 0)
        self.assertEqual(perfil["vitorias"], 0)

    def test_debitar_bankroll_sucesso_e_insuficiente(self):
        # Débito válido
        sucesso = self.gerenciador.debitar_bankroll(2000, "Você")
        self.assertTrue(sucesso)
        perfil = self.gerenciador.obter_perfil("Você")
        self.assertEqual(perfil["bankroll"], 8000)

        # Tentativa de debitar mais do que possui
        falha = self.gerenciador.debitar_bankroll(9000, "Você")
        self.assertFalse(falha)
        perfil = self.gerenciador.obter_perfil("Você")
        self.assertEqual(perfil["bankroll"], 8000, "Bankroll não deve mudar em caso de falha")

        # Tentativa de débito com valor inválido
        invalido = self.gerenciador.debitar_bankroll(-500, "Você")
        self.assertFalse(invalido)

    def test_creditar_bankroll(self):
        sucesso = self.gerenciador.creditar_bankroll(1500, "Você")
        self.assertTrue(sucesso)
        perfil = self.gerenciador.obter_perfil("Você")
        self.assertEqual(perfil["bankroll"], 11500)

        invalido = self.gerenciador.creditar_bankroll(-100, "Você")
        self.assertFalse(invalido)

    def test_recarregar_fichas(self):
        # Recarga padrão de 10.000
        perfil = self.gerenciador.recarregar_fichas(10000, "Você")
        self.assertEqual(perfil["bankroll"], 20000)
        self.assertIsNotNone(perfil["ultimo_resgate_bonus"])

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
        bankroll_inicial = 10000
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

