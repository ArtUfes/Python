import sys
import os
import json
import time
from threading import Thread, Event
from flask import Flask
from flask_socketio import SocketIO, emit

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.mesa import Mesa
from core.jogador import Jogador
from core.bot import Bot

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

mesa = None
humano = None
jogo_rodando = False
esperando_humano = Event()
acao_humano = None
valor_humano = 0

def empacotar_estado():
    if not mesa: return {}
    estado = {
        "estado_atual": mesa.estado_atual,
        "pote_total": sum(p.valor for p in mesa.gerenciador_pote.potes) + sum(mesa.apostas_rodada.values()),
        "maior_aposta": mesa.maior_aposta_rodada,
        "cartas_na_mesa": [f"{c.simbolo}{c.naipe}" for c in mesa.cartas_na_mesa],
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
    global mesa, jogo_rodando, acao_humano, valor_humano
    
    # Inicia a Mesa
    mesa = Mesa(small_blind=10, big_blind=20)
    humano = Jogador("Você", stack=1000)
    
    # Carregar o DNA supremo se existir, ou usar o padrão
    genes_supremos = None
    if os.path.exists("dna_supremo.json"):
        with open("dna_supremo.json", "r") as f:
            genes_supremos = json.load(f)
            
    b1 = Bot("ProBot_1", stack=1000, genes=genes_supremos)
    b2 = Bot("ProBot_2", stack=1000, genes=genes_supremos)
    b3 = Bot("ProBot_3", stack=1000, genes=genes_supremos)
    
    mesa.adiciona_jogador(humano)
    mesa.adiciona_jogador(b1)
    mesa.adiciona_jogador(b2)
    mesa.adiciona_jogador(b3)

    while jogo_rodando:
        mesa.iniciar_mao()
        emitir_estado()
        time.sleep(1.5) # Pausa dramática para o frontend animar as cartas
        
        while mesa.estado_atual != "SHOWDOWN":
            rodada_atual = mesa.estado_atual
            ativos_livres = [j for j in mesa.jogadores if j.ativo and not j.is_all_in]
            
            if len(ativos_livres) == 0:
                if mesa.estado_atual != "SHOWDOWN": mesa.avancar_rodada()
                continue
            elif len(ativos_livres) == 1:
                unico_livre = ativos_livres[0]
                falta = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(unico_livre.nome, 0)
                if falta == 0:
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

                emitir_estado()
                
                falta_pagar = mesa.maior_aposta_rodada - mesa.apostas_rodada.get(j.nome, 0)
                
                if j.nome == "Você":
                    socketio.emit('pedir_acao', {"falta_pagar": falta_pagar, "maior_aposta": mesa.maior_aposta_rodada})
                    esperando_humano.wait() # Pausa até o front mandar a ação via botão
                    acao, valor = acao_humano, valor_humano
                    esperando_humano.clear()
                else:
                    # Bot "pensa"
                    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
                    acao, valor = j.decidir_acao(mesa)
                    sys.stdout = sys.__stdout__
                    time.sleep(1) # Tempo pro frontend mostrar de quem é a vez
                    
                if acao == "CALL" and valor == 0: acao = "CHECK"
                
                sucesso = mesa.processar_acao(j.nome, acao, valor) if acao == "RAISE" else mesa.processar_acao(j.nome, acao)
                if not sucesso: mesa.processar_acao(j.nome, "FOLD")
                
                # Enviar notificação visual pro feed de chat do frontend
                msg_valor = f" ${valor}" if valor > 0 else ""
                socketio.emit('mensagem', f"{j.nome} deu {acao}{msg_valor}")
                
                jogadores_agiram[j.nome] = True
                if acao == "RAISE":
                    for outro in mesa.jogadores:
                        if outro.nome != j.nome: jogadores_agiram[outro.nome] = False
                
                idx_atual = (idx_atual + 1) % len(mesa.jogadores)
                
        ranking, pagamentos = mesa.executar_showdown()
        emitir_estado()
        
        from core.avaliador_otimizado import AvaliadorDeMaosOtimizado
        if ranking:
            vencedores = " e ".join(ranking[0])
            jogador_exemplo = next(j for j in mesa.jogadores if j.nome == ranking[0][0])
            cartas_str = " ".join([f"[{c.simbolo}{c.naipe}]" for c in jogador_exemplo.cartas])
            nome_mao = AvaliadorDeMaosOtimizado.imprimir_mao(jogador_exemplo.classificacao_mao)
            socketio.emit('mensagem', f"🏆 {vencedores} ganhou com {nome_mao}! (Mão: {cartas_str})")
            
        for nome, valor in pagamentos.items():
            if valor > 0:
                socketio.emit('mensagem', f"💰 {nome} recolheu ${valor}")
        
        socketio.emit('mensagem', "Próxima mão em 10s...")
        time.sleep(10)
        
        # Limpar jogadores falidos (Rebuy automático)
        for j in mesa.jogadores:
            if j.stack <= 0:
                j.stack = 1000
                socketio.emit('mensagem', f"{j.nome} fez Rebuy de $1000.")

@socketio.on('iniciar_jogo')
def handle_iniciar_jogo():
    global jogo_rodando, thread_jogo
    if not jogo_rodando:
        jogo_rodando = True
        thread_jogo = Thread(target=loop_do_jogo)
        thread_jogo.start()
        emit('mensagem', 'O Jogo começou! As cartas foram dadas.')

@socketio.on('enviar_acao')
def handle_enviar_acao(data):
    global acao_humano, valor_humano
    acao_humano = data.get('acao')
    valor_humano = data.get('valor', 0)
    esperando_humano.set() # Libera a trava do loop principal do jogo

if __name__ == '__main__':
    print("Iniciando Servidor WebSocket de Poker na porta 5000...")
    # allow_unsafe_werkzeug é seguro para testes locais e desenvolvimento
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
