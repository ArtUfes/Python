from core.carta import Carta

class Jogador:
    def __init__(self, nome, stack=0):
        self.nome = nome
        self.stack = stack
        self.aposta_atual = 0
        self.ativo = True
        self.is_all_in = False
        self.cartas = [] # Contém as duas cartas que o jogador recebe em cada rodada
        self.mao = [] # Contém as cinco cartas da mesa e as duas cartas do jogador
        self.melhor_mao = [] # Contém as 5 cartas que resultam na melhor mão do jogador
        self.classificacao_mao = 0 # Armazena qual foi a classificação da mão do jogador (Par, Flush, etc.)
        self.maior_valor = 0  # Armazena o maior valor da carta da mão que o jogador tem. Por exemplo: se tem par de As, armazena o valor 14
    
    def sorteia_cartas_jogador(self, baralho):
        for i in range(0, 2):
            self.cartas.append(baralho.sorteia_uma_carta())
    
    def imprimir_jogador(self):
        print(f'{self.nome}')
        for c in self.cartas:
            c.imprimir_carta()

    def reseta_cartas_jogador(self):
        self.cartas.clear()
        self.classificacao_mao = 0
        self.mao.clear()
        self.melhor_mao.clear()
        self.maior_valor = 0

    def apostar(self, valor):
        if valor <= 0:
            return 0
            
        if valor >= self.stack:
            valor_real = self.stack
            self.is_all_in = True
        else:
            valor_real = valor
        
        self.stack -= valor_real
        self.aposta_atual += valor_real
        return valor_real

    def receber_fichas(self, valor):
        self.stack += valor

    def foldar(self):
        self.ativo = False
        self.reseta_cartas_jogador()

    def preparar_nova_mao(self):
        self.aposta_atual = 0
        self.is_all_in = False
        self.ativo = self.stack > 0
        self.reseta_cartas_jogador()