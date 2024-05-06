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
    
    @staticmethod
    def cria_set_cartas_pelo_valor(cartas):
        set_cartas = set()
        for carta in cartas:
            valor_igual = False
            if len(set_cartas) == 0:
                set_cartas.add(carta)
            else:
                for carta_set in set_cartas:
                    if carta_set.valor == carta.valor:
                        valor_igual = True
                        break
                if valor_igual == False:
                    set_cartas.add(carta)
        return set_cartas