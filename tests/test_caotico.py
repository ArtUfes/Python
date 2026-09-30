import sys
import os
import random
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.mesa import Mesa
from core.jogador import Jogador
from core.carta import Carta

class TestCaotico(unittest.TestCase):
    
    def test_simulacao_aleatoria_conservacao_energia(self):
        # 9 jogadores começam com 1000 fichas cada = 9000 totais no ecossistema
        mesa = Mesa(small_blind=1, big_blind=2)
        nomes = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        fichas_iniciais = 1000
        total_fichas_no_jogo = len(nomes) * fichas_iniciais
        
        for n in nomes:
            mesa.adiciona_jogador(Jogador(n, stack=fichas_iniciais))
            
        acoes_possiveis = ["FOLD", "CALL", "RAISE", "CHECK"]
        
        for mao in range(5000000):
            mesa.iniciar_mao()
            
            for _ in range(4): # 4 rodadas de aposta (Pre-flop, Flop, Turn, River)
                if mesa.estado_atual == "SHOWDOWN":
                    break
                    
                # Apenas quem pode falar
                ativos = [j for j in mesa.jogadores if j.ativo and not j.is_all_in]
                
                for j in ativos:
                    # Verifica de novo se o estado mudou dentro do loop (alguem deu fold e causou W.O.)
                    if mesa.estado_atual == "SHOWDOWN":
                        break
                        
                    acao = random.choice(acoes_possiveis)
                    if acao == "RAISE":
                        valor = mesa.maior_aposta_rodada + random.randint(1, 100)
                        if not mesa.processar_acao(j.nome, acao, valor):
                            mesa.processar_acao(j.nome, "CALL")
                    else:
                        if not mesa.processar_acao(j.nome, acao):
                            mesa.processar_acao(j.nome, "CALL")
                            
                mesa.avancar_rodada()
                
            # Forçar cartas na mesa caso não tenham rolado todas
            while len(mesa.cartas_na_mesa) < 5:
                mesa.cartas_na_mesa.append(Carta(2, '♥️'))
            
            mesa.estado_atual = "SHOWDOWN"
            mesa.executar_showdown()
            
            # Verificacao matematica: Fichas nao podem sumir nem ser criadas
            fichas_atuais = sum(j.stack for j in mesa.jogadores)
            self.assertEqual(fichas_atuais, total_fichas_no_jogo, f"ECONOMIA QUEBRADA na mao {mao}! Tinha {total_fichas_no_jogo}, agora tem {fichas_atuais}")

if __name__ == '__main__':
    unittest.main()
