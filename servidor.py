import sys
import os
import json
import time
from threading import Thread, Event
from flask import Flask, send_file, jsonify
from flask_socketio import SocketIO, emit

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.mesa import Mesa
from core.jogador import Jogador
from core.bot import Bot
from core.gravador_historico import GravadorHistorico
from core.perfil import GerenciadorPerfil
from core.avaliador_otimizado import AvaliadorDeMaosOtimizado

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

gravador = GravadorHistorico()
gerenciador_perfil = GerenciadorPerfil()

mesa = None
humano = None
jogo_rodando = False
thread_jogo = None
esperando_humano = Event()
acao_humano = None
valor_humano = 0
turno_atual = None

# Configurações ativas da sessão
config_sessao = {
    "small_blind": 10,
    "big_blind": 20,
    "buy_in": 1000
}

@app.route('/api/perfil', methods=['GET'])
def api_obter_perfil():
    return jsonify(gerenciador_perfil.obter_perfil("Você"))

@app.route('/api/historico-txt', methods=['GET'])
def api_download_historico():
    caminho = "historico_pokerstars.txt"
    if os.path.exists(caminho):
        return send_file(caminho, as_attachment=True, download_name="historico_pokerstars.txt")
    return jsonify({"erro": "Histórico ainda não disponível."}), 404

def empacotar_estado():
    if not mesa:
        return {}
    estado = {
        "estado_atual": mesa.estado_atual,
        "pote_total": sum(p.valor for p in mesa.gerenciador_pote.potes) + sum(mesa.apostas_rodada.values()),
        "maior_aposta": mesa.maior_aposta_rodada,
        "cartas_na_mesa": [f"{c.simbolo}{c.naipe}" for c in mesa.cartas_na_mesa],
        "turno_atual": turno_atual,
        "small_blind": mesa.small_blind,
        "big_blind": mesa.big_blind,
        "jogadores": []
    }
    for j in mesa.jogadores:
        estado["jogadores"].append({
            "nome": j.nome,
            "stack": j.stack,
            "aposta": mesa.apostas_rodada.get(j.nome, 0),
            "ativo": j.ativo,
            "is_all_in": j.is_all_in,
            # Esconde as cartas dos bots a menos que seja showdown
            "cartas": [f"{c.simbolo}{c.naipe}" for c in j.cartas] if j.nome == "Você" or mesa.estado_atual == "SHOWDOWN" else ["?", "?"]
        })
    return estado

def emitir_estado():
    socketio.emit('estado_mesa', empacotar_estado())

def loop_do_jogo():
    global mesa, humano, jogo_rodando, acao_humano, valor_humano, turno_atual

    sb = config_sessao.get("small_blind", 10)
    bb = config_sessao.get("big_blind", 20)
    buy_in = config_sessao.get("buy_in", 1000)

    # Inicia a Mesa com os blinds e stack configurados
    mesa = Mesa(small_blind=sb, big_blind=bb)
    humano = Jogador("Você", stack=buy_in)

    # Carregar o DNA supremo dos bots se existir
    genes_supremos = None
    if os.path.exists("dna_supremo.json"):
        with open("dna_supremo.json", "r") as f:
            genes_supremos = json.load(f)

    bot_stack = max(bb * 50, buy_in)
    b1 = Bot("ProBot_1", stack=bot_stack, genes=genes_supremos)
    b2 = Bot("ProBot_2", stack=bot_stack, genes=genes_supremos)
    b3 = Bot("ProBot_3", stack=bot_stack, genes=genes_supremos)

    mesa.adiciona_jogador(humano)
    mesa.adiciona_jogador(b1)
    mesa.adiciona_jogador(b2)
    mesa.adiciona_jogador(b3)

    while jogo_rodando:
        mesa.iniciar_mao()
        emitir_estado()
        time.sleep(1.5) # Pausa dramática para o frontend animar as cartas

        if not jogo_rodando:
            break

        ativos_iniciais = [j for j in mesa.jogadores if j.ativo]
        sb_nome = ativos_iniciais[(mesa.posicao_button + 1) % len(ativos_iniciais)].nome if len(ativos_iniciais) >= 2 else ""
        bb_nome = ativos_iniciais[(mesa.posicao_button + 2) % len(ativos_iniciais)].nome if len(ativos_iniciais) >= 2 else ""

        stacks_iniciais = {j.nome: j.stack + mesa.apostas_rodada.get(j.nome, 0) for j in mesa.jogadores}
        cartas_iniciais = {j.nome: list(j.cartas) for j in mesa.jogadores}
        acoes_historico = []

        while mesa.estado_atual != "SHOWDOWN":
            if not jogo_rodando:
                break

            rodada_atual = mesa.estado_atual
            ativos_livres = [j for j in mesa.jogadores if j.ativo and not j.is_all_in]

            if len(ativos_livres) == 0:
                if mesa.estado_atual != "SHOWDOWN":
                    mesa.avancar_rodada()
                continue
            elif len(ativos_livres) == 1:
                unico_livre = ativos_livres[0]
                falta = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(unico_livre.nome, 0)
                if falta == 0:
                    if mesa.estado_atual != "SHOWDOWN":
                        mesa.avancar_rodada()
                    continue

            idx_atual = (mesa.posicao_button + (3 if mesa.estado_atual == "PRE_FLOP" else 1)) % len(mesa.jogadores)
            jogadores_agiram = {j.nome: False for j in mesa.jogadores}

            while mesa.estado_atual == rodada_atual and mesa.estado_atual != "SHOWDOWN":
                if not jogo_rodando:
                    break

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

                turno_atual = j.nome
                emitir_estado()

                falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(j.nome, 0)

                if j.nome == "Você":
                    socketio.emit('pedir_acao', {"falta_pagar": falta_pagar, "maior_aposta": mesa.maior_aposta_rodada})
                    agiu_no_tempo = esperando_humano.wait(timeout=10.0)
                    if not jogo_rodando:
                        break

                    if agiu_no_tempo:
                        acao, valor = acao_humano, valor_humano
                        esperando_humano.clear()
                    else:
                        if falta_pagar > 0:
                            acao, valor = "FOLD", 0
                        else:
                            acao, valor = "CHECK", 0
                        esperando_humano.clear()
                        socketio.emit('mensagem', "⏳ Tempo esgotado! Ação automática.")
                else:
                    import random
                    r = random.random()
                    if r < 0.80:
                        wait_time = random.uniform(2, 7)
                    elif r < 0.95:
                        wait_time = 1.0
                    else:
                        wait_time = random.uniform(8, 10)
                    
                    # Dorme em fatias curtas de 0.1s para responder imediatamente a pedidos de saída
                    passos = int(wait_time / 0.1)
                    for _ in range(passos):
                        if not jogo_rodando:
                            break
                        time.sleep(0.1)

                    if not jogo_rodando:
                        break

                    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
                    acao, valor = j.decidir_acao(mesa)
                    sys.stdout = sys.__stdout__

                turno_atual = None
                if acao == "CALL" and valor == 0:
                    acao = "CHECK"

                sucesso, acao_real, valor_real = mesa.processar_acao(j.nome, acao, valor) if acao == "RAISE" else mesa.processar_acao(j.nome, acao)
                if not sucesso:
                    _, acao_real, valor_real = mesa.processar_acao(j.nome, "FOLD")

                acoes_historico.append({
                    'rodada': rodada_atual,
                    'jogador': j.nome,
                    'acao': acao_real,
                    'valor': valor_real
                })

                msg_valor = f" ${valor_real}" if valor_real > 0 else ""
                socketio.emit('mensagem', f"{j.nome} deu {acao_real}{msg_valor}")
                socketio.emit('acao_executada', {'jogador': j.nome, 'acao': acao_real, 'valor': valor_real})

                if acao_real in ["CALL", "RAISE"] and valor_real > 0:
                    socketio.emit('animar_fichas', {'de': j.nome, 'para': 'centro', 'valor': valor_real})

                jogadores_agiram[j.nome] = True
                if acao_real == "RAISE":
                    for outro in mesa.jogadores:
                        if outro.nome != j.nome:
                            jogadores_agiram[outro.nome] = False

                idx_atual = (idx_atual + 1) % len(mesa.jogadores)

        if not jogo_rodando:
            break

        pote_final_calculado = sum(p.valor for p in mesa.gerenciador_pote.potes) + sum(mesa.apostas_rodada.values())
        ranking, pagamentos = mesa.executar_showdown()
        emitir_estado()

        vencedores_detalhe = []
        humano_venceu = False
        if ranking:
            vencedores = " e ".join(ranking[0])
            if "Você" in ranking[0]:
                humano_venceu = True
            jogador_exemplo = next(j for j in mesa.jogadores if j.nome == ranking[0][0])
            cartas_str = " ".join([f"[{c.simbolo}{c.naipe}]" for c in jogador_exemplo.cartas])
            nome_mao = AvaliadorDeMaosOtimizado.imprimir_mao(jogador_exemplo.classificacao_mao)
            socketio.emit('mensagem', f"🏆 {vencedores} ganhou com {nome_mao}! (Mão: {cartas_str})")

        for nome, valor in pagamentos.items():
            if valor > 0:
                vencedores_detalhe.append({'nome': nome, 'valor': valor})
                socketio.emit('mensagem', f"💰 {nome} recolheu ${valor}")
                socketio.emit('animar_fichas', {'de': 'centro', 'para': nome, 'valor': valor})

        # Atualiza métricas e histórico no banco SQLite
        gerenciador_perfil.registrar_mao_jogada(venceu=humano_venceu, nome="Você")

        try:
            ativos_finais = [j for j in mesa.jogadores if j.ativo]
            houve_showdown = len(ativos_finais) >= 2

            dados_para_salvar = {
                'small_blind': mesa.small_blind,
                'big_blind': mesa.big_blind,
                'posicao_button': mesa.posicao_button,
                'small_blind_player': sb_nome,
                'big_blind_player': bb_nome,
                'cartas_comunitarias': list(mesa.cartas_na_mesa),
                'pote_total': pote_final_calculado,
                'showdown': houve_showdown,
                'jogadores': [
                    {
                        'nome': j.nome,
                        'stack_inicial': stacks_iniciais.get(j.nome, j.stack),
                        'cartas': list(cartas_iniciais.get(j.nome, j.cartas)),
                        'lucro_liquido': j.stack - stacks_iniciais.get(j.nome, j.stack),
                        'chegou_showdown': j.ativo and houve_showdown,
                        'desc_mao': AvaliadorDeMaosOtimizado.imprimir_mao(j.classificacao_mao) if (getattr(j, 'classificacao_mao', None) and houve_showdown) else ""
                    }
                    for j in mesa.jogadores
                ],
                'acoes': acoes_historico,
                'vencedores_detalhe': vencedores_detalhe
            }
            gravador.salvar_mao(dados_para_salvar)

            metricas_humano = gravador.obter_metricas_jogador("Você")
            if metricas_humano:
                socketio.emit('metricas_jogador', metricas_humano)
        except Exception as e:
            print("Erro ao gravar histórico da mão:", e)

        # Emite perfil atualizado para manter o HUD/Header sincronizado
        socketio.emit('perfil_atualizado', gerenciador_perfil.obter_perfil("Você"))

        # Checa se o jogador humano faliu na mesa
        if humano and humano.stack <= 0:
            socketio.emit('jogador_falido', {
                "mensagem": "Suas fichas na mesa acabaram!",
                "bankroll": gerenciador_perfil.obter_perfil("Você")["bankroll"]
            })
            jogo_rodando = False
            break

        # Limpar bots falidos (Rebuy automático dos bots)
        for j in mesa.jogadores:
            if j.nome != "Você" and j.stack <= 0:
                j.stack = max(bb * 50, buy_in)
                socketio.emit('mensagem', f"{j.nome} fez Rebuy de ${j.stack}.")

        socketio.emit('mensagem', "Próxima mão em 5s...")
        for _ in range(10):
            if not jogo_rodando:
                break
            time.sleep(0.5)

    # Encerramento do loop: Devolve fichas restantes do humano ao bankroll
    if humano and humano.stack > 0:
        gerenciador_perfil.creditar_bankroll(humano.stack, "Você")
        socketio.emit('mensagem', f"Fichas na mesa (${humano.stack}) devolvidas ao seu Bankroll.")
        humano.stack = 0

    perfil_final = gerenciador_perfil.obter_perfil("Você")
    socketio.emit('perfil_atualizado', perfil_final)
    socketio.emit('sessao_encerrada', {'perfil': perfil_final})

@socketio.on('connect')
def handle_connect():
    emit('perfil_atualizado', gerenciador_perfil.obter_perfil("Você"))
    metricas = gravador.obter_metricas_jogador("Você")
    if metricas:
        emit('metricas_jogador', metricas)
    if jogo_rodando and mesa:
        emit('estado_mesa', empacotar_estado())

@socketio.on('obter_perfil')
def handle_obter_perfil():
    emit('perfil_atualizado', gerenciador_perfil.obter_perfil("Você"))

@socketio.on('recarregar_fichas')
def handle_recarregar_fichas(data=None):
    valor = data.get('valor', 10000) if data else 10000
    novo_perfil = gerenciador_perfil.recarregar_fichas(valor, "Você")
    emit('perfil_atualizado', novo_perfil)
    socketio.emit('mensagem', f"💵 Recarga de ${valor:,} creditada no seu Bankroll!")

@socketio.on('iniciar_cash_game')
def handle_iniciar_cash_game(data):
    global jogo_rodando, thread_jogo, config_sessao

    if jogo_rodando:
        emit('erro_entrada', {"mensagem": "Uma partida já está em andamento."})
        return

    data = data or {}
    sb = data.get('small_blind', 10)
    bb = data.get('big_blind', 20)
    buy_in = data.get('buy_in', 1000)

    # Valida e debita o buy-in do bankroll do jogador
    if not gerenciador_perfil.debitar_bankroll(buy_in, "Você"):
        emit('erro_entrada', {"mensagem": "Saldo insuficiente no Bankroll para este Buy-In!"})
        return

    config_sessao["small_blind"] = sb
    config_sessao["big_blind"] = bb
    config_sessao["buy_in"] = buy_in

    emit('perfil_atualizado', gerenciador_perfil.obter_perfil("Você"))
    emit('entrada_autorizada', {"small_blind": sb, "big_blind": bb, "buy_in": buy_in})

    jogo_rodando = True
    esperando_humano.clear()
    thread_jogo = Thread(target=loop_do_jogo)
    thread_jogo.start()
    socketio.emit('mensagem', f"Mesa iniciada! Blinds: ${sb}/${bb} • Buy-In: ${buy_in}")

@socketio.on('sair_da_mesa')
def handle_sair_da_mesa(data=None):
    global jogo_rodando, acao_humano, valor_humano

    data = data or {}
    forcar = data.get('forcar', False)

    # Verifica se o jogador humano está em uma mão ativa
    humano_na_mao = False
    if mesa and mesa.estado_atual != "SHOWDOWN":
        j_humano = next((j for j in mesa.jogadores if j.nome == "Você"), None)
        if j_humano and j_humano.ativo and not j_humano.is_all_in:
            humano_na_mao = True

    if humano_na_mao and not forcar:
        emit('confirmar_saida', {
            "mensagem": "Você está disputando a rodada atual! Se sair agora, você dará FOLD e perderá o valor apostado nesta mão. Deseja sair mesmo assim?"
        })
        return

    # Se estiver forçando a saída durante uma mão, folda o jogador
    if humano_na_mao and forcar:
        mesa.processar_acao("Você", "FOLD")
        acao_humano = "FOLD"
        valor_humano = 0
        esperando_humano.set()
        socketio.emit('mensagem', "Você desistiu da rodada para sair da mesa.")

    jogo_rodando = False
    esperando_humano.set() # Libera a trava caso a thread esteja bloqueada aguardando o humano

    # Imediatamente credita fichas restantes de volta ao Bankroll e encerra no front sem delay
    if humano and humano.stack > 0:
        gerenciador_perfil.creditar_bankroll(humano.stack, "Você")
        socketio.emit('mensagem', f"Fichas na mesa (${humano.stack}) devolvidas ao seu Bankroll.")
        humano.stack = 0

    perfil_final = gerenciador_perfil.obter_perfil("Você")
    socketio.emit('perfil_atualizado', perfil_final)
    socketio.emit('sessao_encerrada', {'perfil': perfil_final})
    socketio.emit('mensagem', "Sessão encerrada pelo jogador.")

@socketio.on('enviar_acao')
def handle_enviar_acao(data):
    global acao_humano, valor_humano
    if turno_atual != "Você":
        return
    acao_humano = data.get('acao')
    valor_humano = data.get('valor', 0)
    esperando_humano.set()

if __name__ == '__main__':
    print("Iniciando Servidor WebSocket de Poker na porta 5000...")
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
