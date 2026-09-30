class Pote:
    def __init__(self):
        self.valor = 0
        self.jogadores_elegiveis = set()

class GerenciadorDePote:
    def __init__(self):
        self.potes = []
        self.potes.append(Pote())

    def processar_rodada(self, apostas_jogadores, jogadores_ativos):
        """
        Processa as apostas da rodada e cria Side Pots automaticamente.
        apostas_jogadores: dict {nome_jogador: valor_apostado_nesta_rodada}
        jogadores_ativos: set/list de nomes de jogadores que não deram fold.
        """
        # Filtra apenas os jogadores que apostaram mais que 0
        apostas = {j: v for j, v in apostas_jogadores.items() if v > 0}
        
        while apostas:
            # Encontra a menor aposta > 0
            menor_aposta = min(apostas.values())
            pote_atual = self.potes[-1]
            
            for jogador, valor in list(apostas.items()):
                pote_atual.valor += menor_aposta
                apostas[jogador] -= menor_aposta
                
                # O jogador só é elegível se não tiver dado fold
                if jogador in jogadores_ativos:
                    pote_atual.jogadores_elegiveis.add(jogador)
                    
                if apostas[jogador] == 0:
                    del apostas[jogador]
            
            # Se ainda existem apostas para processar, precisamos criar um Side Pot
            if apostas:
                # Se as apostas restantes são de jogadores que já deram fold (dead money),
                # esse dinheiro simplesmente vai para o pote atual.
                ativos_restantes = [j for j in apostas.keys() if j in jogadores_ativos]
                if len(ativos_restantes) > 0:
                    self.potes.append(Pote())
                else:
                    for jogador, valor_restante in apostas.items():
                        pote_atual.valor += valor_restante
                    apostas.clear()

    def distribuir(self, ranking_jogadores):
        """
        Distribui os potes para os vencedores. Lida com Split Pots e Side Pots.
        ranking_jogadores: list de listas (ou sets) ordenada da melhor mão para a pior.
                           Ex: [["A"], ["B", "C"]] significa que A ganhou. Se A não for elegível ao Side Pot, B e C dividem.
        Retorna: dict {nome_jogador: total_fichas_ganhas}
        """
        pagamentos = {}
        
        for pote in self.potes:
            if pote.valor == 0:
                continue
                
            vencedores_pote = []
            # Procurar do melhor rank (index 0) até o pior
            for rank_group in ranking_jogadores:
                # Interseção: quem deste rank está elegível para este pote?
                vencedores = [j for j in rank_group if j in pote.jogadores_elegiveis]
                if vencedores:
                    vencedores_pote = vencedores
                    break
            
            if not vencedores_pote:
                # Se TODO MUNDO que era elegível a este side pot deu fold
                # o pote é "herdado" pelos jogadores que ainda estão vivos na mão.
                for rank_group in ranking_jogadores:
                    if rank_group:
                        vencedores_pote = rank_group
                        break
                        
            if vencedores_pote:
                qtd_vencedores = len(vencedores_pote)
                premio_base = pote.valor // qtd_vencedores
                fichas_impares = pote.valor % qtd_vencedores
                
                for v in vencedores_pote:
                    pagamentos[v] = pagamentos.get(v, 0) + premio_base
                    
                # A ficha ímpar vai para o primeiro jogador da lista (simplificação da regra real de posição)
                if fichas_impares > 0:
                    pagamentos[vencedores_pote[0]] += fichas_impares
                    
            pote.valor = 0 # Esvazia o pote após distribuir
            
        return pagamentos
