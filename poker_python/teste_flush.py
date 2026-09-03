from carta import Carta
from jogador import Jogador
from avaliador_de_maos import AvaliadorDeMaos
from mesa import Mesa
from baralho import Baralho

qtd_flush = rodadas = 0

mesa = Mesa() # Instancia um objeto da classe Mesa

# Adiciona jogadores na mesa:
mesa.adiciona_jogador(Jogador('Arthur'))
player = mesa.jogadores[0]

for i in range(10):
    mesa.sorteia_jogo() # Sorteia cartas da mesa e dos jogadores

    mesa.imprimir_mesa()
        
    mesa.avalia_mao_jogadores() # Vê qual mão cada jogador possui (par, trio, flush...)
        
    jogadores_com_melhores_maos = mesa.encontra_jogadores_com_melhores_maos() # Deixa apenas os jogadores com a maior mão
        
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
                                

    if(player.classificacao_mao == 6):
        qtd_flush += 1
    
    rodadas += 1

    mesa.reseta_mesa() # Reseta a mesa para a próxima rodada

print(f'Tiveram {qtd_flush} flush em {rodadas} rodadas!\nPorcentagem: {qtd_flush/rodadas*100:.2f}%')



