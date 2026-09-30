import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.pote import GerenciadorDePote

class TestPote(unittest.TestCase):
    
    def test_pote_simples(self):
        gerenciador = GerenciadorDePote()
        apostas = {"A": 100, "B": 100, "C": 100}
        ativos = {"A", "B", "C"}
        
        gerenciador.processar_rodada(apostas, ativos)
        
        self.assertEqual(len(gerenciador.potes), 1)
        self.assertEqual(gerenciador.potes[0].valor, 300)
        
        ranking = [["A"], ["B"], ["C"]]
        pagamentos = gerenciador.distribuir(ranking)
        
        self.assertEqual(pagamentos.get("A"), 300)
        self.assertIsNone(pagamentos.get("B"))

    def test_split_pot_com_fichas_impares(self):
        gerenciador = GerenciadorDePote()
        # Num cenário real: C apostou 1 e foldou para um raise de 10.
        apostas = {"A": 10, "B": 10, "C": 1} 
        ativos = {"A", "B"} # C não está ativo
        
        gerenciador.processar_rodada(apostas, ativos)
        
        self.assertEqual(gerenciador.potes[0].valor, 3)
        self.assertEqual(gerenciador.potes[1].valor, 18)
        
        # A e B empatam
        ranking = [["A", "B"]]
        pagamentos = gerenciador.distribuir(ranking)
        
        # 21 dividido por 2 = 10 para cada e sobra 1 ficha.
        # A sobra vai para o primeiro da lista (no caso, A).
        self.assertEqual(pagamentos.get("A"), 11)
        self.assertEqual(pagamentos.get("B"), 10)

    def test_side_pot_cenario_complexo(self):
        # Cenário:
        # A tem 100 (All-in)
        # B tem 200 (All-in)
        # C tem 300 (Cobre os dois)
        gerenciador = GerenciadorDePote()
        apostas = {"A": 100, "B": 200, "C": 300}
        ativos = {"A", "B", "C"}
        
        gerenciador.processar_rodada(apostas, ativos)
        
        # Cria Main Pot + 2 Side Pots (sendo 1 de "refund" para o C)
        self.assertEqual(len(gerenciador.potes), 3)
        
        # Pote 0 (Main): A, B, C colaboram com 100 cada. Valor = 300.
        self.assertEqual(gerenciador.potes[0].valor, 300)
        self.assertTrue("A" in gerenciador.potes[0].jogadores_elegiveis)
        
        # Pote 1 (Side): B e C colaboram com os 100 excedentes. Valor = 200.
        self.assertEqual(gerenciador.potes[1].valor, 200)
        self.assertFalse("A" in gerenciador.potes[1].jogadores_elegiveis)
        
        # Pote 2 (Side/Refund): C colabora com o resto (100). Valor = 100.
        self.assertEqual(gerenciador.potes[2].valor, 100)
        self.assertFalse("B" in gerenciador.potes[2].jogadores_elegiveis)
        
        # Simulação: A tem a melhor mão de todos. B é o segundo.
        ranking = [["A"], ["B"], ["C"]]
        pagamentos = gerenciador.distribuir(ranking)
        
        # A ganha Pote 0 (300).
        # B ganha Pote 1 (200) porque A não é elegível para este pote.
        # C ganha Pote 2 (100) porque é o único elegível e recebe de volta.
        self.assertEqual(pagamentos.get("A"), 300)
        self.assertEqual(pagamentos.get("B"), 200)
        self.assertEqual(pagamentos.get("C"), 100)

if __name__ == '__main__':
    unittest.main()
