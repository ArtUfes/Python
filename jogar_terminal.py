import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.mesa import Mesa
from core.jogador import Jogador

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
    mesa = Mesa(small_blind=10, big_blind=20)
    j1 = Jogador("J1", stack=1000)
    j2 = Jogador("J2", stack=1000)
    mesa.adiciona_jogador(j1)
    mesa.adiciona_jogador(j2)
    
    while True:
        mesa.iniciar_mao()
        print("\n\n" + "#"*50)
        print("🃏 NOVA MÃO DISTRIBUÍDA!")
        print("#"*50)
        
        while mesa.estado_atual != "SHOWDOWN":
            rodada_atual = mesa.estado_atual
            
            ativos_livres = [j for j in mesa.jogadores if j.ativo and not j.is_all_in]
            
            if len(ativos_livres) <= 1:
                # Se sobrou no máximo 1 pessoa não All-in, avança a fase sem pedir ações
                if mesa.estado_atual != "SHOWDOWN":
                    mesa.avancar_rodada()
                continue

            # Quem começa falando? O SB (jogador logo à esquerda do botão)
            idx_atual = (mesa.posicao_button + 1) % len(mesa.jogadores)
            
            # Marca que ninguem agiu ainda nesta fase
            jogadores_agiram = {j.nome: False for j in mesa.jogadores}
            
            while mesa.estado_atual == rodada_atual and mesa.estado_atual != "SHOWDOWN":
                j = mesa.jogadores[idx_atual]
                
                # Pula quem já desistiu ou está All-In
                if not j.ativo or j.is_all_in:
                    idx_atual = (idx_atual + 1) % len(mesa.jogadores)
                    
                    # Checagem de segurança (se todos deram all-in depois que a fase começou)
                    if len([x for x in mesa.jogadores if x.ativo and not x.is_all_in]) <= 1:
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
                    print(f"⚠️  Você precisa pagar para continuar: 💵 {falta_pagar}")
                else:
                    print("✅ Suas apostas estão igualadas com a mesa. Você pode pedir Mesa (Check).")
                    
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
                else:
                    jogadores_agiram[j.nome] = True
                    
                    # O pulo do gato do Texas Hold'em:
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
