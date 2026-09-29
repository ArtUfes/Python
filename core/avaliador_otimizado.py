class AvaliadorDeMaosOtimizado:
    @staticmethod
    def avalia_mao(cartas):
        contagem_valores = [0] * 15
        contagem_naipes = {'♠️': 0, '♦️': 0, '♣️': 0, '♥️': 0}
        valores_por_naipe = {'♠️': 0, '♦️': 0, '♣️': 0, '♥️': 0} 
        mascara_valores = 0
        
        for c in cartas:
            v = c.valor
            n = c.naipe
            
            contagem_valores[v] += 1
            contagem_naipes[n] += 1
            
            bit = 1 << v
            mascara_valores |= bit
            valores_por_naipe[n] |= bit
            
        # Função auxiliar para extrair kickers (cartas mais altas restantes)
        def get_kickers(n_cartas, exclude=()):
            k = []
            for v in range(14, 1, -1):
                if v not in exclude:
                    for _ in range(contagem_valores[v]):
                        k.append(v)
                        if len(k) == n_cartas:
                            return tuple(k)
            return tuple(k)

        # 1. Verifica Flush e Straight Flush
        naipe_flush = None
        for n, cont in contagem_naipes.items():
            if cont >= 5:
                naipe_flush = n
                break
                
        if naipe_flush:
            bits_flush = valores_por_naipe[naipe_flush]
            if bits_flush & (1 << 14):
                bits_flush |= (1 << 1)
            
            for shift in range(10, 0, -1):
                if (bits_flush >> shift) & 31 == 31:
                    if shift == 10:
                        return (10,)
                    return (9, shift + 4)
                    
        # 2. Varredura por Quadra, Trincas e Pares
        pares = []
        trincas = []
        quadra = 0
        
        for v in range(14, 1, -1):
            qtd = contagem_valores[v]
            if qtd == 4:
                quadra = v
            elif qtd == 3:
                trincas.append(v)
            elif qtd == 2:
                pares.append(v)
                
        if quadra:
            return (8, quadra) + get_kickers(1, exclude=(quadra,))
            
        if len(trincas) >= 2:
            return (7, trincas[0], trincas[1])
        elif len(trincas) == 1 and len(pares) >= 1:
            return (7, trincas[0], pares[0])
            
        if naipe_flush:
            bits = valores_por_naipe[naipe_flush]
            flush_cards = []
            for v in range(14, 1, -1):
                if (bits >> v) & 1:
                    flush_cards.append(v)
                    if len(flush_cards) == 5:
                        break
            return (6, *flush_cards)
            
        # 3. Straight Normal
        bits_seq = mascara_valores
        if bits_seq & (1 << 14):
            bits_seq |= (1 << 1)
            
        for shift in range(10, 0, -1):
            if (bits_seq >> shift) & 31 == 31:
                return (5, shift + 4)
                
        # 4. Outras Mãos
        if len(trincas) >= 1:
            return (4, trincas[0]) + get_kickers(2, exclude=(trincas[0],))
        if len(pares) >= 2:
            return (3, pares[0], pares[1]) + get_kickers(1, exclude=(pares[0], pares[1]))
        if len(pares) == 1:
            return (2, pares[0]) + get_kickers(3, exclude=(pares[0],))
            
        return (1,) + get_kickers(5)

    @staticmethod
    def imprimir_mao(mao):
        # Acomoda tanto a classe nova (que manda tupla) quanto a antiga (que manda int)
        if isinstance(mao, tuple):
            mao = mao[0]
            
        if mao == 10: return 'Royal Flush'
        elif mao == 9: return 'Straight Flush'
        elif mao == 8: return 'Quadra'
        elif mao == 7: return 'Full House'
        elif mao == 6: return 'Flush'
        elif mao == 5: return 'Sequencia'
        elif mao == 4: return 'Trio'
        elif mao == 3: return 'Dois Pares'
        elif mao == 2: return 'Par'
        else: return 'Carta Alta'
