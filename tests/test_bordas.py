import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.jogador import Jogador
from core.pote import GerenciadorDePote
from core.mesa import Mesa

class TestCasosDeBorda(unittest.TestCase):

    # --- BORDAS FASE 1: JOGADOR ---
    def test_jogador_aposta_negativa_ou_zero(self):
        j = Jogador("Trapaceiro", stack=100)
        # Tenta apostar valor negativo para ver se o stack aumenta (bug de criar dinheiro infinito)
        valor_apostado = j.apostar(-50)
        self.assertEqual(valor_apostado, 0)
        self.assertEqual(j.stack, 100) # Stack nao deve mudar

        # Tenta apostar 0
        valor_apostado2 = j.apostar(0)
        self.assertEqual(valor_apostado2, 0)
        self.assertEqual(j.stack, 100)

    # --- BORDAS FASE 2: POTE ---
    def test_pote_fichas_impares_multiplos_vencedores(self):
        # O pote tem 10 fichas e há 3 vencedores.
        # Eles empataram, entao cada um deveria ganhar 3, e sobra 1 ficha.
        # A ficha impar deve ir para o primeiro cara (A).
        gerenciador = GerenciadorDePote()
        
        # Forçamos o estado do pote para focar no teste matematico do distribuir()
        gerenciador.potes[0].valor = 10
        gerenciador.potes[0].jogadores_elegiveis = {"A", "B", "C"}
        
        # Simula que os tres jogadores tiverem exatamenta a mesma mao e empataram (ranking index 0)
        ranking = [["A", "B", "C"]]
        pagamentos = gerenciador.distribuir(ranking)
        
        # 10 / 3 = 3 pra cada, sobra 1. A sobra vai pro primeiro da lista ("A").
        self.assertEqual(pagamentos.get("A"), 4)
        self.assertEqual(pagamentos.get("B"), 3)
        self.assertEqual(pagamentos.get("C"), 3)

    # --- BORDAS FASE 3: MESA ---
    def test_mesa_raise_invalido(self):
        mesa = Mesa(small_blind=10, big_blind=20)
        mesa.adiciona_jogador(Jogador("A", stack=1000))
        mesa.adiciona_jogador(Jogador("B", stack=1000))
        mesa.iniciar_mao()
        
        # Aposta maior atual é 20 (do Big Blind)
        # O jogador "A" (Small Blind) tenta dar RAISE para 15 (menor que a aposta maxima atual)
        resultado = mesa.processar_acao("A", "RAISE", 15)
        
        # O motor deve rejeitar e retornar False
        self.assertFalse(resultado)
        
    def test_mesa_check_invalido(self):
        mesa = Mesa(small_blind=10, big_blind=20)
        mesa.adiciona_jogador(Jogador("A", stack=1000))
        mesa.adiciona_jogador(Jogador("B", stack=1000))
        mesa.iniciar_mao()
        
        nome_sb = "A" if mesa.apostas_rodada["A"] == 10 else "B"
        nome_bb = "B" if nome_sb == "A" else "A"
        
        # O jogador que pagou 10 (SB) não pode dar CHECK porque a maior aposta é 20
        resultado = mesa.processar_acao(nome_sb, "CHECK")
        self.assertFalse(resultado)
        
        # Ele da CALL
        mesa.processar_acao(nome_sb, "CALL")
        
        # Agora as apostas estão iguais. O BB pode dar CHECK.
        resultado_bb = mesa.processar_acao(nome_bb, "CHECK")
        self.assertTrue(resultado_bb)

if __name__ == '__main__':
    unittest.main()
