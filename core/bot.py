import random
from core.jogador import Jogador
from core.carta import Carta
from core.baralho import Baralho
from core.avaliador_otimizado import AvaliadorDeMaosOtimizado

class Bot(Jogador):
    def __init__(self, nome, stack=0, agressividade=1.0, genes=None):
        super().__init__(nome, stack)
        self.agressividade = agressividade  # Fator que multiplica as apostas do bot
        
        # DNA Padrão (ABC Poker) se nenhum gene for passado
        self.genes = genes or {
            "forca_open_raise": 1.2,
            "forca_call_overbet": 1.8,
            "agressividade_raise": 2.5,
            "taxa_blefe": 0.05,
            "taxa_slowplay": 0.0
        }

    def _calcular_equidade(self, mesa, num_simulacoes=1000):
        # 1. Identificar cartas conhecidas
        cartas_conhecidas = set([c.simbolo for c in self.cartas] + [c.simbolo for c in mesa.cartas_na_mesa])
        
        # 2. Criar deck com cartas restantes
        baralho = Baralho()
        cartas_restantes = [c for c in baralho.cartas if c.simbolo not in cartas_conhecidas]
        
        num_oponentes = len([j for j in mesa.jogadores if j.ativo and j.nome != self.nome])
        if num_oponentes == 0:
            return 1.0  # Se não há oponentes, vitória garantida
            
        cartas_mesa_faltantes = 5 - len(mesa.cartas_na_mesa)
        
        vitorias = 0
        empates = 0
        
        for _ in range(num_simulacoes):
            # Embaralhar cópia
            deck_simulacao = random.sample(cartas_restantes, len(cartas_restantes))
            
            # Completar mesa
            mesa_simulada = mesa.cartas_na_mesa.copy()
            for _ in range(cartas_mesa_faltantes):
                mesa_simulada.append(deck_simulacao.pop())
                
            # Avaliar mão do bot
            mao_bot = self.cartas + mesa_simulada
            score_bot = AvaliadorDeMaosOtimizado.avalia_mao(mao_bot)
            
            # Distribuir e avaliar oponentes
            ganhou = True
            empatou_com = 0
            
            for _ in range(num_oponentes):
                cartas_oponente = [deck_simulacao.pop(), deck_simulacao.pop()]
                mao_oponente = cartas_oponente + mesa_simulada
                score_oponente = AvaliadorDeMaosOtimizado.avalia_mao(mao_oponente)
                
                if score_oponente > score_bot:
                    ganhou = False
                    break
                elif score_oponente == score_bot:
                    empatou_com += 1
            
            if ganhou:
                if empatou_com > 0:
                    empates += 1.0 / (empatou_com + 1)
                else:
                    vitorias += 1
                    
        return (vitorias + empates) / num_simulacoes

    def decidir_acao(self, mesa):
        if not self.ativo or self.is_all_in:
            return "CHECK", 0

        equidade = self._calcular_equidade(mesa, num_simulacoes=2000)
        falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(self.nome, 0)
        pote_total = sum(p.valor for p in mesa.gerenciador_pote.potes) + sum(mesa.apostas_rodada.values())
        
        print(f"🤖 [BOT {self.nome}] Calculando... Equidade estimada: {equidade*100:.1f}%")

        num_oponentes = len([j for j in mesa.jogadores if j.ativo and j.nome != self.nome])
        if num_oponentes == 0:
            return "CHECK", 0
            
        equidade_media = 1.0 / (num_oponentes + 1)
        forca_relativa = equidade / equidade_media 

        # SLOWPLAY: Mão Monstruosa disfarçada (apenas paga ou passa a vez para induzir blefes)
        if equidade > 0.85 and falta_pagar <= (mesa.big_blind if hasattr(mesa, 'big_blind') else 20):
            if random.random() < self.genes["taxa_slowplay"]:
                return ("CALL", falta_pagar) if falta_pagar > 0 else ("CHECK", 0)

        if falta_pagar == 0:
            if forca_relativa > self.genes["forca_open_raise"]:
                valor = int((pote_total * 0.5) * self.genes["agressividade_raise"] * self.agressividade)
                valor = max(mesa.maior_aposta_rodada * 2, valor) if mesa.maior_aposta_rodada > 0 else max(20, valor)
                valor = min(self.stack, valor)
                return "RAISE", mesa.apostas_rodada.get(self.nome, 0) + valor
            else:
                return "CHECK", 0
                
        # Se tem aposta para pagar
        pot_odds = falta_pagar / (pote_total + falta_pagar) if (pote_total + falta_pagar) > 0 else 1.0
        
        limite_forca = 0.95 
        if falta_pagar > 20: limite_forca = 1.2
        if falta_pagar > pote_total: limite_forca = 1.4
        if falta_pagar >= self.stack * 0.4: limite_forca = self.genes["forca_call_overbet"]
            
        if equidade > pot_odds or forca_relativa >= limite_forca: 
            if forca_relativa > 1.8:
                valor = int(falta_pagar * self.genes["agressividade_raise"] * self.agressividade)
                valor = min(self.stack, valor)
                valor_total = mesa.apostas_rodada.get(self.nome, 0) + falta_pagar + valor
                if valor > 0 and valor_total > falta_pagar:
                    return "RAISE", valor_total
            return "CALL", falta_pagar
        else:
            if forca_relativa < 0.5 and random.random() < self.genes["taxa_blefe"]:
                valor_total = mesa.apostas_rodada.get(self.nome, 0) + falta_pagar + int(pote_total * 0.7)
                return "RAISE", valor_total
            return "FOLD", 0
