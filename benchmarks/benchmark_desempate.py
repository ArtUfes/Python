import time
import csv
from core.baralho import Baralho
from core.avaliador_de_maos import AvaliadorDeMaos
from core.avaliador_otimizado import AvaliadorDeMaosOtimizado
from core.jogador import Jogador

def gerar_cenarios_simulacao(tamanho_lote):
    print(f"Gerando lote de {tamanho_lote} simulações de 2 jogadores (mesa completa)...")
    cenarios = []
    baralho = Baralho()
    for _ in range(tamanho_lote):
        baralho.reseta_baralho()
        
        mesa = [baralho.sorteia_uma_carta() for _ in range(5)]
        cartas_p1 = [baralho.sorteia_uma_carta() for _ in range(2)]
        cartas_p2 = [baralho.sorteia_uma_carta() for _ in range(2)]
        
        mao_p1 = sorted(mesa + cartas_p1, key=lambda x: x.valor, reverse=True)
        mao_p2 = sorted(mesa + cartas_p2, key=lambda x: x.valor, reverse=True)
        
        cenarios.append((mao_p1, mao_p2))
    return cenarios

def rodar_benchmark_pipeline_completo():
    quantidades = [10000, 50000, 200000, 1000000]
    resultados = []
    
    resultados.append(["Simulacoes", "Estrategia", "Tempo_Total_Segundos", "Simulacoes_Por_Segundo"])
    
    lote_maximo = 50000
    lote_base = gerar_cenarios_simulacao(lote_maximo)
    
    print("\n==== TESTANDO MODELO ANTIGO (COM FUNCOES DE DESEMPATE) ====")
    for qtd in quantidades:
        inicio = time.perf_counter()
        
        restante = qtd
        while restante > 0:
            pedaco = min(restante, lote_maximo)
            for i in range(pedaco):
                mao_p1, mao_p2 = lote_base[i]
                
                # Setup simulação
                j1 = Jogador("P1")
                j1.mao = mao_p1
                j1.classificacao_mao = AvaliadorDeMaos.avalia_mao(mao_p1)
                
                j2 = Jogador("P2")
                j2.mao = mao_p2
                j2.classificacao_mao = AvaliadorDeMaos.avalia_mao(mao_p2)
                
                # Se empatarem na força base, acionamos o desempate
                if j1.classificacao_mao == j2.classificacao_mao:
                    # O seu pipeline antigo
                    empatados = [j1, j2]
                    AvaliadorDeMaos.encontra_melhor_mao_jogadores(empatados)
                    vencedores = AvaliadorDeMaos.encontra_ganhadores_desempate(empatados)
                else:
                    vencedor = j1 if j1.classificacao_mao > j2.classificacao_mao else j2
                    
            restante -= pedaco
            
        fim = time.perf_counter()
        tempo = fim - inicio
        print(f"[{qtd} sims] Tempo total: {tempo:.4f}s | Sims/seg: {qtd / tempo:.2f}")
        resultados.append([qtd, "Antigo", f"{tempo:.4f}", f"{qtd/tempo:.2f}"])

    print("\n==== TESTANDO MODELO NOVO (TUPLAS NATIVAS SEM DESEMPATE) ====")
    for qtd in quantidades:
        inicio = time.perf_counter()
        
        restante = qtd
        while restante > 0:
            pedaco = min(restante, lote_maximo)
            for i in range(pedaco):
                mao_p1, mao_p2 = lote_base[i]
                
                # Nova abordagem: Avalia já retorna a Tupla de Força
                tupla_p1 = AvaliadorDeMaosOtimizado.avalia_mao(mao_p1)
                tupla_p2 = AvaliadorDeMaosOtimizado.avalia_mao(mao_p2)
                
                # O Python resolve o empate magicamente com um '>' nativo!
                if tupla_p1 > tupla_p2:
                    vencedor = "P1"
                elif tupla_p2 > tupla_p1:
                    vencedor = "P2"
                else:
                    vencedor = "Empate Total"
                    
            restante -= pedaco
            
        fim = time.perf_counter()
        tempo = fim - inicio
        print(f"[{qtd} sims] Tempo total: {tempo:.4f}s | Sims/seg: {qtd / tempo:.2f}")
        resultados.append([qtd, "Otimizado (Tuplas)", f"{tempo:.4f}", f"{qtd/tempo:.2f}"])
        
    with open("resultados_pipeline_monte_carlo.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(resultados)
        
    print("\nBenchmark completo! Salvo em 'resultados_pipeline_monte_carlo.csv'.")

if __name__ == '__main__':
    rodar_benchmark_pipeline_completo()
