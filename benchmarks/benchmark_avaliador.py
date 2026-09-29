import time
import csv
from core.baralho import Baralho
from core.avaliador_de_maos import AvaliadorDeMaos
from core.avaliador_otimizado import AvaliadorDeMaosOtimizado

def gerar_lote_maos(tamanho_lote):
    maos_para_avaliar = []
    baralho = Baralho()
    for _ in range(tamanho_lote):
        baralho.reseta_baralho()
        mao = []
        for _ in range(7):
            mao.append(baralho.sorteia_uma_carta())
        mao_ordenada = sorted(mao, key=lambda x: x.valor, reverse=True)
        maos_para_avaliar.append(mao_ordenada)
    return maos_para_avaliar

def rodar_benchmark():
    quantidades = [50000, 200000, 1000000, 5000000]
    resultados = []
    
    # Cabeçalho do CSV
    resultados.append(["Quantidade_Maos", "Avaliador", "Tempo_Total_Segundos", "Maos_Por_Segundo"])
    
    tamanho_lote_maximo = 200000
    print(f"Gerando lote base de {tamanho_lote_maximo} mãos para validação e testes...")
    lote_base = gerar_lote_maos(tamanho_lote_maximo)
    
    # PASSO DE VALIDAÇÃO: Garantir que o novo dá a mesma resposta que o antigo
    print("Validando a precisão do Avaliador Otimizado...")
    erros = 0
    for mao in lote_base:
        resultado_antigo = AvaliadorDeMaos.avalia_mao(mao)
        resultado_novo = AvaliadorDeMaosOtimizado.avalia_mao(mao)
        if resultado_antigo != resultado_novo:
            erros += 1
            
    if erros > 0:
        print(f"ERRO FATAL: Encontramos {erros} divergências entre os avaliadores. O teste será abortado.")
        return
    else:
        print("Validação concluída: O Avaliador Otimizado teve 100% de acerto contra o Antigo!\n")
    
    # Executando testes
    avaliadores = [
        ("Antigo", AvaliadorDeMaos.avalia_mao),
        ("Otimizado", AvaliadorDeMaosOtimizado.avalia_mao)
    ]
    
    for nome_avaliador, funcao_avaliar in avaliadores:
        print(f"==== TESTANDO AVALIADOR {nome_avaliador.upper()} ====")
        for qtd in quantidades:
            inicio = time.perf_counter()
            
            restante = qtd
            while restante > 0:
                pedaco = min(restante, tamanho_lote_maximo)
                for i in range(pedaco):
                    funcao_avaliar(lote_base[i])
                restante -= pedaco
                
            fim = time.perf_counter()
            tempo_total = fim - inicio
            maos_por_seg = qtd / tempo_total
            
            print(f"[{qtd} mãos] Tempo total: {tempo_total:.4f}s | Mãos/seg: {maos_por_seg:.2f}")
            resultados.append([qtd, nome_avaliador, f"{tempo_total:.4f}", f"{maos_por_seg:.2f}"])
        print()
        
    with open("resultados_benchmark.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(resultados)
        
    print("Benchmark completo! Os novos tempos foram salvos em 'resultados_benchmark.csv'.")

if __name__ == '__main__':
    rodar_benchmark()
