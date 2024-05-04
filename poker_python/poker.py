import time
from mesa import Mesa
from jogador import Jogador
from avaliador_de_maos import AvaliadorDeMaos
from baralho import Baralho

mesa = Mesa() # Instancia um objeto da classe Mesa

# Adiciona jogadores na mesa:
mesa.adiciona_jogador(Jogador('Arthur'))
mesa.adiciona_jogador(Jogador('Matheus'))
mesa.adiciona_jogador(Jogador('Robson'))
# mesa.adiciona_jogador(Jogador('Marcia'))
# mesa.adiciona_jogador(Jogador('Marilene'))
# mesa.adiciona_jogador(Jogador('Bruninho'))
# mesa.adiciona_jogador(Jogador('Gatti'))
# mesa.adiciona_jogador(Jogador('Miguel Carlini'))
# mesa.adiciona_jogador(Jogador('Eder'))

opcao = int(input('Qual opcao você deseja?\n1-Realizar uma jogada\n2-Testar cartas especificas\n3-Testar uma mão várias vezes\n4-Testar probabilidade de maos\n5-Testar probabilidade de sorteio de carta\n'))

if opcao == 1:
    qtd = int(input('Quantas rodadas você deseja ver? '))
    for i in range(0, qtd):
        player = mesa.realiza_uma_jogada()

elif opcao == 2:
    mesa.mesa_set()

    mesa.imprimir_mesa()

    player = mesa.jogadores[0]

    player.mao = AvaliadorDeMaos.avalia_mao(mesa.cartas_na_mesa + mesa.jogadores[0].cartas)

    print(f'{player.nome} venceu com {AvaliadorDeMaos.imprimir_mao(player.mao)}!')

elif opcao == 3:
    mao = int(input('Qual mão deseja testar?\n2-Par\n3-Dois Pares\n4-Trio\n5-Sequencia\n6-Flush\n7-Full House\n8-Quadra\n9-Straight Flush\n10-Royal Flush\n'))
    qtd = int(input('Quantas vezes deseja rodar o programa? '))
    tempo_medio = rodadas_media = rodadas = 0

    print('Calculando...')
    for i in range(0, qtd):
        start = time.time()
        rodadas = 0

        while True:
            rodadas += 1

            mesa.sorteia_cartas_mesa()

            for j in mesa.jogadores:
                j.sorteia_cartas_jogador(mesa.baralho)
            
            # mesa.imprimir_mesa()

            num = False
            for j in mesa.jogadores:
                if mao == 2:
                    num = AvaliadorDeMaos.eh_par(mesa.cartas_na_mesa + j.cartas)
                elif mao == 3:
                    num = AvaliadorDeMaos.eh_dois_pares(mesa.cartas_na_mesa + j.cartas)
                elif mao == 4:
                    num = AvaliadorDeMaos.eh_trio(mesa.cartas_na_mesa + j.cartas)
                elif mao == 5:
                    num = AvaliadorDeMaos.eh_sequencia(mesa.cartas_na_mesa + j.cartas)
                elif mao == 6:
                    num = AvaliadorDeMaos.eh_flush(mesa.cartas_na_mesa + j.cartas)
                elif mao == 7:
                    num = AvaliadorDeMaos.eh_full_house(mesa.cartas_na_mesa + j.cartas)
                elif mao == 8:
                    num = AvaliadorDeMaos.eh_quadra(mesa.cartas_na_mesa + j.cartas)
                elif mao == 9:
                    num = AvaliadorDeMaos.eh_straight_flush(mesa.cartas_na_mesa + j.cartas)
                elif mao == 10:
                    num = AvaliadorDeMaos.eh_royal_flush(mesa.cartas_na_mesa + j.cartas)
                if num:
                    print(f'\n{i+1}° vez:')
                    mesa.imprimir_mesa()
                    break

            mesa.reseta_mesa()
            if num:
                break

        end = time.time()

        tempo_medio += end - start
        rodadas_media += rodadas
        
    rodadas_media /= qtd

    print(f'Foram necessarias em media {rodadas_media:.2f} rodadas para sair {AvaliadorDeMaos.imprimir_mao(mao)}!')
    print(f'Cada {AvaliadorDeMaos.imprimir_mao(mao)} levou em media {tempo_medio/qtd:.2f} seg para aparecer!')
    print(f'O programa levou {tempo_medio:.2f} seg para executar!')

elif opcao == 4:
    mesa.jogadores.clear() # Retira todos os jogadores da mesa
    mesa.adiciona_jogador(Jogador('Arthur')) # Adiciona o jogador Arthur para calcular para só um jogador

    maos = [0] * 10 # Cria um array com 10 posições inicializadas com zero

    qtd = int(input('Quantas rodadas você deseja ver? '))
    for i in range(0, qtd):
        mesa.sorteia_cartas_mesa()

        # Sorteia as cartas dos jogadores:
        for j in mesa.jogadores:
            j.sorteia_cartas_jogador(mesa.baralho)

        # Avalia a mão para cada jogador da mesa:
        for j in mesa.jogadores:
            mao = AvaliadorDeMaos.avalia_mao(mesa.cartas_na_mesa + j.cartas)

        maos[mao-1] += 1 # Soma um na posição do array referente a mão retirada para efetuar o somatório

        mesa.reseta_mesa()

    # Imprime a saída:
    for i in range(0, 10):
        porcentagem = (maos[i]/qtd)*100
        if i < 7:
            print(f'Quantidade de mãos com {AvaliadorDeMaos.imprimir_mao(i+1)}: {maos[i]} ({porcentagem:.2f}%)')
        else:
            print(f'Quantidade de mãos com {AvaliadorDeMaos.imprimir_mao(i+1)}: {maos[i]} ({porcentagem:.8f}%)')

elif opcao == 5:
    baralho = Baralho()

    sorteios = int(input('Quantas vezes deseja sortear? '))

    qtds = [0] *  52 # Cria um array com 52 posições e inicializa todas com zero

    start = time.time() # Começa a contar o tempo

    for i in range(0, sorteios):
        sort = baralho.sorteia_uma_carta_idx()

        qtds[sort] += 1 # Soma um na posição do array referente a carta que foi sorteada para efetuar o somatório
        
        baralho.reseta_baralho() # Fazemos isso para que o baralho possa sortear qualquer uma das 52 cartas novamente
    
    end = time.time() # Para de contar o tempo
    
    # Imprime a saída:
    print(f'\nQuantidade de cartas sorteadas:')
    for i in range(52):
        carta = baralho.cartas[i].retornar_carta()
        porcentagem = (qtds[i]/sorteios) * 100
        print(f'{carta}: {qtds[i]} ({porcentagem:.2f}%)')
    
    print(f'O programa levou {end - start:.2f} seg para executar!')