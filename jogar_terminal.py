import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.mesa import Mesa
from core.jogador import Jogador
from core.bot import Bot
import time

def imprimir_estado_mesa(mesa):
    print("\n" + "="*50)
    print(f"[{mesa.estado_atual}] | POTE TOTAL (Inclui apostas na mesa): {sum(p.valor for p in mesa.gerenciador_pote.potes) + sum(mesa.apostas_rodada.values())}")
    
    print("CARTAS NA MESA: ", end="")
    if not mesa.cartas_na_mesa:
        print("[ Sem Cartas ]")
    else:
        for c in mesa.cartas_na_mesa:
            print(f"[{c.simbolo}{c.naipe}]", end=" ")
        print()
    print("-" * 50)
    
    for j in mesa.jogadores:
        status = ""
        if not j.ativo:
            status = " (FOLD)"
        elif j.is_all_in:
            status = " (ALL-IN)"
            
        aposta = mesa.apostas_rodada.get(j.nome, 0)
        print(f"👤 {j.nome} | Stack: 💰 {j.stack} | Aposta na mesa: 💵 {aposta} {status}")
        
        if j.ativo:
            print("   Cartas: ", end="")
            for c in j.cartas:
                print(f"[{c.simbolo}{c.naipe}]", end=" ")
            print("\n")
    print("="*50)

def main():
    print("♠️ ♥️ BEM-VINDO AO SIMULADOR DE POKER NO TERMINAL ♣️ ♦️")
    
    try:
        num_bots = int(input("Quantos bots você quer na mesa? (ex: 4): ") or "4")
    except ValueError:
        num_bots = 4
        
    mesa = Mesa(small_blind=10, big_blind=20)
    
    mesa.adiciona_jogador(Jogador("Você (Humano)", stack=1000))
    for i in range(num_bots):
        mesa.adiciona_jogador(Bot(f"Bot_{i+1}", stack=1000))
    
    while True:
        mesa.iniciar_mao()
        print("\n\n" + "#"*50)
        print("🃏 NOVA MÃO DISTRIBUÍDA!")
        print("#"*50)
        
        while mesa.estado_atual != "SHOWDOWN":
            rodada_atual = mesa.estado_atual
            
            ativos_livres = [j for j in mesa.jogadores if j.ativo and not j.is_all_in]
            
            if len(ativos_livres) == 0:
                if mesa.estado_atual != "SHOWDOWN":
                    mesa.avancar_rodada()
                continue
            elif len(ativos_livres) == 1:
                # Se só tem um jogador livre, ele só pode agir se ainda dever fichas para pagar o all-in dos outros
                unico_livre = ativos_livres[0]
                falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(unico_livre.nome, 0)
                if falta_pagar == 0:
                    if mesa.estado_atual != "SHOWDOWN":
                        mesa.avancar_rodada()
                    continue

            # Quem começa falando?
            # No pré-flop, quem fala primeiro é o UTG (depois do BB, ou seja, Botão + 3)
            # No pós-flop, quem fala primeiro é o SB (depois do Botão, ou seja, Botão + 1)
            if mesa.estado_atual == "PRE_FLOP":
                idx_atual = (mesa.posicao_button + 3) % len(mesa.jogadores)
            else:
                idx_atual = (mesa.posicao_button + 1) % len(mesa.jogadores)
            
            # Marca que ninguem agiu ainda nesta fase
            jogadores_agiram = {j.nome: False for j in mesa.jogadores}
            
            while mesa.estado_atual == rodada_atual and mesa.estado_atual != "SHOWDOWN":
                j = mesa.jogadores[idx_atual]
                
                # Pula quem já desistiu ou está All-In
                if not j.ativo or j.is_all_in:
                    idx_atual = (idx_atual + 1) % len(mesa.jogadores)
                    
                    # Checagem de segurança (se todos deram all-in depois que a fase começou)
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
                
                # Condição de Fim da Rodada:
                # Se esse jogador já agiu nesta fase, e a aposta dele está igualada à aposta máxima da mesa,
                # significa que a mesa toda rodou e todos pagaram! Avançamos para o Flop/Turn/River.
                if jogadores_agiram[j.nome] and mesa.apostas_rodada.get(j.nome, 0) == mesa.maior_aposta_rodada:
                    mesa.avancar_rodada()
                    break

                imprimir_estado_mesa(mesa)
                
                print(f"\n👉 VEZ DO JOGADOR: {j.nome}")
                falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(j.nome, 0)
                if falta_pagar > 0:
                    print(f"⚠️  Para continuar: 💵 {falta_pagar}")
                else:
                    print("✅ Apostas igualadas. Pode pedir Mesa (Check).")
                    
                if isinstance(j, Bot):
                    acao, valor = j.decidir_acao(mesa)
                    print(f"[{j.nome}] decidiu: {acao} {valor if valor > 0 else ''}")
                    time.sleep(2)  # Pausa dramática
                    
                    if acao == "RAISE":
                        sucesso = mesa.processar_acao(j.nome, acao, valor)
                    else:
                        sucesso = mesa.processar_acao(j.nome, acao)
                        
                    if not sucesso:
                        print(f"❌ Bot tentou ação inválida! Forçando FOLD de segurança.")
                        mesa.processar_acao(j.nome, "FOLD")
                        sucesso = True
                else:
                    print("Opções: [C] Check | [L] Call | [R] Raise | [F] Fold")
                    acao_char = input("Sua ação: ").upper().strip()
                    
                    acao_map = {"C": "CHECK", "L": "CALL", "R": "RAISE", "F": "FOLD"}
                    if acao_char not in acao_map:
                        print("❌ Ação desconhecida. Tente novamente.")
                        continue
                        
                    acao = acao_map[acao_char]
                    
                    if acao == "RAISE":
                        try:
                            valor = int(input("Qual valor TOTAL você quer colocar na mesa? "))
                            sucesso = mesa.processar_acao(j.nome, acao, valor)
                        except ValueError:
                            print("❌ Valor numérico inválido.")
                            sucesso = False
                    else:
                        sucesso = mesa.processar_acao(j.nome, acao)
                        
                    if not sucesso:
                        print("\n❌ Jogada bloqueada pelo Motor de Regras! (Tentou dar Check devendo fichas, ou o valor do Raise foi abaixo do mínimo).")
                        input("Aperte ENTER para tentar novamente...")
                
                if sucesso:
                    jogadores_agiram[j.nome] = True
                    
                    # Se você der Raise, TODOS os outros jogadores na mesa tem que falar DE NOVO!
                    if acao == "RAISE":
                        for outro in mesa.jogadores:
                            if outro.nome != j.nome:
                                jogadores_agiram[outro.nome] = False
                                
                    idx_atual = (idx_atual + 1) % len(mesa.jogadores)

        print("\n\n" + "🏆 "*15)
        print("SHOWDOWN!")
        print("🏆 "*15)
        mesa.executar_showdown()
        imprimir_estado_mesa(mesa)
        
        resp = input("\nJogar outra mão? (S/N): ").strip().upper()
        if resp != 'S':
            break

if __name__ == "__main__":
    main()
