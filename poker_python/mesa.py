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

    def realiza_uma_jogada(self):
        self.sorteia_cartas_mesa()

        # Sorteia as cartas de cada jogador:
        for j in self.jogadores:
            j.sorteia_cartas_jogador(self.baralho)

        self.imprimir_mesa()
        
        # Avalia a mão de cada jogador:
        for j in self.jogadores:
            j.classificacao_mao = AvaliadorDeMaos.avalia_mao(self.cartas_na_mesa + j.cartas)
            j.mao = sorted(self.cartas_na_mesa + j.cartas, key=lambda x: x.valor, reverse=True)
        
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

        # Imprime os jogadores com as melhores mãos:
        for j in jogadores_com_melhores_maos:
            # print(f'{j.nome} - {j.classificacao_mao}')
            pass
        
        # Se houver apenas um jogador com a melhor mão, ele vence:
        if len(jogadores_com_melhores_maos) == 1:
            j = jogadores_com_melhores_maos[0]
            print(f'{j.nome} venceu com {AvaliadorDeMaos.imprimir_mao(j.classificacao_mao)}!')

        # Se houver mais de um jogador com a melhor mão, implementar desempate:
        else:
            # implementar desempate
            if jogadores_com_melhores_maos[0].classificacao_mao == 2:
                ganhadores = AvaliadorDeMaos.desempata_par(jogadores_com_melhores_maos)
                # self.imprimir_mesa() # Verificar se esse método está na melhor posição do código
                if len(ganhadores) == 1:
                    print(f'{ganhadores[0].nome} venceu com {AvaliadorDeMaos.imprimir_mao(ganhadores[0].classificacao_mao)}!\n')
                else:
                    self.imprimir_mesa()

                    print('Os jogadores ', end='')
                    for i in range(len(ganhadores)):
                        print(f'{ganhadores[i].nome}', end='')
                        if i != len(ganhadores) - 1 and i != len(ganhadores) - 2:
                            print(end=', ')
                        elif i == len(ganhadores) - 2:
                            print(end=' e ')
                        else:
                            print(f' venceram com {AvaliadorDeMaos.imprimir_mao(ganhadores[0].classificacao_mao)}!\n')

                              
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




            
        

        
