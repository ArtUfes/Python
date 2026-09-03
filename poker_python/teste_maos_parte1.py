import unittest
from carta import Carta
from jogador import Jogador
from avaliador_de_maos import AvaliadorDeMaos

# Atalhos para os naipes para deixar os testes mais fáceis de ler
ESP = '♠️'
COP = '♥️'
OUR = '♦️'
PAU = '♣️'

class TestesAvaliadorPokerParte1(unittest.TestCase):

    def simular_rodada(self, cartas_mesa, cartas_j1, cartas_j2):
        """
        Função Helper: Simula o pipeline exato do seu arquivo poker.py
        """
        j1 = Jogador("J1")
        # CORREÇÃO: Agora estamos ordenando as cartas igual no seu mesa.py!
        j1.mao = sorted(cartas_mesa + cartas_j1, key=lambda c: c.valor, reverse=True)
        j1.classificacao_mao = AvaliadorDeMaos.avalia_mao(j1.mao)

        j2 = Jogador("J2")
        # CORREÇÃO: Ordenando aqui também!
        j2.mao = sorted(cartas_mesa + cartas_j2, key=lambda c: c.valor, reverse=True)
        j2.classificacao_mao = AvaliadorDeMaos.avalia_mao(j2.mao)

        jogadores = [j1, j2]

        # 1. Filtra apenas os jogadores com a maior classificação de mão
        melhor_class = max(j.classificacao_mao for j in jogadores)
        empatados = [j for j in jogadores if j.classificacao_mao == melhor_class]

        # 2. Monta a melhor combinação de 5 cartas para os empatados
        AvaliadorDeMaos.encontra_melhor_mao_jogadores(empatados)

        # ==========================================
        # VISUALIZADOR DOS BASTIDORES
        # ==========================================
        print(f"\n[MESA]: ", end="")
        for c in cartas_mesa: print(c.retornar_carta(), end=" ")
        print()
        
        for j in empatados:
            print(f"   -> Melhor mão escolhida para {j.nome}: ", end="")
            for c in j.melhor_mao:
                print(c.retornar_carta(), end=" ")
            print()
        # ==========================================

        # 3. Resolve o desempate
        if len(empatados) > 1:
            return AvaliadorDeMaos.encontra_ganhadores_desempate(empatados)
        return empatados

    # ==========================================
    # 1. TESTES DE CARTA ALTA (High Card)
    # ==========================================
    def test_carta_alta_desempate_na_terceira_carta(self):
        # Caso Pesadelo: As duas maiores cartas e a mesa são iguais, o desempate vai longe
        mesa = [Carta(13, ESP), Carta(8, OUR), Carta(7, PAU), Carta(5, COP), Carta(2, ESP)]
        j1 = [Carta(14, PAU), Carta(9, COP)] # Melhor mão: A, K, 9, 8, 7
        j2 = [Carta(14, OUR), Carta(6, ESP)] # Melhor mão: A, K, 8, 7, 6
        
        vencedores = self.simular_rodada(mesa, j1, j2)
        
        self.assertEqual(len(vencedores), 1)
        self.assertEqual(vencedores[0].nome, "J1", "J1 deveria ganhar com o Kicker 9 contra o 6")

    # ==========================================
    # 2. TESTES DE PAR (Pair)
    # ==========================================
    def test_par_falsificado_na_mesa(self):
        # Caso Pesadelo: A mesa tem um par alto, invalidando cartas médias da mão
        mesa = [Carta(13, ESP), Carta(13, OUR), Carta(8, PAU), Carta(7, COP), Carta(5, ESP)]
        j1 = [Carta(14, PAU), Carta(2, COP)] # Joga o par da mesa com Kicker Ás (K, K, A, 8, 7)
        j2 = [Carta(12, OUR), Carta(11, ESP)] # Joga o par da mesa com Kicker Dama (K, K, Q, J, 8)
        
        vencedores = self.simular_rodada(mesa, j1, j2)
        
        self.assertEqual(len(vencedores), 1)
        self.assertEqual(vencedores[0].nome, "J1", "J1 tem o Ás, deveria vencer mesmo J2 tendo Q e J")

    # ==========================================
    # 3. TESTES DE DOIS PARES (Two Pair)
    # ==========================================
    def test_dois_pares_counterfeit(self):
        # O MAIOR CASO PESADELO DO POKER: Dois Pares Counterfeitados (Falsificados)
        mesa = [Carta(10, ESP), Carta(10, OUR), Carta(8, PAU), Carta(8, COP), Carta(13, ESP)]
        j1 = [Carta(5, PAU), Carta(5, COP)] # Tem par de 5 na mão, mas a mesa tem 10 e 8. Os 5 morrem!
        j2 = [Carta(14, OUR), Carta(2, ESP)] # Não tem nada, mas joga a mesa e usa o Ás de Kicker
        
        # J1 Melhor Mão: 10, 10, 8, 8, K (O par de 5 foi engolido pela mesa)
        # J2 Melhor Mão: 10, 10, 8, 8, A
        
        vencedores = self.simular_rodada(mesa, j1, j2)
        
        self.assertEqual(len(vencedores), 1)
        self.assertEqual(vencedores[0].nome, "J2", "J2 deveria ganhar usando o Ás de kicker contra o K da mesa")

    # ==========================================
    # 4. TESTES DE TRIO (Three of a Kind)
    # ==========================================
    def test_trio_na_mesa_decidido_pelo_kicker(self):
        # Caso: Trinca comunitária, quem tem a carta mais alta na mão leva
        mesa = [Carta(7, ESP), Carta(7, OUR), Carta(7, PAU), Carta(13, COP), Carta(2, ESP)]
        j1 = [Carta(14, PAU), Carta(3, COP)] # 7, 7, 7, A, K
        j2 = [Carta(12, OUR), Carta(11, ESP)] # 7, 7, 7, K, Q
        
        vencedores = self.simular_rodada(mesa, j1, j2)
        
        self.assertEqual(len(vencedores), 1)
        self.assertEqual(vencedores[0].nome, "J1", "J1 ganha com o Kicker Ás")

    # ==========================================
    # 5. TESTES DE SEQUÊNCIA (Straight)
    # ==========================================
    def test_sequencia_wheel_contra_normal(self):
        # Caso Pesadelo: O Ás valendo '1' (A-2-3-4-5) contra uma sequência maior (2-3-4-5-6)
        mesa = [Carta(2, ESP), Carta(3, OUR), Carta(4, PAU), Carta(5, COP), Carta(11, ESP)]
        j1 = [Carta(14, PAU), Carta(13, COP)] # A-2-3-4-5 (Straight altura 5)
        j2 = [Carta(6, OUR), Carta(7, ESP)]   # 2-3-4-5-6 (Straight altura 6)
        
        vencedores = self.simular_rodada(mesa, j1, j2)
        
        self.assertEqual(len(vencedores), 1)
        self.assertEqual(vencedores[0].nome, "J2", "J2 tem uma sequência altura 6, ganha da Wheel (A-5)")

    def test_sequencia_jogando_a_mesa_empate(self):
        # Caso: A maior sequência já está na mesa, as cartas da mão são inúteis
        mesa = [Carta(6, ESP), Carta(7, OUR), Carta(8, PAU), Carta(9, COP), Carta(10, ESP)]
        j1 = [Carta(14, PAU), Carta(2, COP)]
        j2 = [Carta(3, OUR), Carta(4, ESP)]
        
        vencedores = self.simular_rodada(mesa, j1, j2)
        
        self.assertEqual(len(vencedores), 2, "Deveria ser um empate, pois ambos jogam a mesa (6-10)")

    def test_sequencia_maior_escondida(self):
        # Caso: J1 tem uma sequência alta misturada, J2 tem uma sequência óbvia mas menor
        mesa = [Carta(5, ESP), Carta(6, OUR), Carta(7, PAU), Carta(8, COP), Carta(2, ESP)]
        j1 = [Carta(4, PAU), Carta(9, COP)] # 5-6-7-8-9
        j2 = [Carta(4, OUR), Carta(4, ESP)] # 4-5-6-7-8
        
        vencedores = self.simular_rodada(mesa, j1, j2)
        
        self.assertEqual(len(vencedores), 1)
        self.assertEqual(vencedores[0].nome, "J1", "J1 deve vencer com o 9 fechando a sequência maior")
    
    def test_empate_absoluto_split_pot(self):
        # Caso: Empate total. As 5 melhores cartas de ambos são idênticas.
        mesa = [Carta(14, ESP), Carta(10, OUR), Carta(8, PAU), Carta(5, COP), Carta(2, ESP)]
        j1 = [Carta(13, PAU), Carta(4, COP)] # Kicker K
        j2 = [Carta(13, OUR), Carta(3, ESP)] # Kicker K também! (Os kickers 4 e 3 são ignorados)
        vencedores = self.simular_rodada(mesa, j1, j2)
        self.assertEqual(len(vencedores), 2, "Deveria ser empate (Split Pot), as 5 cartas são iguais")

    def test_trio_set_over_set(self):
        # Caso: Trinca vs Trinca (Mãos diferentes)
        mesa = [Carta(10, ESP), Carta(5, OUR), Carta(2, PAU), Carta(13, COP), Carta(8, ESP)]
        j1 = [Carta(10, PAU), Carta(10, COP)] # Trinca de 10
        j2 = [Carta(5, ESP), Carta(5, PAU)]   # Trinca de 5
        vencedores = self.simular_rodada(mesa, j1, j2)
        self.assertEqual(vencedores[0].nome, "J1", "Trinca de 10 ganha da trinca de 5")

    def test_dois_pares_maior_par_vence(self):
        # Caso: O primeiro par define o vencedor, ignorando o segundo par
        mesa = [Carta(2, ESP), Carta(3, OUR), Carta(8, PAU), Carta(13, COP), Carta(7, ESP)]
        j1 = [Carta(14, PAU), Carta(14, COP)] # Par de A (Dois pares: AA-88 usando a mesa? Não, só AA)
        j2 = [Carta(13, ESP), Carta(8, COP)]  # Dois pares: KK-88
        # Opa, pegadinha: J1 tem SÓ UM PAR (AA). J2 tem DOIS PARES (KK-88). 
        # Como Dois Pares > Par, J2 deve vencer!
        vencedores = self.simular_rodada(mesa, j1, j2)
        self.assertEqual(vencedores[0].nome, "J2", "J2 tem Dois Pares, ganha do Par de Ás do J1")

if __name__ == '__main__':
    # Roda os testes com detalhes (verbosity=2)
    unittest.main(verbosity=2)