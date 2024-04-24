class Carta:
    def __init__(self, valor, naipe):
        self.valor = valor
        self.naipe = naipe
        self.simbolo = self.calcula_simbolo()

    def imprimir_carta(self):
        if self.naipe == '♠️' or self.naipe == '♣️':
            print(f'[\033[30m{self.simbolo}{self.naipe}\033[0m]', end='')
        elif self.naipe == '♥️' or self.naipe == '♦️':
            print(f'[\033[31m{self.simbolo}{self.naipe}\033[0m]', end='')
    
    def retornar_carta(self):
        if self.naipe == '♠️' or self.naipe == '♣️':
            return (f'[\033[30m{self.simbolo}{self.naipe}\033[0m]')
        elif self.naipe == '♥️' or self.naipe == '♦️':
            return (f'[\033[31m{self.simbolo}{self.naipe}\033[0m]')
    
    def calcula_simbolo(self):
        if self.valor == 14:
            return 'A'
        elif self.valor == 13:
            return 'K'
        elif self.valor == 12:
            return 'Q'
        elif self.valor == 11:
            return 'J'
        else:
            return self.valor