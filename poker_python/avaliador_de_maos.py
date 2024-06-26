from jogador import Jogador
from carta import Carta

class AvaliadorDeMaos:
    @staticmethod
    def imprimir_mao(mao):
        if mao == 10:
            return 'Royal Flush'
        elif mao == 9:
            return 'Straight Flush'
        elif mao == 8:
            return 'Quadra'
        elif mao == 7:
            return 'Full House'
        elif mao == 6:
            return 'Flush'
        elif mao == 5:
            return 'Sequencia'
        elif mao == 4:
            return 'Trio'
        elif mao == 3:
            return 'Dois Pares'
        elif mao == 2:
            return 'Par'
        else:
            return 'Carta Alta'

    @staticmethod
    def eh_royal_flush(cartas):
        # Primeiro verifica se existe um flush, senão, não é um Royal Flush:
        espadas = copas = paus = ouros = 0
        for c in cartas:
            if c.naipe == '♠️':
                espadas += 1
            elif c.naipe == '♦️':
                ouros += 1
            elif c.naipe == '♣️':
                paus += 1
            elif c.naipe == '♥️':
                copas += 1
        
        # Identifica qual naipe tem 5 ou mais cartas:
        tem_flush = False
        if espadas >= 5:
            naipe = '♠️'
            tem_flush = True            
        elif ouros >= 5:
            naipe = '♦️'
            tem_flush = True
        elif paus >= 5:
            naipe = '♣️'
            tem_flush = True
        elif copas >= 5:
            naipe = '♥️'
            tem_flush = True

        # Se não tem um flush, não é um Royal Flush:
        if not tem_flush:
            return False

        # Verifica se existe a maior sequencia do jogo:
        valores = sorted(cartas, key=lambda c: c.valor, reverse=True)
        val = 14
        count = -1
        for c in valores:
            if c.naipe == naipe:
                if count == -1:
                    if c.valor == val:
                        val -= 1
                        count = 1
                    else:
                        count = 0
                else:
                    if c.valor == val:
                        val -= 1
                        count += 1
                        if count == 5:
                            return True
                    else:
                        count = 0
        if count >= 5:
            return True
        return False
            
    @staticmethod
    def eh_straight_flush(cartas):
        # Primeiro verifica se existe um flush, senão, não é um Straight Flush:
        espadas = copas = paus = ouros = 0
        for c in cartas:
            if c.naipe == '♠️':
                espadas += 1
            elif c.naipe == '♦️':
                ouros += 1
            elif c.naipe == '♣️':
                paus += 1
            elif c.naipe == '♥️':
                copas += 1
        
        # Identifica qual naipe tem 5 ou mais cartas:
        tem_flush = False
        if espadas >= 5:
            naipe = '♠️'
            tem_flush = True            
        elif ouros >= 5:
            naipe = '♦️'
            tem_flush = True
        elif paus >= 5:
            naipe = '♣️'
            tem_flush = True
        elif copas >= 5:
            naipe = '♥️'
            tem_flush = True

        # Se não tem um flush, não é um Straight Flush:
        if not tem_flush:
            return False

        # Verifica se existe uma sequencia de 5 cartas do mesmo naipe:
        valores = sorted(cartas, key=lambda c: c.valor, reverse=True)
        val = 0
        count = 0
        for c in valores:
            if c.naipe == naipe:
                if val == 0:
                    val = c.valor - 1
                    count += 1
                else:
                    if c.valor == val:
                        val = c.valor - 1
                        count += 1
                        if count == 5:
                            return True
                    else:
                        val = c.valor - 1
                        count = 1
        if count >= 5:
            return True
        return False
    
    @staticmethod
    def eh_quadra(cartas):
        valores = sorted(cartas, key=lambda c: c.valor, reverse=True)
        val = 0
        count = 0
        for c in valores:
            if val == 0:
                val = c.valor
                count += 1
            else:
                if c.valor == val:
                    count += 1
                else:
                    if count == 4:
                        return True
                    val = c.valor
                    count = 1

        if count == 4:
            return True
        return False
    
    @staticmethod
    def eh_full_house(cartas):
        valores = sorted(cartas, key=lambda c: c.valor, reverse=True)
        eh_trio = False
        val = 0
        count = 0
        trio = -1
        for c in valores:
            if val == 0:
                val = c.valor
                count += 1
            else:
                if c.valor == val:
                    count += 1
                    if count == 3:
                        eh_trio = True
                        trio = val
                        break
                else:
                    val = c.valor
                    count = 1

        if count == 3:
            trio = val
            eh_trio = True
        
        if eh_trio:
            val = 0
            count = 0
            for c in valores:
                if val == 0 and c.valor != trio:
                    val = c.valor
                    count += 1
                else:
                    if c.valor != trio and c.valor == val:
                        count += 1
                        if count == 2:
                            return True
                    else:
                        if c.valor != trio:
                            val = c.valor
                            count = 1
            if count >= 2:
                return True
        return False
    
    @staticmethod
    def eh_flush(cartas):
        espadas = copas = paus = ouros = 0
        for c in cartas:
            if c.naipe == '♠️':
                espadas += 1
            elif c.naipe == '♦️':
                ouros += 1
            elif c.naipe == '♣️':
                paus += 1
            elif c.naipe == '♥️':
                copas += 1
            
        if espadas >= 5 or ouros >= 5 or paus >= 5 or copas >= 5:
            return True
        return False
    
    @staticmethod
    def eh_sequencia(cartas):
        valores = sorted(cartas, key=lambda c: c.valor, reverse=True)
        val = 0
        count = 0
        for c in valores:
            if val == 0:
                val = c.valor - 1
                count += 1
            else:
                if c.valor == val:
                    val = c.valor - 1
                    count += 1
                    if count == 5:
                        return True
                elif c.valor == val + 1:
                    continue
                else:
                    val = c.valor - 1
                    count = 1
        if count < 5:
            # Analise especial para o caso de A, 2, 3, 4, 5:
            # Lembrando que essa lista cartas possuem 7 cartas, então precisamos criar um set a partir dos valores das cartas
            # para depois verificar o caso especial A, 2, 3, 4, 5:
            vals = set()
            for c in valores:
                vals.add(c.valor)
            if 14 in vals and 2 in vals and 3 in vals and 4 in vals and 5 in vals:
                return True
            
        if count >= 5:
            return True
        return False
    
    @staticmethod
    def eh_trio(cartas):
        valores = sorted(cartas, key=lambda c: c.valor, reverse=True)
        val = 0
        count = 0
        for c in valores:
            if val == 0:
                val = c.valor
                count += 1
            else:
                if c.valor == val:
                    count += 1
                else:
                    if count == 3:
                        return True
                    val = c.valor
                    count = 1
        if count == 3:
            return True
        return False
    
    @staticmethod
    def eh_dois_pares(cartas):
        valores = sorted(cartas, key=lambda c: c.valor, reverse=True)
        eh_par = False
        val = 0
        count = 0
        par = -1
        for c in valores:
            if val == 0:
                val = c.valor
                count += 1
            else:
                if c.valor == val:
                    count += 1
                else:
                    if count == 2:
                        eh_par = True
                        par = val
                    val = c.valor
                    count = 1

        if count == 2:
            par = val
            eh_par = True

        if eh_par:
            val = 0
            count = 0
            for c in valores:
                if val == 0 and c.valor != par:
                    val = c.valor
                    count += 1
                else:
                    if c.valor != par and c.valor == val:
                        count += 1
                    else:
                        if c.valor != par:
                            if count == 2:
                                return True
                            val = c.valor
                            count = 1
            if count == 2:
                return True
        return False
    
    @staticmethod
    def eh_par(cartas):
        valores = sorted(cartas, key=lambda c: c.valor, reverse=True)

        val = 0
        count = 0
        for c in valores:
            if val == 0:
                val = c.valor
                count += 1
            else:
                if c.valor == val:
                    count += 1
                else:
                    if count == 2:
                        return True
                    val = c.valor
                    count = 1
        if count == 2:
            return True
        return False
    
    @staticmethod
    def avalia_mao(cartas):
        if AvaliadorDeMaos.eh_royal_flush(cartas):
            return 10
        elif AvaliadorDeMaos.eh_straight_flush(cartas):
            return 9
        elif AvaliadorDeMaos.eh_quadra(cartas):
            return 8
        elif AvaliadorDeMaos.eh_full_house(cartas):
            return 7
        elif AvaliadorDeMaos.eh_flush(cartas):
            return 6
        elif AvaliadorDeMaos.eh_sequencia(cartas):
            return 5
        elif AvaliadorDeMaos.eh_trio(cartas):
            return 4
        elif AvaliadorDeMaos.eh_dois_pares(cartas):
            return 3
        elif AvaliadorDeMaos.eh_par(cartas):
            return 2
        else:
            return 1
    
    @staticmethod
    def desempata_par(jogadores):  
        for qtd_vezes in range(4):
            jogadores_para_remover = [] # Lista que vai armazenar jogadores que não possuem a melhor mao
            maior_valor_carta = -1
            idx_maiores_cartas = [] # Lista que armazena o idx dos jogadores que possuem a maior carta atual

            idx = qtd_vezes + 1
            
            for i in range(len(jogadores)):
                if i == 0:
                    maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                    idx_maiores_cartas.append(i)
                else:
                    if jogadores[i].melhor_mao[idx].valor > maior_valor_carta:
                        for j in idx_maiores_cartas:
                            jogadores_para_remover.append(jogadores[j])
                        maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                        idx_maiores_cartas.clear()
                        idx_maiores_cartas.append(i)
                    elif jogadores[i].melhor_mao[idx].valor < maior_valor_carta:
                        jogadores_para_remover.append(jogadores[i])
                    else:
                        idx_maiores_cartas.append(i)
            
            # Criamos um set da lista de jogadores para remover para remover jogadores repetidos
            jogadores_para_remover_unicos = set(jogadores_para_remover)
            for j in jogadores_para_remover_unicos:
                jogadores.remove(j)
            
        return jogadores

    @staticmethod
    def desempata_dois_pares(jogadores):
        # Agora devemos analisar quem tem a melhor mão e ir removendo os jogadores que tem a pior mão da lista de jogadores:

        for qtd_vezes in range(3):
            jogadores_para_remover = [] # Lista que vai armazenar jogadores que não possuem a melhor mao
            maior_valor_carta = -1
            idx_maiores_cartas = [] # Lista que armazena o idx dos jogadores que possuem a maior carta atual

            if qtd_vezes == 0:
                idx = 0
            elif qtd_vezes == 1:
                idx = 2
            else:
                idx = 4

            for i in range(len(jogadores)):
                if i == 0:
                    maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                    idx_maiores_cartas.append(i)
                else:
                    if jogadores[i].melhor_mao[idx].valor > maior_valor_carta:
                        for j in idx_maiores_cartas:
                            jogadores_para_remover.append(jogadores[j])
                        maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                        idx_maiores_cartas.clear()
                        idx_maiores_cartas.append(i)
                    elif jogadores[i].melhor_mao[idx].valor < maior_valor_carta:
                        jogadores_para_remover.append(jogadores[i])
                    else:
                        idx_maiores_cartas.append(i)
            
            # Criamos um set da lista de jogadores para remover para remover jogadores repetidos
            jogadores_para_remover_unicos = set(jogadores_para_remover)
            for j in jogadores_para_remover_unicos:
                jogadores.remove(j)
            
        return jogadores

    @staticmethod
    def desempata_trio(jogadores):
        for qtd_vezes in range(3):
            jogadores_para_remover = [] # Lista que vai armazenar jogadores que não possuem a melhor mao
            maior_valor_carta = -1
            idx_maiores_cartas = [] # Lista que armazena o idx dos jogadores que possuem a maior carta atual

            if qtd_vezes == 0:
                idx = 0
            elif qtd_vezes == 1:
                idx = 3
            else:
                idx = 4
            
            for i in range(len(jogadores)):
                if i == 0:
                    maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                    idx_maiores_cartas.append(i)
                else:
                    if jogadores[i].melhor_mao[idx].valor > maior_valor_carta:
                        for j in idx_maiores_cartas:
                            jogadores_para_remover.append(jogadores[j])
                        maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                        idx_maiores_cartas.clear()
                        idx_maiores_cartas.append(i)
                    elif jogadores[i].melhor_mao[idx].valor < maior_valor_carta:
                        jogadores_para_remover.append(jogadores[i])
                    else:
                        idx_maiores_cartas.append(i)
            
            # Criamos um set da lista de jogadores para remover para remover jogadores repetidos
            jogadores_para_remover_unicos = set(jogadores_para_remover)
            for j in jogadores_para_remover_unicos:
                jogadores.remove(j)
        
        return jogadores

    @staticmethod
    def desempata_sequencia(jogadores):
        # Agora devemos analisar quem tem a melhor sequência e ir removendo os jogadores que tem a pior mão da lista de jogadores:
        # Faremos isso apenas analisando a carta mais alta da sequência

        jogadores_para_remover = [] # Lista que vai armazenar jogadores que não possuem a melhor mao
        maior_valor_carta = -1
        idx_maiores_cartas = []
        for j in range(len(jogadores)):
            if j == 0:
                maior_valor_carta = jogadores[j].melhor_mao[0].valor
                idx_maiores_cartas.append(j)
            else:
                if jogadores[j].melhor_mao[0].valor > maior_valor_carta:
                    for i in idx_maiores_cartas:
                        jogadores_para_remover.append(jogadores[i])
                    maior_valor_carta = jogadores[j].melhor_mao[0].valor
                    idx_maiores_cartas.clear()
                    idx_maiores_cartas.append(j)
                elif jogadores[j].melhor_mao[0].valor < maior_valor_carta:
                    jogadores_para_remover.append(jogadores[j])
                else:
                    idx_maiores_cartas.append(j)
        
        # Criamos um set da lista de jogadores para remover para remover jogadores repetidos
        jogadores_para_remover_unicos = set(jogadores_para_remover)
        
        for j in jogadores_para_remover_unicos:
            jogadores.remove(j)
        
        return jogadores
    
    @staticmethod
    def desempata_flush(jogadores):
        for qtd_vezes in range(5):
            jogadores_para_remover = [] # Lista que vai armazenar jogadores que não possuem a melhor mao
            maior_valor_carta = -1
            idx_maiores_cartas = [] # Lista que armazena o idx dos jogadores que possuem a maior carta atual

            idx = qtd_vezes
            
            for i in range(len(jogadores)):
                if i == 0:
                    maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                    idx_maiores_cartas.append(i)
                else:
                    if jogadores[i].melhor_mao[idx].valor > maior_valor_carta:
                        for j in idx_maiores_cartas:
                            jogadores_para_remover.append(jogadores[j])
                        maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                        idx_maiores_cartas.clear()
                        idx_maiores_cartas.append(i)
                    elif jogadores[i].melhor_mao[idx].valor < maior_valor_carta:
                        jogadores_para_remover.append(jogadores[i])
                    else:
                        idx_maiores_cartas.append(i)
        
            # Criamos um set da lista de jogadores para remover para remover jogadores repetidos
            jogadores_para_remover_unicos = set(jogadores_para_remover)
            for j in jogadores_para_remover_unicos:
                jogadores.remove(j)
    
        return jogadores

    @staticmethod
    def desempata_full_house(jogadores):
        # Agora devemos analisar quem tem a melhor mão e ir removendo os jogadores que tem a pior mão da lista de jogadores:
        # Faremos isso apenas analisando a carta mais alta do trio

        for qtd_vezes in range(2):
            jogadores_para_remover = [] # Lista que vai armazenar jogadores que não possuem a melhor mao
            maior_valor_carta = -1
            idx_maiores_cartas = [] # Lista que armazena o idx dos jogadores que possuem a maior carta atual

            if qtd_vezes == 0:
                idx = 0
            else:
                idx = 3
            
            for i in range(len(jogadores)):
                if i == 0:
                    maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                    idx_maiores_cartas.append(i)
                else:
                    if jogadores[i].melhor_mao[idx].valor > maior_valor_carta:
                        for j in idx_maiores_cartas:
                            jogadores_para_remover.append(jogadores[j])
                        maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                        idx_maiores_cartas.clear()
                        idx_maiores_cartas.append(i)
                    elif jogadores[i].melhor_mao[idx].valor < maior_valor_carta:
                        jogadores_para_remover.append(jogadores[i])
                    else:
                        idx_maiores_cartas.append(i)
        
            # Criamos um set da lista de jogadores para remover para remover jogadores repetidos
            jogadores_para_remover_unicos = set(jogadores_para_remover)
            for j in jogadores_para_remover_unicos:
                jogadores.remove(j)
    
        return jogadores

    @staticmethod
    def desempata_quadra(jogadores):
        for qtd_vezes in range(2):
            jogadores_para_remover = [] # Lista que vai armazenar jogadores que não possuem a melhor mao
            maior_valor_carta = -1
            idx_maiores_cartas = [] # Lista que armazena o idx dos jogadores que possuem a maior carta atual

            if qtd_vezes == 0:
                idx = 0
            else:
                idx = 4
            
            for i in range(len(jogadores)):
                if i == 0:
                    maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                    idx_maiores_cartas.append(i)
                else:
                    if jogadores[i].melhor_mao[idx].valor > maior_valor_carta:
                        for j in idx_maiores_cartas:
                            jogadores_para_remover.append(jogadores[j])
                        maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                        idx_maiores_cartas.clear()
                        idx_maiores_cartas.append(i)
                    elif jogadores[i].melhor_mao[idx].valor < maior_valor_carta:
                        jogadores_para_remover.append(jogadores[i])
                    else:
                        idx_maiores_cartas.append(i)
        
            # Criamos um set da lista de jogadores para remover para remover jogadores repetidos
            jogadores_para_remover_unicos = set(jogadores_para_remover)
            for j in jogadores_para_remover_unicos:
                jogadores.remove(j)
    
        return jogadores
    
    @staticmethod
    def desempata_straight_flush(jogadores):
        # Agora devemos analisar quem tem a melhor sequência e ir removendo os jogadores que tem a pior mão da lista de jogadores:
        # Faremos isso apenas analisando a carta mais alta da sequência

        jogadores_para_remover = [] # Lista que vai armazenar jogadores que não possuem a melhor mao
        maior_valor_carta = -1
        idx_maiores_cartas = []
        for j in range(len(jogadores)):
            if j == 0:
                maior_valor_carta = jogadores[j].melhor_mao[0].valor
                idx_maiores_cartas.append(j)
            else:
                if jogadores[j].melhor_mao[0].valor > maior_valor_carta:
                    for i in idx_maiores_cartas:
                        jogadores_para_remover.append(jogadores[i])
                    maior_valor_carta = jogadores[j].melhor_mao[0].valor
                    idx_maiores_cartas.clear()
                    idx_maiores_cartas.append(j)
                elif jogadores[j].melhor_mao[0].valor < maior_valor_carta:
                    jogadores_para_remover.append(jogadores[j])
                else:
                    idx_maiores_cartas.append(j)
        
        # Criamos um set da lista de jogadores para remover para remover jogadores repetidos
        jogadores_para_remover_unicos = set(jogadores_para_remover)
        
        for j in jogadores_para_remover_unicos:
            jogadores.remove(j)
        
        return jogadores

    def desempata_carta_alta(jogadores):
        for qtd_vezes in range(5):
            jogadores_para_remover = [] # Lista que vai armazenar jogadores que não possuem a melhor mao
            maior_valor_carta = -1
            idx_maiores_cartas = [] # Lista que armazena o idx dos jogadores que possuem a maior carta atual

            idx = qtd_vezes
            
            for i in range(len(jogadores)):
                if i == 0:
                    maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                    idx_maiores_cartas.append(i)
                else:
                    if jogadores[i].melhor_mao[idx].valor > maior_valor_carta:
                        for j in idx_maiores_cartas:
                            jogadores_para_remover.append(jogadores[j])
                        maior_valor_carta = jogadores[i].melhor_mao[idx].valor
                        idx_maiores_cartas.clear()
                        idx_maiores_cartas.append(i)
                    elif jogadores[i].melhor_mao[idx].valor < maior_valor_carta:
                        jogadores_para_remover.append(jogadores[i])
                    else:
                        idx_maiores_cartas.append(i)
        
            # Criamos um set da lista de jogadores para remover para remover jogadores repetidos
            jogadores_para_remover_unicos = set(jogadores_para_remover)
            for j in jogadores_para_remover_unicos:
                jogadores.remove(j)
    
        return jogadores
        

    @staticmethod
    def naipe_do_flush(cartas):
        espadas = copas = paus = ouros = 0
        for c in cartas:
            if c.naipe == '♠️':
                espadas += 1
            elif c.naipe == '♦️':
                ouros += 1
            elif c.naipe == '♣️':
                paus += 1
            elif c.naipe == '♥️':
                copas += 1
            
        if espadas >= 5:
            return '♠️'
        if ouros >= 5:
            return '♦️'
        if paus >= 5:
            return '♣️'
        if copas >= 5:
            return '♥️'
        
        return False

    @staticmethod
    def remove_cartas_que_nao_sao_do_naipe(cartas, naipe):
        cartas_para_remover = []
        for c in cartas:
            if c.naipe != naipe:
                cartas_para_remover.append(c)
        for c in cartas_para_remover:
            cartas.remove(c)
        return cartas

    @staticmethod
    def encontra_melhor_mao_carta_alta(jogadores):
        # A primeira etapa é construir a melhor mão possível de 5 cartas para cada um dos jogadores:
        for j in jogadores:
            for c in j.mao:
                j.melhor_mao.append(c)
                if len(j.melhor_mao) == 5:
                    break

    @staticmethod
    def encontra_melhor_mao_par(jogadores):
        for j in jogadores:
            mao = j.mao.copy()
            cartas_para_remover = []

            for c in range(len(mao) - 1):
                if mao[c].valor == mao[c+1].valor:
                    j.melhor_mao.append(mao[c])
                    j.melhor_mao.append(mao[c+1])
                    cartas_para_remover.append(mao[c])
                    cartas_para_remover.append(mao[c+1])
                    break

            for c in cartas_para_remover:
                mao.remove(c)

            for c in mao:
                if len(j.melhor_mao) < 5:
                    j.melhor_mao.append(c)
                else:
                    break

    @staticmethod
    def encontra_melhor_mao_dois_pares(jogadores):
        for j in jogadores:
            mao = j.mao.copy()
            cartas_para_remover = []
            count_pares_achados = 0
            # De inicio, teremos sempre sete cartas, (7-1), pois vamos comparar a carta atual com a próxima e não queremos ultrapassar o indice da lista
            for c in range(7 - 1): 
                if mao[c].valor == mao[c+1].valor:
                    count_pares_achados += 1 
                    j.melhor_mao.append(mao[c])
                    j.melhor_mao.append(mao[c+1])
                    cartas_para_remover.append(mao[c])
                    cartas_para_remover.append(mao[c+1])
                    if count_pares_achados == 2: # Se já achamos dois pares, já podemos sair do loop
                        break

            # Removendo da mão analisada os dois pares encontrados:
            for c in cartas_para_remover:
                mao.remove(c)
            
            j.melhor_mao.append(mao[0]) # Adicionando a melhor carta restante na mesa na mão do jogador
    
    @staticmethod
    def encontra_melhor_mao_trio(jogadores):
         # A primeira etapa é construir a melhor mão possível de 5 cartas para cada um dos jogadores:
        for j in jogadores:
            mao = j.mao.copy()
            cartas_para_remover = []

            # Procuramos por um trio na mão do jogador e adicionamos ele na melhor mão do jogador:
            for c in range(7 - 2):
                if j.mao[c].valor == j.mao[c+1].valor and j.mao[c].valor == j.mao[c+2].valor:
                    j.melhor_mao.append(j.mao[c])
                    j.melhor_mao.append(j.mao[c+1])
                    j.melhor_mao.append(j.mao[c+2])
                    cartas_para_remover.append(j.mao[c])
                    cartas_para_remover.append(j.mao[c+1])
                    cartas_para_remover.append(j.mao[c+2])
                    break
            
            # Removemos as três cartas que formam o trio da mão do jogador:
            for c in cartas_para_remover:
                mao.remove(c)

            # Preenche a melhor mão com as duas maiores cartas da mão do jogador (combo de 5 cartas da mesa + 2 do jogador):
            for c in mao:
                if len(j.melhor_mao) < 5:
                    j.melhor_mao.append(c)
                else:
                    break
    
    @staticmethod
    def encontra_melhor_mao_sequencia(jogadores):
        # A primeira etapa é construir a melhor mão possível de 5 cartas para cada um dos jogadores:
        for j in jogadores:
            set_cartas = Carta.cria_set_cartas_pelo_valor(j.mao) # Retiramos a repetição de cartas de mesmo valor

            lista_cartas = sorted(set_cartas, key=lambda c: c.valor, reverse=True) # Ordenamos as cartas pelo valor e colocamos em uma lista

            # A partir disso, teremos três possibilidades: len() == 5, len() == 6 e len() == 7

            if len(lista_cartas) == 5: # Se tivermos 5 cartas, então elas obrigatoriamente formam a sequência
                # Verificamos se a sequência é A, 2, 3, 4, 5
                if lista_cartas[0].valor == 14 and lista_cartas[1].valor == 5:
                    j.melhor_mao.append(lista_cartas[1])
                    j.melhor_mao.append(lista_cartas[2])
                    j.melhor_mao.append(lista_cartas[3])
                    j.melhor_mao.append(lista_cartas[4])
                    j.melhor_mao.append(lista_cartas[0])
                # Se não for A, 2, 3, 4, 5, então a sequência é normal
                else:
                    for c in lista_cartas:
                        j.melhor_mao.append(c)
                
            # Se tivermos 6 cartas então temos que ver se a sequência é formada pelas 5 primeiras cartas, pelas 5 últimas:
            elif len(lista_cartas) == 6:
                # Analisando se a sequência esta nas 5 primeiras cartas:
                if AvaliadorDeMaos.eh_sequencia(lista_cartas[0:5]):
                    for c in lista_cartas[0:5]:
                        j.melhor_mao.append(c)
                # Analisando se a sequência esta nas 5 últimas cartas:
                elif AvaliadorDeMaos.eh_sequencia(lista_cartas[1:6]):
                    for c in lista_cartas[1:6]:
                        j.melhor_mao.append(c)
                # Se não for nenhuma das duas, então estamos no caso especial A, 2, 3, 4, 5:
                else:
                    for c in lista_cartas[2:6]:
                        j.melhor_mao.append(c)
                    j.melhor_mao.append(lista_cartas[0])
            # Se tivermos 7 cartas então temos que ver se a sequência é formada pelas 5 primeiras cartas, pelas 5 do meio, ou pelas 5 últimas:
            elif len(lista_cartas) == 7:
                # Analisando se a sequência esta nas 5 primeiras cartas:
                if AvaliadorDeMaos.eh_sequencia(lista_cartas[0:5]):
                    for c in lista_cartas[0:5]:
                        j.melhor_mao.append(c)
                # Analisando se a sequência esta nas 5 cartas do meio:
                elif AvaliadorDeMaos.eh_sequencia(lista_cartas[1:6]):
                    for c in lista_cartas[1:6]:
                        j.melhor_mao.append(c)
                # Analisando se a sequência esta nas 5 últimas cartas:
                elif AvaliadorDeMaos.eh_sequencia(lista_cartas[2:7]):
                    for c in lista_cartas[2:7]:
                        j.melhor_mao.append(c)
                # Se não for nenhuma das três, então estamos no caso especial A, 2, 3, 4, 5:
                else:
                    for c in lista_cartas[3:7]:
                        j.melhor_mao.append(c)
                    j.melhor_mao.append(lista_cartas[0])

    @staticmethod
    def encontra_melhor_mao_flush(jogadores):
        # A primeira etapa é construir a melhor mão possível de 5 cartas para cada um dos jogadores:
        for j in jogadores:
            naipe = AvaliadorDeMaos.naipe_do_flush(j.mao)

            for c in j.mao:
                if c.naipe == naipe:
                    j.melhor_mao.append(c)
                    if len(j.melhor_mao) == 5:
                        break

    @staticmethod
    def encontra_melhor_mao_full_house(jogadores):
         # A primeira etapa é construir a melhor mão possível de 5 cartas para cada um dos jogadores:
        for j in jogadores:
            mao = j.mao.copy()
            cartas_para_remover = []

            # Procuramos por um trio na mão do jogador e adicionamos ele na melhor mão do jogador:
            for c in range(7 - 2):
                if j.mao[c].valor == j.mao[c+1].valor and j.mao[c].valor == j.mao[c+2].valor:
                    j.melhor_mao.append(j.mao[c])
                    j.melhor_mao.append(j.mao[c+1])
                    j.melhor_mao.append(j.mao[c+2])
                    cartas_para_remover.append(j.mao[c])
                    cartas_para_remover.append(j.mao[c+1])
                    cartas_para_remover.append(j.mao[c+2])
                    break
            
            # Removemos as três cartas que formam o trio da mão do jogador:
            for c in cartas_para_remover:
                mao.remove(c)
            
            cartas_para_remover.clear() # Limpamos a lista de cartas para remover
            
            # Procuramos por um par na mão do jogador e adicionamos ele na melhor mão do jogador:
            for c in range(4 - 1):
                if mao[c].valor == mao[c+1].valor:
                    j.melhor_mao.append(mao[c])
                    j.melhor_mao.append(mao[c+1])
                    cartas_para_remover.append(mao[c])
                    cartas_para_remover.append(mao[c+1])
                    break
            
            # Removemos as duas cartas que formam o par da mão do jogador:
            for c in cartas_para_remover:
                mao.remove(c)

    @staticmethod
    def encontra_melhor_mao_quadra(jogadores):
         # A primeira etapa é construir a melhor mão possível de 5 cartas para cada um dos jogadores:
        for j in jogadores:
            mao = j.mao.copy()
            cartas_para_remover = []

            # Procuramos por uma quadra na mão do jogador e adicionamos ele na melhor mão do jogador:
            for c in range(7 - 3):
                if j.mao[c].valor == j.mao[c+1].valor and j.mao[c].valor == j.mao[c+2].valor and j.mao[c].valor == j.mao[c+3].valor:
                    j.melhor_mao.append(j.mao[c])
                    j.melhor_mao.append(j.mao[c+1])
                    j.melhor_mao.append(j.mao[c+2])
                    j.melhor_mao.append(j.mao[c+3])
                    cartas_para_remover.append(j.mao[c])
                    cartas_para_remover.append(j.mao[c+1])
                    cartas_para_remover.append(j.mao[c+2])
                    cartas_para_remover.append(j.mao[c+3])
                    break
            
            # Removemos as quatro cartas que formam o trio da mão do jogador:
            for c in cartas_para_remover:
                mao.remove(c)
            
            # Preenche a melhor mão com a maior carta restante da mão do jogador:
            j.melhor_mao.append(mao[0])
    
    @staticmethod
    def encontra_melhor_mao_straight_flush(jogadores):
        for j in jogadores:
            naipe = AvaliadorDeMaos.naipe_do_flush(j.mao)
            lista_cartas = AvaliadorDeMaos.remove_cartas_que_nao_sao_do_naipe(j.mao, naipe)

            if len(lista_cartas) == 5: # Se tivermos 5 cartas, então elas obrigatoriamente formam a sequência
                # Verificamos se a sequência é A, 2, 3, 4, 5
                if lista_cartas[0].valor == 14 and lista_cartas[1].valor == 5:
                    j.melhor_mao.append(lista_cartas[1])
                    j.melhor_mao.append(lista_cartas[2])
                    j.melhor_mao.append(lista_cartas[3])
                    j.melhor_mao.append(lista_cartas[4])
                    j.melhor_mao.append(lista_cartas[0])
                # Se não for A, 2, 3, 4, 5, então a sequência é normal
                else:
                    for c in lista_cartas:
                        j.melhor_mao.append(c)
                
            # Se tivermos 6 cartas então temos que ver se a sequência é formada pelas 5 primeiras cartas, pelas 5 últimas:
            elif len(lista_cartas) == 6:
                # Analisando se a sequência esta nas 5 primeiras cartas:
                if AvaliadorDeMaos.eh_sequencia(lista_cartas[0:5]):
                    for c in lista_cartas[0:5]:
                        j.melhor_mao.append(c)
                # Analisando se a sequência esta nas 5 últimas cartas:
                elif AvaliadorDeMaos.eh_sequencia(lista_cartas[1:6]):
                    for c in lista_cartas[1:6]:
                        j.melhor_mao.append(c)
                # Se não for nenhuma das duas, então estamos no caso especial A, 2, 3, 4, 5:
                else:
                    for c in lista_cartas[2:6]:
                        j.melhor_mao.append(c)
                    j.melhor_mao.append(lista_cartas[0])
            # Se tivermos 7 cartas então temos que ver se a sequência é formada pelas 5 primeiras cartas, pelas 5 do meio, ou pelas 5 últimas:
            elif len(lista_cartas) == 7:
                # Analisando se a sequência esta nas 5 primeiras cartas:
                if AvaliadorDeMaos.eh_sequencia(lista_cartas[0:5]):
                    for c in lista_cartas[0:5]:
                        j.melhor_mao.append(c)
                # Analisando se a sequência esta nas 5 cartas do meio:
                elif AvaliadorDeMaos.eh_sequencia(lista_cartas[1:6]):
                    for c in lista_cartas[1:6]:
                        j.melhor_mao.append(c)
                # Analisando se a sequência esta nas 5 últimas cartas:
                elif AvaliadorDeMaos.eh_sequencia(lista_cartas[2:7]):
                    for c in lista_cartas[2:7]:
                        j.melhor_mao.append(c)
                # Se não for nenhuma das três, então estamos no caso especial A, 2, 3, 4, 5:
                else:
                    for c in lista_cartas[3:7]:
                        j.melhor_mao.append(c)
                    j.melhor_mao.append(lista_cartas[0])

    @staticmethod
    def encontra_melhor_mao_royal_flush(jogadores):
        for j in jogadores:
            naipe = AvaliadorDeMaos.naipe_do_flush(jogadores)
            for i in range(5):
                j.melhor_mao[i] = Carta(14-i, naipe)
    
    @staticmethod
    def encontra_melhor_mao_jogadores(jogadores):
        mao = jogadores[0].classificacao_mao

        if mao == 1:
            AvaliadorDeMaos.encontra_melhor_mao_carta_alta(jogadores)
        elif mao == 2:
            AvaliadorDeMaos.encontra_melhor_mao_par(jogadores)
        elif mao == 3:
            AvaliadorDeMaos.encontra_melhor_mao_dois_pares(jogadores)
        elif mao == 4:
            AvaliadorDeMaos.encontra_melhor_mao_trio(jogadores)
        elif mao == 5:
            AvaliadorDeMaos.encontra_melhor_mao_sequencia(jogadores)
        elif mao == 6:
            AvaliadorDeMaos.encontra_melhor_mao_flush(jogadores)
        elif mao == 7:
            AvaliadorDeMaos.encontra_melhor_mao_full_house(jogadores)
        elif mao == 8:
            AvaliadorDeMaos.encontra_melhor_mao_quadra(jogadores)
        elif mao == 9:
            AvaliadorDeMaos.encontra_melhor_mao_straight_flush(jogadores)
        elif mao == 10:
            AvaliadorDeMaos.encontra_melhor_mao_royal_flush(jogadores)
    
    @staticmethod
    def encontra_ganhadores_desempate(jogadores):
        if jogadores[0].classificacao_mao == 1:
            return AvaliadorDeMaos.desempata_carta_alta(jogadores)
        elif jogadores[0].classificacao_mao == 2:
            return AvaliadorDeMaos.desempata_par(jogadores)
        elif jogadores[0].classificacao_mao == 3:
            return AvaliadorDeMaos.desempata_dois_pares(jogadores)
        elif jogadores[0].classificacao_mao == 4:
            return AvaliadorDeMaos.desempata_trio(jogadores)
        elif jogadores[0].classificacao_mao == 5:
            return AvaliadorDeMaos.desempata_sequencia(jogadores)
        elif jogadores[0].classificacao_mao == 6:
            return AvaliadorDeMaos.desempata_flush(jogadores)
        elif jogadores[0].classificacao_mao == 7:
            return AvaliadorDeMaos.desempata_full_house(jogadores)
        elif jogadores[0].classificacao_mao == 8:
            return AvaliadorDeMaos.desempata_quadra(jogadores)
        elif jogadores[0].classificacao_mao == 9:
            return AvaliadorDeMaos.desempata_straight_flush(jogadores)