from jogador import Jogador

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
        val = 10
        count = -1
        for c in valores:
            if c.naipe == naipe:
                if count == -1:
                    if c.valor == val:
                        val += 1
                        count = 1
                    else:
                        count = 0
                else:
                    if c.valor == val:
                        val += 1
                        count += 1
                    else:
                        if count == 5:
                            return True
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
                    val = c.valor + 1
                    count += 1
                else:
                    if c.valor == val:
                        val = c.valor + 1
                        count += 1
                    else:
                        if count == 5:
                            return True
                        val = c.valor + 1
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
                else:
                    if count == 3:
                        eh_trio = True
                        trio = val
                        break
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
                    else:
                        if c.valor != trio:
                            if count == 2:
                                return True
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
                val = c.valor + 1
                count += 1
            else:
                if c.valor == val:
                    val = c.valor + 1
                    count += 1
                elif c.valor == val - 1:
                    continue
                else:
                    if count == 5:
                        return True
                    val = c.valor + 1
                    count = 1
        if count < 5:
            # Analise especial para o caso de A, 2, 3, 4, 5:
            # Lembrando que essa lista cartas possuem 7 cartas, então precisamos criar um set a partir dos valores das cartas
            # para depois verificar o caso especial A, 2, 3, 4, 5:
            # vals = set()
            # for c in valores:
            #     vals.add(c.valor)
            # if 14 in vals and 2 in vals and 3 in vals and 4 in vals and 5 in vals:
            #     return True
            pass
            
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
        for j in jogadores:
            print(f'Jogador: {j.nome} - Cartas: ')
            for c in j.mao:
                c.imprimir_carta()
            print('\n')

            val = 0
            count = 0
            for c in j.mao:
                if val == 0:
                    val = c.valor
                    count += 1
                else:
                    if c.valor == val:
                        count += 1
                        if count == 2:
                            j.maior_valor = c.valor
                    else:
                        if count == 2:
                            break
                        val = c.valor
                        count = 1
                if count == 2:
                    break
        
        maiores_pares = sorted(jogadores, key=lambda x: x.maior_valor, reverse=True)
        maior_par = maiores_pares[0].maior_valor
        jogadores_para_remover = []
        for j in jogadores:
            if j.maior_valor != maior_par:
                jogadores_para_remover.append(j)
        
        for j in jogadores_para_remover:
            jogadores.remove(j)
        
        for j in jogadores:
            print(f'Jogador: {j.nome} - Par: {j.maior_valor}')
        
        if len(jogadores) == 1:
            return jogadores
        else:
            # Implementar desempate
            return []

            
            
    
    
