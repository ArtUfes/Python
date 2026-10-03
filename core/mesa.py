from core.baralho import Baralho
from core.avaliador_de_maos import AvaliadorDeMaos
from core.avaliador_otimizado import AvaliadorDeMaosOtimizado
from core.jogador import Jogador
from core.carta import Carta
from core.pote import GerenciadorDePote

class Mesa:
    def __init__(self, small_blind=10, big_blind=20):
        self.baralho = Baralho()
        self.cartas_na_mesa = []
        self.jogadores = []
        
        # Atributos Financeiros
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.posicao_button = 0
        self.gerenciador_pote = GerenciadorDePote()
        
        # Controle de Estado
        self.estado_atual = "PRE_FLOP"
        self.maior_aposta_rodada = 0
        self.apostas_rodada = {}
        
    def adiciona_jogador(self, jogador):
        if len(self.jogadores) < 9:
            self.jogadores.append(jogador)
        else:
            print('A mesa já está cheia!')

    def iniciar_mao(self):
        self.baralho.reseta_baralho()
        self.cartas_na_mesa.clear()
        self.gerenciador_pote = GerenciadorDePote()
        self.estado_atual = "PRE_FLOP"
        self.maior_aposta_rodada = 0
        self.apostas_rodada = {}
        
        for j in self.jogadores:
            j.preparar_nova_mao()
            
        # Filtra apenas os que têm fichas e estão ativos
        ativos = [j for j in self.jogadores if j.ativo]
        
        for j in ativos:
            j.sorteia_cartas_jogador(self.baralho)
            self.apostas_rodada[j.nome] = 0
            
        if len(ativos) >= 2:
            sb_idx = (self.posicao_button + 1) % len(ativos)
            bb_idx = (self.posicao_button + 2) % len(ativos)
            
            sb_jogador = ativos[sb_idx]
            bb_jogador = ativos[bb_idx]
            
            valor_sb = sb_jogador.apostar(self.small_blind)
            valor_bb = bb_jogador.apostar(self.big_blind)
            
            self.apostas_rodada[sb_jogador.nome] += valor_sb
            self.apostas_rodada[bb_jogador.nome] += valor_bb
            
            self.maior_aposta_rodada = self.big_blind

    def processar_acao(self, nome_jogador, acao, valor=0):
        jogador = next((j for j in self.jogadores if j.nome == nome_jogador), None)
        if not jogador or not jogador.ativo:
            return False
            
        if acao == "FOLD":
            ativos_antes = [j for j in self.jogadores if j.ativo]
            if len(ativos_antes) <= 1:
                return False # O último jogador não pode dar fold
            jogador.foldar()
            
            # Se apos o fold so sobrou 1 jogador ativo, o jogo vai direto pro showdown (W.O.)
            ativos_agora = [j for j in self.jogadores if j.ativo]
            if len(ativos_agora) == 1:
                self.estado_atual = "SHOWDOWN"
            return True
            
        if acao == "CALL":
            falta_pagar = self.maior_aposta_rodada - self.apostas_rodada.get(jogador.nome, 0)
            valor_real = jogador.apostar(falta_pagar)
            self.apostas_rodada[jogador.nome] = self.apostas_rodada.get(jogador.nome, 0) + valor_real
            return True
            
        if acao == "RAISE":
            # Para ser um raise válido, o valor final deve ser maior que a aposta máxima atual
            if valor <= self.maior_aposta_rodada:
                return False
                
            # 'valor' é o total que a pessoa quer atingir (ex: raise TO 60)
            falta_pagar = valor - self.apostas_rodada.get(jogador.nome, 0)
            if falta_pagar > 0:
                valor_real = jogador.apostar(falta_pagar)
                nova_aposta_total = self.apostas_rodada.get(jogador.nome, 0) + valor_real
                self.apostas_rodada[jogador.nome] = nova_aposta_total
                
                if nova_aposta_total > self.maior_aposta_rodada:
                    self.maior_aposta_rodada = nova_aposta_total
                return True
        
        if acao == "CHECK":
            # Só pode dar check se a aposta atual dele for igual a maior aposta
            if self.apostas_rodada.get(jogador.nome, 0) == self.maior_aposta_rodada:
                return True
                
        return False

    def avancar_rodada(self):
        # Coleta as apostas para o Pote
        ativos = {j.nome for j in self.jogadores if j.ativo}
        self.gerenciador_pote.processar_rodada(self.apostas_rodada, ativos)
        
        # Reseta apostas para a próxima fase
        self.apostas_rodada = {j.nome: 0 for j in self.jogadores if j.ativo}
        self.maior_aposta_rodada = 0
        
        if self.estado_atual == "PRE_FLOP":
            self.estado_atual = "FLOP"
            for _ in range(3): self.cartas_na_mesa.append(self.baralho.sorteia_uma_carta())
        elif self.estado_atual == "FLOP":
            self.estado_atual = "TURN"
            self.cartas_na_mesa.append(self.baralho.sorteia_uma_carta())
        elif self.estado_atual == "TURN":
            self.estado_atual = "RIVER"
            self.cartas_na_mesa.append(self.baralho.sorteia_uma_carta())
        elif self.estado_atual == "RIVER":
            self.estado_atual = "SHOWDOWN"

    def executar_showdown(self):
        # Força o avanço da última rodada de apostas se ainda tiver apostas
        if sum(self.apostas_rodada.values()) > 0:
            ativos = {j.nome for j in self.jogadores if j.ativo}
            self.gerenciador_pote.processar_rodada(self.apostas_rodada, ativos)
            
        ativos_objs = [j for j in self.jogadores if j.ativo]
        
        # Avalia mãos
        for j in ativos_objs:
            # Completa cartas caso alguem tenha dado all-in no pre-flop e nao rolou as outras
            cartas_totais = self.cartas_na_mesa + j.cartas
            j.mao = sorted(cartas_totais, key=lambda x: x.valor, reverse=True)
            # Avaliador original exige 7 cartas (5 da mesa + 2 do jogador). 
            # Se for all-in antes do river, a mesa precisa estar completa para avaliar
            if len(self.cartas_na_mesa) == 5:
                j.classificacao_mao = AvaliadorDeMaosOtimizado.avalia_mao(j.mao)
            else:
                j.classificacao_mao = 0
        
        # O AvaliadorOtimizado gera uma tupla com a força absoluta da mão. Ex: (3, 11, 3, 14) -> Dois Pares
        # Python compara tuplas nativamente elemento por elemento! Basta ordenar a lista decrescente:
        ativos_objs.sort(key=lambda j: j.classificacao_mao, reverse=True)
        
        ranking = []
        if ativos_objs:
            grupo_atual = [ativos_objs[0].nome]
            valor_atual = ativos_objs[0].classificacao_mao
            
            for j in ativos_objs[1:]:
                if j.classificacao_mao == valor_atual:
                    grupo_atual.append(j.nome)
                else:
                    ranking.append(grupo_atual)
                    grupo_atual = [j.nome]
                    valor_atual = j.classificacao_mao
            ranking.append(grupo_atual)
            
        print("\n=== CLASSIFICAÇÃO DAS MÃOS ===")
        for pos, grupo in enumerate(ranking, 1):
            nomes = " e ".join(grupo)
            jogador_exemplo = next(j for j in ativos_objs if j.nome == grupo[0])
            nome_mao = AvaliadorDeMaosOtimizado.imprimir_mao(jogador_exemplo.classificacao_mao)
            print(f"{pos}º Lugar: {nomes} com {nome_mao}")
        print("==============================\n")
                
        # Distribui potes
        pagamentos = self.gerenciador_pote.distribuir(ranking)
        for nome, valor in pagamentos.items():
            jogador = next((j for j in self.jogadores if j.nome == nome), None)
            if jogador:
                jogador.receber_fichas(valor)
                
        # Gira o botão do Dealer
        self.posicao_button = (self.posicao_button + 1) % len(self.jogadores)
        
        return ranking, pagamentos
