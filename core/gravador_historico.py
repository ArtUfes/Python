import sqlite3
import os
from datetime import datetime

class GravadorHistorico:
    """
    Gravador de Histórico de Partidas de Poker.
    Persiste cada mão em banco relacional SQLite e gera o formato
    canônico de Hand History compatível com a notação do PokerStars.
    """
    def __init__(self, db_path="historico_partidas.db"):
        self.db_path = db_path
        self._inicializar_banco()
        
    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _inicializar_banco(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Tabela de Mãos (Resumo da Partida)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS maos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo_jogo TEXT DEFAULT 'Holdem No Limit',
                small_blind INTEGER,
                big_blind INTEGER,
                cartas_comunitarias TEXT,
                pote_total INTEGER,
                vencedores TEXT,
                raw_hand_history TEXT
            )
            """)

            # 2. Tabela de Jogadores na Mão
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS mao_jogadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mao_id INTEGER,
                nome TEXT,
                stack_inicial INTEGER,
                posicao_assento INTEGER,
                posicao_mesa TEXT,
                cartas TEXT,
                lucro_liquido INTEGER,
                chegou_showdown BOOLEAN,
                FOREIGN KEY (mao_id) REFERENCES maos(id)
            )
            """)

            # 3. Tabela de Ações Detalhadas (Passo a passo por rodada)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS acoes_mao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mao_id INTEGER,
                rodada TEXT,
                ordem_acao INTEGER,
                jogador TEXT,
                acao TEXT,
                valor INTEGER,
                FOREIGN KEY (mao_id) REFERENCES maos(id)
            )
            """)

            # 4. Tabela de Resumo Agregado por Jogador (Cache instantâneo de métricas)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS estatisticas_jogadores (
                nome TEXT PRIMARY KEY,
                total_maos INTEGER DEFAULT 0,
                vpip_count INTEGER DEFAULT 0,
                pfr_count INTEGER DEFAULT 0,
                saw_flop_count INTEGER DEFAULT 0,
                wtsd_count INTEGER DEFAULT 0,
                wsd_count INTEGER DEFAULT 0,
                total_bets_raises INTEGER DEFAULT 0,
                total_calls INTEGER DEFAULT 0,
                cbet_opps INTEGER DEFAULT 0,
                cbet_done INTEGER DEFAULT 0,
                lucro_total INTEGER DEFAULT 0
            )
            """)

            conn.commit()

    @staticmethod
    def _formatar_carta_pokerstars(carta):
        """Converte carta do formato interno (ex: A♥️, 10♠️) para padrão internacional (Ah, Ts)"""
        simbolo = str(carta.simbolo)
        if simbolo == '10': simbolo = 'T'
        naipe_map = {'♥️': 'h', '♦️': 'd', '♣️': 'c', '♠️': 's'}
        n = naipe_map.get(carta.naipe, 'x')
        return f"{simbolo}{n}"

    def gerar_hand_history_text(self, dados_mao):
        """
        Gera a transcrição textual exata da mão no padrão universal PokerStars.
        """
        hand_id = dados_mao.get('hand_id', int(datetime.now().timestamp()))
        dt_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S ET")
        sb = dados_mao['small_blind']
        bb = dados_mao['big_blind']
        
        lines = []
        lines.append(f"PokerStars Hand #{hand_id}: Hold'em No Limit (${sb}/${bb} USD) - {dt_str}")
        lines.append(f"Table 'VIP Python Club' 4-max Seat #{dados_mao['posicao_button'] + 1} is the button")
        
        # Lista os assentos
        for idx, j in enumerate(dados_mao['jogadores']):
            lines.append(f"Seat {idx + 1}: {j['nome']} (${j['stack_inicial']} in chips)")
            
        # Blinds
        if 'small_blind_player' in dados_mao:
            lines.append(f"{dados_mao['small_blind_player']}: posts small blind ${sb}")
        if 'big_blind_player' in dados_mao:
            lines.append(f"{dados_mao['big_blind_player']}: posts big blind ${bb}")
            
        lines.append("*** HOLE CARDS ***")
        for j in dados_mao['jogadores']:
            cartas_str = " ".join([self._formatar_carta_pokerstars(c) for c in j['cartas']])
            if (j['nome'] == 'Você' or dados_mao.get('revelar_todas', False)) and cartas_str.strip():
                lines.append(f"Dealt to {j['nome']} [{cartas_str}]")

        # Ações street por street (Garante exibição do board mesmo em All-In Pré-Flop)
        acoes = dados_mao.get('acoes', [])
        
        def formatar_linha_acao(acao):
            jog = acao['jogador']
            act = acao['acao'].lower()
            val = acao['valor']
            if act == 'fold':
                return f"{jog}: folds"
            elif act == 'check':
                return f"{jog}: checks"
            elif act == 'call':
                return f"{jog}: calls ${val}"
            elif act == 'raise':
                return f"{jog}: raises to ${val}"
            return f"{jog}: {act} ${val}"

        # 1. PRE-FLOP
        for acao in [a for a in acoes if a['rodada'] == 'PRE_FLOP']:
            lines.append(formatar_linha_acao(acao))

        comunitarias = dados_mao.get('cartas_comunitarias', [])
        total_com = len(comunitarias)

        # 2. FLOP
        if total_com >= 3:
            cartas_flop = " ".join([self._formatar_carta_pokerstars(c) for c in comunitarias[:3]])
            lines.append(f"*** FLOP *** [{cartas_flop}]")
            for acao in [a for a in acoes if a['rodada'] == 'FLOP']:
                lines.append(formatar_linha_acao(acao))

        # 3. TURN
        if total_com >= 4:
            cartas_flop = " ".join([self._formatar_carta_pokerstars(c) for c in comunitarias[:3]])
            turn = self._formatar_carta_pokerstars(comunitarias[3])
            lines.append(f"*** TURN *** [{cartas_flop}] [{turn}]")
            for acao in [a for a in acoes if a['rodada'] == 'TURN']:
                lines.append(formatar_linha_acao(acao))

        # 4. RIVER
        if total_com >= 5:
            board_4 = " ".join([self._formatar_carta_pokerstars(c) for c in comunitarias[:4]])
            river = self._formatar_carta_pokerstars(comunitarias[4])
            lines.append(f"*** RIVER *** [{board_4}] [{river}]")
            for acao in [a for a in acoes if a['rodada'] == 'RIVER']:
                lines.append(formatar_linha_acao(acao))

        # Showdown & Summary (só ocorre se 2 ou mais jogadores chegaram ao showdown)
        jogadores_showdown = [j for j in dados_mao['jogadores'] if j.get('chegou_showdown', False)]
        if dados_mao.get('showdown', False) and len(jogadores_showdown) >= 2:
            lines.append("*** SHOWDOWN ***")
            for j in jogadores_showdown:
                cartas_str = " ".join([self._formatar_carta_pokerstars(c) for c in j['cartas']])
                desc = j.get('desc_mao', '')
                if desc:
                    lines.append(f"{j['nome']}: shows [{cartas_str}] ({desc})")
                elif cartas_str.strip():
                    lines.append(f"{j['nome']}: shows [{cartas_str}]")
                    
        for v in dados_mao.get('vencedores_detalhe', []):
            lines.append(f"{v['nome']} collected ${v['valor']} from pot")
            
        lines.append("*** SUMMARY ***")
        board_str = " ".join([self._formatar_carta_pokerstars(c) for c in dados_mao['cartas_comunitarias']])
        lines.append(f"Total pot ${dados_mao['pote_total']} | Rake $0")
        if board_str:
            lines.append(f"Board [{board_str}]")
        for idx, j in enumerate(dados_mao['jogadores']):
            lucro = j.get('lucro_liquido', 0)
            resultado = f"won (${lucro})" if lucro > 0 else f"lost (${abs(lucro)})"
            lines.append(f"Seat {idx + 1}: {j['nome']} {resultado}")

        return "\n".join(lines)

    def salvar_mao(self, dados_mao):
        """
        Salva atomicamente a mão no SQLite e atualiza agregados.
        """
        raw_text = self.gerar_hand_history_text(dados_mao)
        cartas_mesa_str = " ".join([self._formatar_carta_pokerstars(c) for c in dados_mao['cartas_comunitarias']])
        vencedores_str = ", ".join([v['nome'] for v in dados_mao.get('vencedores_detalhe', [])])
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Inserir Mão
            cursor.execute("""
            INSERT INTO maos (small_blind, big_blind, cartas_comunitarias, pote_total, vencedores, raw_hand_history)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                dados_mao['small_blind'],
                dados_mao['big_blind'],
                cartas_mesa_str,
                dados_mao['pote_total'],
                vencedores_str,
                raw_text
            ))
            mao_id = cursor.lastrowid
            
            # 2. Inserir Jogadores
            for idx, j in enumerate(dados_mao['jogadores']):
                cartas_str = " ".join([self._formatar_carta_pokerstars(c) for c in j['cartas']])
                cursor.execute("""
                INSERT INTO mao_jogadores (mao_id, nome, stack_inicial, posicao_assento, posicao_mesa, cartas, lucro_liquido, chegou_showdown)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mao_id,
                    j['nome'],
                    j['stack_inicial'],
                    idx + 1,
                    j.get('posicao_mesa', ''),
                    cartas_str,
                    j['lucro_liquido'],
                    j['chegou_showdown']
                ))

            # 3. Inserir Ações
            for idx, acao in enumerate(dados_mao['acoes']):
                cursor.execute("""
                INSERT INTO acoes_mao (mao_id, rodada, ordem_acao, jogador, acao, valor)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    mao_id,
                    acao['rodada'],
                    idx + 1,
                    acao['jogador'],
                    acao['acao'],
                    acao['valor']
                ))

            # 4. Atualizar Estatísticas Incrementais (VPIP, PFR, etc)
            self._atualizar_estatisticas_incrementais(cursor, dados_mao)
            
            conn.commit()
            return mao_id

    def _atualizar_estatisticas_incrementais(self, cursor, dados_mao):
        """Atualiza tabela sumarizada com métricas de cada jogador"""
        acoes = dados_mao['acoes']
        
        # Mapeia ações por jogador e rodada
        pre_flop_acoes = [a for a in acoes if a['rodada'] == 'PRE_FLOP']
        agressor_pre_flop = None
        for a in reversed(pre_flop_acoes):
            if a['acao'] == 'RAISE':
                agressor_pre_flop = a['jogador']
                break

        for j in dados_mao['jogadores']:
            nome = j['nome']
            
            # Garante que o jogador existe na tabela de agregados
            cursor.execute("INSERT OR IGNORE INTO estatisticas_jogadores (nome) VALUES (?)", (nome,))
            
            # VPIP: deu Call ou Raise no Pré-Flop
            j_pre_flop = [a for a in pre_flop_acoes if a['jogador'] == nome]
            fez_vpip = any(a['acao'] in ['CALL', 'RAISE'] for a in j_pre_flop)
            fez_pfr = any(a['acao'] == 'RAISE' for a in j_pre_flop)
            
            # Viu o Flop? Se as comunitarias abriram e o jogador nao foldou no pre-flop
            foldou_pre_flop = any(a['jogador'] == nome and a['rodada'] == 'PRE_FLOP' and a['acao'] == 'FOLD' for a in acoes)
            teve_flop = len(dados_mao['cartas_comunitarias']) >= 3
            viu_flop = teve_flop and (not foldou_pre_flop or j['chegou_showdown'])
            
            # WTSD: Went to Showdown (só conta se a mão de fato foi para Showdown entre 2+ jogadores)
            foi_showdown_real = dados_mao.get('showdown', False) and j['chegou_showdown']
            if foi_showdown_real and teve_flop:
                viu_flop = True
            
            # Agressão pós-flop
            pos_flop = [a for a in acoes if a['jogador'] == nome and a['rodada'] != 'PRE_FLOP']
            bets_raises = sum(1 for a in pos_flop if a['acao'] in ['BET', 'RAISE'])
            calls = sum(1 for a in pos_flop if a['acao'] == 'CALL')
            
            # C-Bet
            teve_opp_cbet = (agressor_pre_flop == nome and len(dados_mao['cartas_comunitarias']) >= 3)
            fez_cbet = False
            if teve_opp_cbet:
                flop_acoes_j = [a for a in acoes if a['rodada'] == 'FLOP' and a['jogador'] == nome]
                fez_cbet = any(a['acao'] in ['BET', 'RAISE'] for a in flop_acoes_j)
            
            cursor.execute("""
            UPDATE estatisticas_jogadores
            SET total_maos = total_maos + 1,
                vpip_count = vpip_count + ?,
                pfr_count = pfr_count + ?,
                saw_flop_count = saw_flop_count + ?,
                wtsd_count = wtsd_count + ?,
                wsd_count = wsd_count + ?,
                total_bets_raises = total_bets_raises + ?,
                total_calls = total_calls + ?,
                cbet_opps = cbet_opps + ?,
                cbet_done = cbet_done + ?,
                lucro_total = lucro_total + ?
            WHERE nome = ?
            """, (
                1 if fez_vpip else 0,
                1 if fez_pfr else 0,
                1 if viu_flop else 0,
                1 if (foi_showdown_real and viu_flop) else 0,
                1 if (foi_showdown_real and j['lucro_liquido'] > 0) else 0,
                bets_raises,
                calls,
                1 if teve_opp_cbet else 0,
                1 if fez_cbet else 0,
                j['lucro_liquido'],
                nome
            ))

    def obter_metricas_jogador(self, nome):
        """
        Retorna dicionário com os indicadores prontos para exibição (HUD ou análise)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM estatisticas_jogadores WHERE nome = ?", (nome,))
            row = cursor.fetchone()
            if not row:
                return None
            
            # Indices das colunas
            total_maos = row[1]
            if total_maos == 0:
                return {"nome": nome, "total_maos": 0}
                
            vpip_pct = round((row[2] / total_maos) * 100, 1)
            pfr_pct = round((row[3] / total_maos) * 100, 1)
            wtsd_total = row[5]
            saw_flop = max(row[4], wtsd_total)
            wtsd_pct = min(100.0, round((wtsd_total / saw_flop) * 100, 1)) if saw_flop > 0 else 0.0
            wsd_pct = min(100.0, round((row[6] / wtsd_total) * 100, 1)) if wtsd_total > 0 else 0.0
            
            calls = row[8]
            af = round(row[7] / calls, 2) if calls > 0 else (row[7] if row[7] > 0 else 0.0)
            
            cbet_opps = row[9]
            cbet_pct = round((row[10] / cbet_opps) * 100, 1) if cbet_opps > 0 else 0.0
            
            # Estimativa de BB/100 (considerando BB padrão = 20)
            bb_100 = round((row[11] / 20.0) * (100.0 / total_maos), 1)

            # Classificação de Arquétipo
            arquetipo = "Desconhecido"
            if total_maos >= 10:
                if vpip_pct > 35 and pfr_pct < 15:
                    arquetipo = "Calling Station (Passivo)"
                elif vpip_pct > 32 and pfr_pct >= 22:
                    arquetipo = "Maniac / LAG (Agressivo)"
                elif vpip_pct <= 26 and pfr_pct >= 16:
                    arquetipo = "TAG (Tubarão Regular)"
                elif vpip_pct < 16:
                    arquetipo = "Nit (Ultra Conservador)"
                else:
                    arquetipo = "Balanceado / Recreativo"

            return {
                "nome": nome,
                "total_maos": total_maos,
                "vpip": vpip_pct,
                "pfr": pfr_pct,
                "af": af,
                "wtsd": wtsd_pct,
                "wsd": wsd_pct,
                "cbet": cbet_pct,
                "bb_100": bb_100,
                "lucro_total": row[11],
                "arquetipo": arquetipo
            }

    def exportar_pokerstars_txt(self, arquivo_saida="historico_pokerstars.txt", limit=100):
        """
        Exporta as mãos do banco para um arquivo .txt compatível com PokerTracker e Hand Replayers.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT raw_hand_history FROM maos ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            with open(arquivo_saida, "w", encoding="utf-8") as f:
                for r in reversed(rows):
                    f.write(r[0])
                    f.write("\n\n\n")
            return arquivo_saida
