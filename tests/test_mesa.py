import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.mesa import Mesa
from core.jogador import Jogador
from core.carta import Carta

class TestMesa(unittest.TestCase):
    
    def test_fluxo_simples(self):
        mesa = Mesa(small_blind=10, big_blind=20)
        j1 = Jogador("Alice", stack=1000)
        j2 = Jogador("Bob", stack=1000)
        
        mesa.adiciona_jogador(j1)
        mesa.adiciona_jogador(j2)
        
        mesa.iniciar_mao()
        self.assertEqual(mesa.estado_atual, "PRE_FLOP")
        self.assertEqual(len(mesa.cartas_na_mesa), 0)
        
        mesa.avancar_rodada()
        self.assertEqual(mesa.estado_atual, "FLOP")
        self.assertEqual(len(mesa.cartas_na_mesa), 3)
        
        mesa.avancar_rodada()
        self.assertEqual(mesa.estado_atual, "TURN")
        self.assertEqual(len(mesa.cartas_na_mesa), 4)
        
        mesa.avancar_rodada()
        self.assertEqual(mesa.estado_atual, "RIVER")
        self.assertEqual(len(mesa.cartas_na_mesa), 5)
        
        mesa.avancar_rodada()
        self.assertEqual(mesa.estado_atual, "SHOWDOWN")
        
        mesa.executar_showdown()
        # Após o showdown, ninguém perdeu dinheiro pro nada, a soma deve ser 2000
        self.assertEqual(j1.stack + j2.stack, 2000)

    def test_acao_fold(self):
        mesa = Mesa(small_blind=10, big_blind=20)
        j1 = Jogador("P1", stack=500)
        j2 = Jogador("P2", stack=500)
        mesa.adiciona_jogador(j1)
        mesa.adiciona_jogador(j2)
        
        mesa.iniciar_mao()
        
        mesa.processar_acao("P1", "FOLD")
        self.assertFalse(j1.ativo)
        
        # P1 foldou. Forçar as 5 cartas para o avaliador funcionar.
        mesa.cartas_na_mesa = [Carta(2,'♥️'),Carta(3,'♥️'),Carta(4,'♥️'),Carta(5,'♥️'),Carta(7,'♥️')]
        mesa.estado_atual = "SHOWDOWN"
        mesa.executar_showdown()
        
        # P2 ganha por W.O essencialmente (P1 está inativo e nao entra no ranking)
        self.assertEqual(j1.stack + j2.stack, 1000)
        self.assertTrue(j2.stack > 500)

if __name__ == '__main__':
    unittest.main()
