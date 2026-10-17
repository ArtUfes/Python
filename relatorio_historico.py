import sys
import os

# Força codificação UTF-8 no terminal Windows
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.gravador_historico import GravadorHistorico

def main():
    gravador = GravadorHistorico("historico_partidas.db")
    
    print("\n" + "="*65)
    print(" [POKER VIP] PAINEL DE ESTATISTICAS E HISTORICO DE MAOS")
    print("="*65)
    
    # 1. Total Geral
    with gravador._get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM maos")
        total_maos = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM acoes_mao")
        total_acoes = c.fetchone()[0]
        c.execute("SELECT DISTINCT nome FROM estatisticas_jogadores")
        jogadores = [r[0] for r in c.fetchall()]

    print(f"\n📁 Banco de Dados: historico_partidas.db")
    print(f"🃏 Mãos Registradas: {total_maos}")
    print(f"⚡ Ações Detalhadas (Pre-Flop até River): {total_acoes}")
    print(f"👥 Jogadores Monitorados: {len(jogadores)}")
    
    if total_maos == 0:
        print("\nNenhuma mão registrada ainda. Jogue algumas rodadas na mesa!")
        return

    # 2. Tabela de Indicadores por Jogador
    print("\n" + "-"*75)
    print(f"{'JOGADOR':<12} | {'MÃOS':<5} | {'VPIP %':<7} | {'PFR %':<7} | {'AF':<5} | {'WTSD %':<7} | {'C-BET %':<7} | {'LUCRO ($)':<9} | {'ARQUÉTIPO'}")
    print("-"*75)
    
    for nome in jogadores:
        m = gravador.obter_metricas_jogador(nome)
        if m:
            print(f"{m['nome']:<12} | {m['total_maos']:<5} | {m['vpip']:<6}% | {m['pfr']:<6}% | {m['af']:<5} | {m['wtsd']:<6}% | {m['cbet']:<6}% | ${m['lucro_total']:<8} | {m['arquetipo']}")
            
    print("-"*75)

    # 3. Exportar Mãos no Padrão PokerStars
    print("\n📄 Deseja exportar o arquivo de texto puro no padrão PokerStars?")
    print("👉 Gerando 'historico_pokerstars.txt' com as últimas 20 mãos...")
    arquivo_txt = gravador.exportar_pokerstars_txt("historico_pokerstars.txt", limit=20)
    print(f"✅ Arquivo salvo com sucesso em: {os.path.abspath(arquivo_txt)}")
    print("   (Você pode abrir esse arquivo no Bloco de Notas ou importar em qualquer Hand Replayer!)")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()
