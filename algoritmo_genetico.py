import sys
import os
import random
import json
from copy import deepcopy

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.mesa import Mesa
from core.bot import Bot
from simulador_treinamento import BotManiaco, BotMedroso, BotCallingStation

NUM_GERACOES = 10
TAMANHO_POPULACAO = 15
MAOS_POR_TORNEIO = 30
FICHAS_INICIAIS = 10000

def gerar_genes_aleatorios():
    return {
        "forca_open_raise": round(random.uniform(0.8, 2.0), 2),
        "forca_call_overbet": round(random.uniform(1.2, 3.0), 2),
        "agressividade_raise": round(random.uniform(1.0, 5.0), 2),
        "taxa_blefe": round(random.uniform(0.0, 0.3), 2),
        "taxa_slowplay": round(random.uniform(0.0, 0.4), 2)
    }

def mutar_genes(genes):
    filho = deepcopy(genes)
    if random.random() < 0.3: filho["forca_open_raise"] *= random.uniform(0.8, 1.2)
    if random.random() < 0.3: filho["forca_call_overbet"] *= random.uniform(0.8, 1.2)
    if random.random() < 0.3: filho["agressividade_raise"] *= random.uniform(0.8, 1.2)
    if random.random() < 0.3: filho["taxa_blefe"] = min(0.5, filho["taxa_blefe"] + random.uniform(-0.05, 0.1))
    if random.random() < 0.3: filho["taxa_slowplay"] = min(0.5, filho["taxa_slowplay"] + random.uniform(-0.05, 0.1))
    
    filho["taxa_blefe"] = max(0.0, filho["taxa_blefe"])
    filho["taxa_slowplay"] = max(0.0, filho["taxa_slowplay"])
    
    # Arredondar para facilitar leitura
    for k in filho: filho[k] = round(filho[k], 2)
    return filho

def cruzar_genes(g1, g2):
    filho = {}
    for k in g1.keys():
        filho[k] = g1[k] if random.random() < 0.5 else g2[k]
    return mutar_genes(filho)

def rodar_mesa(bots, maos):
    mesa = Mesa(small_blind=10, big_blind=20)
    for b in bots:
        b.stack = FICHAS_INICIAIS
        mesa.adiciona_jogador(b)
        
    devnull = open(os.devnull, 'w', encoding='utf-8')
    old_stdout = sys.stdout
    sys.stdout = devnull
    
    try:
        for _ in range(maos):
            for j in mesa.jogadores:
                if j.stack <= 0: j.stack = FICHAS_INICIAIS
            
            mesa.iniciar_mao()
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

                idx_atual = (mesa.posicao_button + (3 if mesa.estado_atual == "PRE_FLOP" else 1)) % len(mesa.jogadores)
                jogadores_agiram = {j.nome: False for j in mesa.jogadores}
                
                while mesa.estado_atual == rodada_atual and mesa.estado_atual != "SHOWDOWN":
                    j = mesa.jogadores[idx_atual]
                    
                    if not j.ativo or j.is_all_in:
                        idx_atual = (idx_atual + 1) % len(mesa.jogadores)
                        ativos_livres = [x for x in mesa.jogadores if x.ativo and not x.is_all_in]
                        if len(ativos_livres) == 0 or (len(ativos_livres) == 1 and mesa.maior_aposta_rodada == mesa.apostas_rodada.get(ativos_livres[0].nome, 0)):
                            mesa.avancar_rodada()
                            break
                        continue
                    
                    if jogadores_agiram[j.nome] and mesa.apostas_rodada.get(j.nome, 0) == mesa.maior_aposta_rodada:
                        mesa.avancar_rodada()
                        break

                    acao, valor = j.decidir_acao(mesa)
                    if acao == "CALL" and valor == 0: acao = "CHECK"
                    
                    sucesso = mesa.processar_acao(j.nome, acao, valor) if acao == "RAISE" else mesa.processar_acao(j.nome, acao)
                    if not sucesso: mesa.processar_acao(j.nome, "FOLD")
                    
                    jogadores_agiram[j.nome] = True
                    if acao == "RAISE":
                        for outro in mesa.jogadores:
                            if outro.nome != j.nome: jogadores_agiram[outro.nome] = False
                    
                    idx_atual = (idx_atual + 1) % len(mesa.jogadores)

            mesa.executar_showdown()
    finally:
        sys.stdout = old_stdout
        devnull.close()

def main():
    print("Iniciando Laboratorio Genetico (Evolucao do ProBot)...")
    
    # População inicial
    populacao = [{"id": i, "genes": gerar_genes_aleatorios(), "lucro": 0} for i in range(TAMANHO_POPULACAO)]
    
    for geracao in range(NUM_GERACOES):
        print(f"\n--- GERACAO {geracao + 1}/{NUM_GERACOES} ---")
        
        for ind in populacao: ind["lucro"] = 0
        random.shuffle(populacao)
        
        # Mesas de 3 ProBots + 1 Maniaco + 1 Station
        for i in range(0, TAMANHO_POPULACAO, 3):
            grupo = populacao[i:i+3]
            if len(grupo) < 3: break
            
            bots = []
            for ind in grupo:
                bots.append(Bot(f"Gen_{ind['id']}", genes=ind["genes"]))
            
            bots.append(BotManiaco("Maniaco"))
            bots.append(BotCallingStation("Station"))
            
            rodar_mesa(bots, MAOS_POR_TORNEIO)
            
            for b in bots:
                if b.nome.startswith("Gen_"):
                    idx = int(b.nome.split("_")[1])
                    for ind in grupo:
                        if ind["id"] == idx:
                            ind["lucro"] = b.stack - FICHAS_INICIAIS

        populacao.sort(key=lambda x: x["lucro"], reverse=True)
        print(f"Melhor da Geracao: ID {populacao[0]['id']} | Lucro: {populacao[0]['lucro']}")
        print(f"Genes do Campeao: {populacao[0]['genes']}")
        
        nova_populacao = []
        
        # 1. Elitismo (Top 3)
        elite = populacao[:3]
        for ind in elite:
            nova_populacao.append({"id": ind["id"], "genes": deepcopy(ind["genes"]), "lucro": 0})
            
        # 2. Imigração (2 Aliens)
        for _ in range(2):
            nova_populacao.append({"id": random.randint(1000, 9999), "genes": gerar_genes_aleatorios(), "lucro": 0})
            
        # 3. Cruzamento
        while len(nova_populacao) < TAMANHO_POPULACAO:
            p1 = random.choice(elite)["genes"]
            p2 = random.choice(populacao[:int(TAMANHO_POPULACAO * 0.5)])["genes"]
            filho = cruzar_genes(p1, p2)
            nova_populacao.append({"id": random.randint(1000, 9999), "genes": filho, "lucro": 0})
            
        populacao = nova_populacao

    print("\n===============================")
    print("EVOLUCAO CONCLUIDA!")
    best = populacao[0]
    print(f"DNA SUPREMO (ID {best['id']}):")
    print(json.dumps(best["genes"], indent=4))
    
    with open("dna_supremo.json", "w") as f:
        json.dump(best["genes"], f, indent=4)
    print("DNA salvo em 'dna_supremo.json'!")

if __name__ == "__main__":
    main()
