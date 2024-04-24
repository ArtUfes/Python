from carta import Carta

class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.cartas = []
        self.mao = []
        self.classificacao_mao = 0
        self.maior_valor = 0
    
    def sorteia_cartas_jogador(self, baralho):
        for i in range(0, 2):
            self.cartas.append(baralho.sorteia_uma_carta())
    
    def imprimir_jogador(self):
        print(f'{self.nome}')
        for c in self.cartas:
            c.imprimir_carta()

    def reseta_cartas_jogador(self):
        self.cartas.clear()