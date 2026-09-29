import time
from core.mesa import Mesa
from core.jogador import Jogador
from core.avaliador_de_maos import AvaliadorDeMaos
from core.baralho import Baralho


qtd_rodadas = 100000
tempo = 0

mesa = Mesa()

mesa.adiciona_jogador(Jogador('Arthur'))
mesa.adiciona_jogador(Jogador('Matheus'))
mesa.adiciona_jogador(Jogador('Robson'))

# Teste v1:

print('Calculando...')
for i in range(0, qtd_rodadas):
    start = time.time()
    rodadas = 0

    mesa.sorteia_cartas_mesa()

    for j in mesa.jogadores:
        j.sorteia_cartas_jogador(mesa.baralho)    

    mesa.reseta_mesa()
        

    end = time.time()

    tempo_medio += end - start
    rodadas_media += rodadas
    
rodadas_media /= qtd

print(f'Foram necessarias em media {rodadas_media:.2f} rodadas para sair {AvaliadorDeMaos.imprimir_mao(mao)}!')
print(f'Cada {AvaliadorDeMaos.imprimir_mao(mao)} levou em media {tempo_medio/qtd:.2f} seg para aparecer!')
print(f'O programa levou {tempo_medio:.2f} seg para executar!')

