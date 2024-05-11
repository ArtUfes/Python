from baralho import Baralho
from avaliador_de_maos import AvaliadorDeMaos
from jogador import Jogador
from carta import Carta

class Mesa:
    def __init__(self):
        self.baralho = Baralho()
        self.cartas_na_mesa = []
        self.jogadores = []
    
    def sorteia_cartas_mesa(self):
        for i in range(0, 5):
            self.cartas_na_mesa.append(self.baralho.sorteia_uma_carta())
    
    def imprimir_mesa(self):
        tam = 22
        print('-'*tam)
        print(f"{'MESA':^{tam}}")
        print('-'*tam)
        for c in self.cartas_na_mesa:
            c.imprimir_carta()
        print()

        print()
        for j in self.jogadores:
            j.imprimir_jogador()
            print('\n')
    
    def adiciona_jogador(self, jogador):
        if len(self.jogadores) < 9:
            self.jogadores.append(jogador)
        else:
            print('A mesa já está cheia!')
    
    def reseta_mesa(self):
        self.baralho.reseta_baralho()
        self.cartas_na_mesa.clear()
        for j in self.jogadores:
            j.reseta_cartas_jogador()
    
    def sorteia_jogo(self):
        self.sorteia_cartas_mesa()

        # Sorteia as cartas de cada jogador:
        for j in self.jogadores:
            j.sorteia_cartas_jogador(self.baralho)
    
    def encontra_jogadores_com_melhores_maos(self):
        # Cria lista ordenada de jogadores com as melhores mãos:
        jogadores_com_melhores_maos = sorted(self.jogadores, key=lambda x: x.classificacao_mao, reverse=True)

        # Cria uma lista de jogadores que não possuem a melhor mão:
        melhor_mao = jogadores_com_melhores_maos[0].classificacao_mao
        pessoas_para_remover = []
        for j in jogadores_com_melhores_maos:
            if j.classificacao_mao != melhor_mao:
                pessoas_para_remover.append(j)
        
        # Remove os jogadores que não possuem a melhor mão da lista de jogadores com as melhores mãos:
        for j in pessoas_para_remover:
            jogadores_com_melhores_maos.remove(j)
        
        return jogadores_com_melhores_maos

    def avalia_mao_jogadores(self):
        # Avalia a mão de cada jogador:
        for j in self.jogadores:
            j.mao = sorted(self.cartas_na_mesa + j.cartas, key=lambda x: x.valor, reverse=True)
            j.classificacao_mao = AvaliadorDeMaos.avalia_mao(j.mao)

    def realiza_uma_jogada(self):
        self.sorteia_jogo() # Sorteia cartas da mesa e dos jogadores

        self.imprimir_mesa()
        
        self.avalia_mao_jogadores() # Vê qual mão cada jogador possui (par, trio, flush...)
        
        jogadores_com_melhores_maos = self.encontra_jogadores_com_melhores_maos() # Deixa apenas os jogadores com a maior mão
        
        AvaliadorDeMaos.encontra_melhor_mao_jogadores(jogadores_com_melhores_maos) # Preenche as melhores 5 cartas de cada jogador
        
        # Se houver apenas um jogador com a melhor mão, ele vence:
        if len(jogadores_com_melhores_maos) == 1:
            Mesa.imprimir_vencedor_unico(jogadores_com_melhores_maos[0])

        # Se houver mais de um jogador com a melhor mão, implementar desempate:
        else:
            ganhadores = AvaliadorDeMaos.encontra_ganhadores_desempate(jogadores_com_melhores_maos)
            
            if len(ganhadores) != 0:
                if len(ganhadores) == 1:
                    Mesa.imprimir_vencedor_unico(ganhadores[0])
                else:
                    Mesa.imprimir_vencedores_multiplos(ganhadores)
                                 
        self.reseta_mesa() # Reseta a mesa para a próxima rodada
        
        
    def mesa_set(self):
        self.adiciona_jogador(Jogador('Arthur'))
        self.jogadores[0].cartas.append(Carta(14, '♦️'))
        self.jogadores[0].cartas.append(Carta(14, '♣️'))

        # '♠️' '♦️' '♣️' '♥️'

        self.cartas_na_mesa.append(Carta(11, '♠️'))
        self.cartas_na_mesa.append(Carta(13, '♦️'))
        self.cartas_na_mesa.append(Carta(10, '♦️'))
        self.cartas_na_mesa.append(Carta(12, '♦️'))
        self.cartas_na_mesa.append(Carta(11, '♦️'))
    
    def imprimir_vencedor_unico(jogador):
        print(f'{jogador.nome} venceu com {AvaliadorDeMaos.imprimir_mao(jogador.classificacao_mao)}!', end='')
        for c in jogador.melhor_mao:
            c.imprimir_carta()
        print('\n')
    
    def imprimir_vencedores_multiplos(jogadores):
        print('Os jogadores ', end='')
        for i in range(len(jogadores)):
            print(f'{jogadores[i].nome}', end='')
            if i != len(jogadores) - 1 and i != len(jogadores) - 2:
                print(end=', ')
            elif i == len(jogadores) - 2:
                print(end=' e ')
            else:
                print(f' venceram com {AvaliadorDeMaos.imprimir_mao(jogadores[0].classificacao_mao)}!', end='')
        for c in jogadores[0].melhor_mao:
            c.imprimir_carta()
        print('\n')
