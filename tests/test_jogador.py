import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.jogador import Jogador
from core.carta import Carta

class TestJogador(unittest.TestCase):
    def test_inicializacao(self):
        j = Jogador("Alice", stack=1000)
        self.assertEqual(j.nome, "Alice")
        self.assertEqual(j.stack, 1000)
        self.assertEqual(j.aposta_atual, 0)
        self.assertTrue(j.ativo)
        self.assertFalse(j.is_all_in)

    def test_apostar_normal(self):
        j = Jogador("Bob", stack=500)
        valor_apostado = j.apostar(100)
        self.assertEqual(valor_apostado, 100)
        self.assertEqual(j.stack, 400)
        self.assertEqual(j.aposta_atual, 100)
        self.assertFalse(j.is_all_in)

    def test_apostar_all_in(self):
        j = Jogador("Charlie", stack=200)
        valor_apostado = j.apostar(300)
        self.assertEqual(valor_apostado, 200) # Ele só pode apostar o que tem
        self.assertEqual(j.stack, 0)
        self.assertEqual(j.aposta_atual, 200)
        self.assertTrue(j.is_all_in)

    def test_receber_fichas(self):
        j = Jogador("Dave", stack=100)
        j.receber_fichas(500)
        self.assertEqual(j.stack, 600)

    def test_foldar(self):
        j = Jogador("Eve", stack=1000)
        j.cartas.append(Carta(14, 'espadas'))
        j.foldar()
        self.assertFalse(j.ativo)
        self.assertEqual(len(j.cartas), 0)

    def test_preparar_nova_mao(self):
        j = Jogador("Frank", stack=50)
        j.aposta_atual = 50
        j.is_all_in = True
        j.cartas.append(Carta(14, 'espadas'))
        
        j.preparar_nova_mao()
        self.assertEqual(j.aposta_atual, 0)
        self.assertFalse(j.is_all_in)
        self.assertEqual(len(j.cartas), 0)
        self.assertTrue(j.ativo)
        
        # Testar se fica inativo caso stack = 0
        j2 = Jogador("Ghost", stack=0)
        j2.preparar_nova_mao()
        self.assertFalse(j2.ativo)

if __name__ == '__main__':
    unittest.main()
