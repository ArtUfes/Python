import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.carta import Carta
from core.gravador_historico import GravadorHistorico

class TestGravadorHistorico(unittest.TestCase):
    def test_all_in_preflop_exibe_streets_do_board(self):
        # Simula gravador em banco temporario em memoria
        gravador = GravadorHistorico(db_path=":memory:")
        
        dados_mao = {
            'hand_id': 1792207726,
            'small_blind': 10,
            'big_blind': 20,
            'posicao_button': 3,
            'small_blind_player': 'ProBot_3',
            'big_blind_player': 'Você',
            'jogadores': [
                {'nome': 'Você', 'stack_inicial': 1298, 'cartas': [Carta('7', '♦️'), Carta('2', '♦️')], 'chegou_showdown': True, 'desc_mao': 'Par'},
                {'nome': 'ProBot_1', 'stack_inicial': 2482, 'cartas': [Carta('K', '♠️'), Carta('9', '♠️')], 'chegou_showdown': False},
                {'nome': 'ProBot_2', 'stack_inicial': 174, 'cartas': [Carta('A', '♦️'), Carta('A', '♣️')], 'chegou_showdown': True, 'desc_mao': 'Par'},
                {'nome': 'ProBot_3', 'stack_inicial': 2046, 'cartas': [Carta('3', '♣️'), Carta('5', '♠️')], 'chegou_showdown': False}
            ],
            'cartas_comunitarias': [
                Carta('Q', '♦️'), Carta('4', '♥️'), Carta('2', '♥️'),
                Carta('J', '♣️'), Carta('8', '♥️')
            ],
            'acoes': [
                {'rodada': 'PRE_FLOP', 'jogador': 'ProBot_1', 'acao': 'raise', 'valor': 41},
                {'rodada': 'PRE_FLOP', 'jogador': 'ProBot_2', 'acao': 'raise', 'valor': 137},
                {'rodada': 'PRE_FLOP', 'jogador': 'ProBot_3', 'acao': 'fold', 'valor': 0},
                {'rodada': 'PRE_FLOP', 'jogador': 'Você', 'acao': 'raise', 'valor': 1274},
                {'rodada': 'PRE_FLOP', 'jogador': 'ProBot_1', 'acao': 'fold', 'valor': 0},
                {'rodada': 'PRE_FLOP', 'jogador': 'ProBot_2', 'acao': 'call', 'valor': 37}
            ],
            'showdown': True,
            'vencedores': [
                {'nome': 'ProBot_2', 'valor': 399, 'descricao_mao': 'Par', 'cartas': [Carta('A', '♦️'), Carta('A', '♣️')]},
                {'nome': 'Você', 'valor': 1100, 'descricao_mao': 'Par', 'cartas': [Carta('7', '♦️'), Carta('2', '♦️')]}
            ],
            'pote_total': 1499,
            'rake': 0,
            'resultados_jogadores': [
                {'nome': 'Você', 'lucro_liquido': -174},
                {'nome': 'ProBot_1', 'lucro_liquido': -41},
                {'nome': 'ProBot_2', 'lucro_liquido': 225},
                {'nome': 'ProBot_3', 'lucro_liquido': -10}
            ]
        }

        texto = gravador.gerar_hand_history_text(dados_mao)

        # Valida que as seções de cada street foram geradas mesmo sem apostas pós-flop
        self.assertIn("*** FLOP *** [Qd 4h 2h]", texto)
        self.assertIn("*** TURN *** [Qd 4h 2h] [Jc]", texto)
        self.assertIn("*** RIVER *** [Qd 4h 2h Jc] [8h]", texto)
        self.assertIn("Board [Qd 4h 2h Jc 8h]", texto)
        self.assertIn("*** SHOWDOWN ***", texto)

    def test_todos_foldam_sem_showdown(self):
        gravador = GravadorHistorico(db_path=":memory:")
        
        dados_mao = {
            'hand_id': 1792363749,
            'small_blind': 10,
            'big_blind': 20,
            'posicao_button': 0,
            'small_blind_player': 'Você',
            'big_blind_player': 'ProBot_1',
            'jogadores': [
                {'nome': 'Você', 'stack_inicial': 720, 'cartas': [Carta('A', '♥️'), Carta('K', '♦️')], 'chegou_showdown': False, 'lucro_liquido': -10},
                {'nome': 'ProBot_1', 'stack_inicial': 3314, 'cartas': [Carta('8', '♦️'), Carta('4', '♥️')], 'chegou_showdown': True, 'lucro_liquido': 10},
                {'nome': 'ProBot_2', 'stack_inicial': 3946, 'cartas': [Carta('2', '♣️'), Carta('7', '♠️')], 'chegou_showdown': False, 'lucro_liquido': 0},
                {'nome': 'ProBot_3', 'stack_inicial': 1020, 'cartas': [Carta('9', '♠️'), Carta('3', '♦️')], 'chegou_showdown': False, 'lucro_liquido': 0}
            ],
            'cartas_comunitarias': [],
            'acoes': [
                {'rodada': 'PRE_FLOP', 'jogador': 'ProBot_2', 'acao': 'fold', 'valor': 0},
                {'rodada': 'PRE_FLOP', 'jogador': 'ProBot_3', 'acao': 'fold', 'valor': 0},
                {'rodada': 'PRE_FLOP', 'jogador': 'Você', 'acao': 'fold', 'valor': 0}
            ],
            'showdown': False,
            'vencedores_detalhe': [
                {'nome': 'ProBot_1', 'valor': 30}
            ],
            'pote_total': 30,
            'rake': 0
        }

        texto = gravador.gerar_hand_history_text(dados_mao)

        # Não deve haver showdown nem revelação de cartas quando todos foldam
        self.assertNotIn("*** SHOWDOWN ***", texto)
        self.assertNotIn("shows", texto)
        self.assertNotIn("()", texto)
        self.assertNotIn("Dealt to Você []", texto)
        self.assertIn("Dealt to Você [Ah Kd]", texto)
        self.assertIn("ProBot_1 collected $30 from pot", texto)

if __name__ == '__main__':
    unittest.main()
