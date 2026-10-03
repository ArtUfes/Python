import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.mesa import Mesa
from core.jogador import Jogador
from core.bot import Bot

# PERSONAS DE TESTE
class BotManiaco(Jogador):
    def decidir_acao(self, mesa):
        if not self.ativo or self.is_all_in: return "CHECK", 0
        falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(self.nome, 0)
        pote_total = sum(p.valor for p in mesa.gerenciador_pote.potes) + sum(mesa.apostas_rodada.values())
        
        # 30% de chance de dar um raise absurdo
        if random.random() < 0.3:
            valor_raise = mesa.apostas_rodada.get(self.nome, 0) + falta_pagar + pote_total + 100
            return "RAISE", min(self.stack, valor_raise)
            
        if falta_pagar > 0:
            return "CALL", falta_pagar
        return "RAISE", mesa.apostas_rodada.get(self.nome, 0) + 50

class BotMedroso(Jogador):
    def decidir_acao(self, mesa):
        if not self.ativo or self.is_all_in: return "CHECK", 0
        falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(self.nome, 0)
        
        if falta_pagar > 0:
            return "FOLD", 0
        return "CHECK", 0

class BotCallingStation(Jogador):
    def decidir_acao(self, mesa):
        if not self.ativo or self.is_all_in: return "CHECK", 0
        falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(self.nome, 0)
        
        if falta_pagar > 0:
            return "CALL", falta_pagar
        return "CHECK", 0

def main():
    print("Iniciando Campo de Treinamento Automatizado (100 Mãos)...")
    mesa = Mesa(small_blind=10, big_blind=20)
    
    # 50.000 fichas para termos profundidade para 100 mãos
    b_prof = Bot("ProBot", stack=50000, agressividade=1.0)
    b_maniaco = BotManiaco("Maniaco", stack=50000)
    b_medroso = BotMedroso("Nit", stack=50000)
    b_station1 = BotCallingStation("Station_1", stack=50000)
    b_station2 = BotCallingStation("Station_2", stack=50000)
    
    mesa.adiciona_jogador(b_prof)
    mesa.adiciona_jogador(b_maniaco)
    mesa.adiciona_jogador(b_medroso)
    mesa.adiciona_jogador(b_station1)
    mesa.adiciona_jogador(b_station2)
    
    num_maos = 50
    
    with open("historico_treinamento.txt", "w", encoding="utf-8") as log_file:
        for i in range(num_maos):
            # Recarga automática de stack (rebuy) para os bots não morrerem antes do fim
            for j in mesa.jogadores:
                if j.stack <= 0:
                    j.stack = 10000
                    log_file.write(f"\n[REBUY] {j.nome} recarregou 10.000 fichas!\n")
            
            mesa.iniciar_mao()
            log_file.write(f"\n" + "="*40 + f"\n--- MÃO {i+1} ---\n")
            
            while mesa.estado_atual != "SHOWDOWN":
                rodada_atual = mesa.estado_atual
                
                ativos_livres = [j for j in mesa.jogadores if j.ativo and not j.is_all_in]
                if len(ativos_livres) == 0:
                    if mesa.estado_atual != "SHOWDOWN": mesa.avancar_rodada()
                    continue
                elif len(ativos_livres) == 1:
                    unico_livre = ativos_livres[0]
                    falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(unico_livre.nome, 0)
                    if falta_pagar == 0:
                        if mesa.estado_atual != "SHOWDOWN": mesa.avancar_rodada()
                        continue

                if mesa.estado_atual == "PRE_FLOP":
                    idx_atual = (mesa.posicao_button + 3) % len(mesa.jogadores)
                else:
                    idx_atual = (mesa.posicao_button + 1) % len(mesa.jogadores)
                
                jogadores_agiram = {j.nome: False for j in mesa.jogadores}
                
                while mesa.estado_atual == rodada_atual and mesa.estado_atual != "SHOWDOWN":
                    j = mesa.jogadores[idx_atual]
                    
                    if not j.ativo or j.is_all_in:
                        idx_atual = (idx_atual + 1) % len(mesa.jogadores)
                        ativos_livres = [x for x in mesa.jogadores if x.ativo and not x.is_all_in]
                        if len(ativos_livres) == 0:
                            mesa.avancar_rodada()
                            break
                        elif len(ativos_livres) == 1:
                            unico_livre = ativos_livres[0]
                            falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(unico_livre.nome, 0)
                            if falta_pagar == 0:
                                mesa.avancar_rodada()
                                break
                        continue
                    
                    if jogadores_agiram[j.nome] and mesa.apostas_rodada.get(j.nome, 0) == mesa.maior_aposta_rodada:
                        mesa.avancar_rodada()
                        break

                    # Chama o bot
                    if isinstance(j, Bot):
                        # Desativa prints para o terminal não poluir muito (evitando erro de emoji no Windows)
                        sys.stdout = open(os.devnull, 'w', encoding='utf-8')
                        acao, valor = j.decidir_acao(mesa)
                        sys.stdout = sys.__stdout__
                    else:
                        acao, valor = j.decidir_acao(mesa)
                        
                    # Tratamento se ele pedir CALL 0 vira CHECK
                    if acao == "CALL" and valor == 0: acao = "CHECK"
                    
                    log_file.write(f"[{mesa.estado_atual}] {j.nome} faz {acao} {valor}\n")
                    
                    if acao == "RAISE":
                        sucesso = mesa.processar_acao(j.nome, acao, valor)
                    else:
                        sucesso = mesa.processar_acao(j.nome, acao)
                        
                    if not sucesso:
                        mesa.processar_acao(j.nome, "FOLD")
                        log_file.write(f"{j.nome} tentou {acao} inválido. FOLD forcado.\n")
                        sucesso = True
                    
                    jogadores_agiram[j.nome] = True
                    if acao == "RAISE":
                        for outro in mesa.jogadores:
                            if outro.nome != j.nome: jogadores_agiram[outro.nome] = False
                                    
                    idx_atual = (idx_atual + 1) % len(mesa.jogadores)

            mesa.executar_showdown()
            
            log_file.write(f"--- FIM DA MÃO ---\n")
            log_file.write(f"Stacks: {[f'{x.nome}: {x.stack}' for x in mesa.jogadores]}\n")

    print("\n=============================================")
    print("RESULTADO FINAL DAS 50 MAOS")
    print("=============================================")
    # Ordenar por lucro (Stack atual vs Inicial)
    jogadores_ordenados = sorted(mesa.jogadores, key=lambda x: x.stack, reverse=True)
    for j in jogadores_ordenados:
        lucro = j.stack - 50000
        sinal = "+" if lucro >= 0 else ""
        print(f"{j.nome:<12} | Stack: {j.stack:<8} | Lucro: {sinal}{lucro}")
    print("=============================================")
    print("Historico completo salvo em 'historico_treinamento.txt'.")

if __name__ == "__main__":
    main()
