from carta import Carta
from random import randint

class Baralho:
    def __init__(self):
        self.cartas = self.inicia_cartas()
        self.cartas_ja_sorteadas = [] # Armazena o idx da carta sorteada na lista de cartas
    
    def inicia_cartas(self):
        cartas = []
        for i in range(1, 5):
            for j in range(2, 15):
                if i == 1:
                    cartas.append(Carta(j, '♠️'))
                elif i == 2:
                    cartas.append(Carta(j, '♦️'))
                elif i == 3:
                    cartas.append(Carta(j, '♣️'))
                elif i == 4:
                    cartas.append(Carta(j, '♥️'))
        return cartas
    
    def imprimir_baralho(self):
        for i in range(0, len(self.cartas)):
            self.cartas[i].imprimir_carta()
            if (i + 1) % 13 == 0:
                print()
    
    def sorteia_uma_carta(self):
        while True:
            i = randint(0, 51) # Sorteia um número entre 0 e 51
            if i not in self.cartas_ja_sorteadas:
                self.cartas_ja_sorteadas.append(i) # Adiciona o idx da carta sorteada na lista de cartas ja sorteadas
                break
        return self.cartas[i] # Retorna a carta sorteada
    
    def sorteia_uma_carta_idx(self):
        while True:
            i = randint(0, 51) # Sorteia um número entre 0 e 51
            if i not in self.cartas_ja_sorteadas:
                self.cartas_ja_sorteadas.append(i) # Adiciona o idx da carta sorteada na lista de cartas ja sorteadas
                break
        return i # Retorna o idx da carta sorteada

        
    
    def reseta_baralho(self):
        self.cartas_ja_sorteadas.clear()