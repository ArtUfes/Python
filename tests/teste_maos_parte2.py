import unittest
from core.carta import Carta
from core.jogador import Jogador
from core.avaliador_de_maos import AvaliadorDeMaos

ESP, COP, OUR, PAU = '♠️', '♥️', '♦️', '♣️'

class TestesAvaliadorPokerParte2(unittest.TestCase):

    def simular_rodada(self, cartas_mesa, cartas_j1, cartas_j2):
        j1 = Jogador("J1")
        j1.mao = sorted(cartas_mesa + cartas_j1, key=lambda c: c.valor, reverse=True)
        j1.classificacao_mao = AvaliadorDeMaos.avalia_mao(j1.mao)

        j2 = Jogador("J2")
        j2.mao = sorted(cartas_mesa + cartas_j2, key=lambda c: c.valor, reverse=True)
        j2.classificacao_mao = AvaliadorDeMaos.avalia_mao(j2.mao)

        jogadores = [j1, j2]
        melhor_class = max(j.classificacao_mao for j in jogadores)
        empatados = [j for j in jogadores if j.classificacao_mao == melhor_class]

        AvaliadorDeMaos.encontra_melhor_mao_jogadores(empatados)

        print(f"\n[MESA]: ", end="")
        for c in cartas_mesa: print(c.retornar_carta(), end=" ")
        print()
        for j in empatados:
            print(f"   -> {j.nome} ({AvaliadorDeMaos.imprimir_mao(j.classificacao_mao)}): ", end="")
            for c in j.melhor_mao: print(c.retornar_carta(), end=" ")
            print()

        if len(empatados) > 1:
            return AvaliadorDeMaos.encontra_ganhadores_desempate(empatados)
        return empatados

    # ==========================================
    # 6. TESTES DE FLUSH
    # ==========================================
    def test_flush_com_6_cartas_do_mesmo_naipe(self):
        # Caso: Mesa tem 4 copas, J1 tem 2 copas (Total 6 copas). O programa tem que pegar as 5 maiores!
        mesa = [Carta(2, COP), Carta(5, COP), Carta(8, COP), Carta(10, COP), Carta(13, ESP)]
        j1 = [Carta(14, COP), Carta(4, COP)] # Flush de A, 10, 8, 5, 4 (Ignora o 2)
        j2 = [Carta(11, COP), Carta(3, PAU)] # Flush de J, 10, 8, 5, 2
        vencedores = self.simular_rodada(mesa, j1, j2)
        
        self.assertEqual(len(vencedores), 1)
        self.assertEqual(vencedores[0].nome, "J1", "J1 ganha pelo Flush mais alto (Ás)")
        # Confirma se o programa ignorou o 2 de copas do J1 (tamanho tem que ser exatos 5)
        self.assertEqual(len(vencedores[0].melhor_mao), 5)

    # ==========================================
    # 7. TESTES DE FULL HOUSE
    # ==========================================
    def test_full_house_desempate_pelo_par(self):
        # Caso: Os dois têm o mesmo Trio, mas o par desempata
        mesa = [Carta(8, ESP), Carta(8, OUR), Carta(8, PAU), Carta(5, COP), Carta(2, ESP)]
        j1 = [Carta(14, PAU), Carta(14, COP)] # Full House de 8 com par de Ás
        j2 = [Carta(13, OUR), Carta(13, ESP)] # Full House de 8 com par de K
        vencedores = self.simular_rodada(mesa, j1, j2)
        self.assertEqual(vencedores[0].nome, "J1", "J1 tem o par de Ás, ganha do par de K")

    def test_full_house_pesadelo_dois_trios(self):
        # Caso Pesadelo: Um jogador consegue DOIS TRIOS. O menor vira par.
        mesa = [Carta(7, ESP), Carta(7, OUR), Carta(4, PAU), Carta(4, COP), Carta(4, ESP)]
        j1 = [Carta(7, PAU), Carta(14, COP)] # Trinca de 4 e Trinca de 7 (A mão dele é 7-7-7-4-4)
        j2 = [Carta(5, OUR), Carta(5, ESP)]  # Full House 4-4-4-5-5
        vencedores = self.simular_rodada(mesa, j1, j2)
        self.assertEqual(vencedores[0].nome, "J1", "J1 ganha com Full House 77744 contra 44455")

    # ==========================================
    # 8. TESTES DE QUADRA
    # ==========================================
    def test_quadra_comunitaria_kicker(self):
        # Caso: Quadra na mesa, quem tiver a maior carta na mão leva
        mesa = [Carta(6, ESP), Carta(6, OUR), Carta(6, PAU), Carta(6, COP), Carta(9, ESP)]
        j1 = [Carta(14, PAU), Carta(2, COP)] # Quadra com kicker Ás
        j2 = [Carta(13, OUR), Carta(12, ESP)] # Quadra com kicker K
        vencedores = self.simular_rodada(mesa, j1, j2)
        self.assertEqual(vencedores[0].nome, "J1", "J1 ganha com Kicker Ás")

    # ==========================================
    # 9 e 10. TESTES DE STRAIGHT E ROYAL FLUSH
    # ==========================================
    def test_straight_flush_maior_vence(self):
        # Caso raríssimo: Straight flush contra Straight flush menor
        mesa = [Carta(5, ESP), Carta(6, ESP), Carta(7, ESP), Carta(8, ESP), Carta(2, COP)]
        j1 = [Carta(9, ESP), Carta(10, ESP)] # 6 a 10 de espadas
        j2 = [Carta(4, ESP), Carta(3, ESP)]  # 4 a 8 de espadas
        vencedores = self.simular_rodada(mesa, j1, j2)
        self.assertEqual(vencedores[0].nome, "J1", "J1 ganha com SF até o 10")

    def test_royal_flush_split_pot(self):
        # Caso que consertamos antes: O pote TEM que ser dividido e retornar a lista intacta
        mesa = [Carta(10, COP), Carta(11, COP), Carta(12, COP), Carta(13, COP), Carta(14, COP)]
        j1 = [Carta(2, ESP), Carta(3, PAU)]
        j2 = [Carta(4, OUR), Carta(5, PAU)]
        vencedores = self.simular_rodada(mesa, j1, j2)
        self.assertEqual(len(vencedores), 2, "A mesa é Royal Flush. Ambos dividem o pote!")

if __name__ == '__main__':
    unittest.main(verbosity=2)