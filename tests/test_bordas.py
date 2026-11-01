import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.jogador import Jogador
from core.pote import GerenciadorDePote
from core.mesa import Mesa

class TestCasosDeBorda(unittest.TestCase):

    # --- BORDAS FASE 1: JOGADOR ---
    def test_jogador_aposta_negativa_ou_zero(self):
        j = Jogador("Trapaceiro", stack=100)
        # Tenta apostar valor negativo para ver se o stack aumenta (bug de criar dinheiro infinito)
        valor_apostado = j.apostar(-50)
        self.assertEqual(valor_apostado, 0)
        self.assertEqual(j.stack, 100) # Stack nao deve mudar

        # Tenta apostar 0
        valor_apostado2 = j.apostar(0)
        self.assertEqual(valor_apostado2, 0)
        self.assertEqual(j.stack, 100)

    # --- BORDAS FASE 2: POTE ---
    def test_pote_fichas_impares_multiplos_vencedores(self):
        # O pote tem 10 fichas e há 3 vencedores.
        # Eles empataram, entao cada um deveria ganhar 3, e sobra 1 ficha.
        # A ficha impar deve ir para o primeiro cara (A).
        gerenciador = GerenciadorDePote()
        
        # Forçamos o estado do pote para focar no teste matematico do distribuir()
        gerenciador.potes[0].valor = 10
        gerenciador.potes[0].jogadores_elegiveis = {"A", "B", "C"}
        
        # Simula que os tres jogadores tiverem exatamenta a mesma mao e empataram (ranking index 0)
        ranking = [["A", "B", "C"]]
        pagamentos = gerenciador.distribuir(ranking)
        
        # 10 / 3 = 3 pra cada, sobra 1. A sobra vai pro primeiro da lista ("A").
        self.assertEqual(pagamentos.get("A"), 4)
        self.assertEqual(pagamentos.get("B"), 3)
        self.assertEqual(pagamentos.get("C"), 3)

    # --- BORDAS FASE 3: MESA ---
    def test_mesa_raise_invalido(self):
        mesa = Mesa(small_blind=10, big_blind=20)
        mesa.adiciona_jogador(Jogador("A", stack=1000))
        mesa.adiciona_jogador(Jogador("B", stack=1000))
        mesa.iniciar_mao()
        
        # Aposta maior atual é 20 (do Big Blind)
        # O jogador "A" (Small Blind) tenta dar RAISE para 15 (menor que a aposta maxima atual)
        resultado = mesa.processar_acao("A", "RAISE", 15)
        
        # O motor deve rejeitar e retornar False
        self.assertFalse(resultado)
        
    def test_mesa_check_invalido(self):
        mesa = Mesa(small_blind=10, big_blind=20)
        mesa.adiciona_jogador(Jogador("A", stack=1000))
        mesa.adiciona_jogador(Jogador("B", stack=1000))
        mesa.iniciar_mao()
        
        nome_sb = "A" if mesa.apostas_rodada["A"] == 10 else "B"
        nome_bb = "B" if nome_sb == "A" else "A"
        
        # O jogador que pagou 10 (SB) não pode dar CHECK porque a maior aposta é 20
        resultado = mesa.processar_acao(nome_sb, "CHECK")
        self.assertFalse(resultado)
        
        # Ele da CALL
        mesa.processar_acao(nome_sb, "CALL")
        
        # Agora as apostas estão iguais. O BB pode dar CHECK.
        resultado_bb = mesa.processar_acao(nome_bb, "CHECK")
        self.assertTrue(resultado_bb)

    # --- BORDAS FASE 4: MODO ESPECTADOR & LEVANTAR / SENTAR ---
    def test_jogador_espectador_nao_entra_na_mao(self):
        """
        Mesmo que o jogador possua fichas, se estiver com espectador=True,
        ele NUNCA deve ser marcado como ativo ao iniciar a mão.
        """
        j = Jogador("Você", stack=5000)
        j.espectador = True
        j.preparar_nova_mao()
        self.assertFalse(j.ativo)
        self.assertEqual(len(j.cartas), 0)

        # Ao desativar o modo espectador, ele volta a ser ativo
        j.espectador = False
        j.preparar_nova_mao()
        self.assertTrue(j.ativo)

    def test_levantar_mid_hand_folda_e_preserva_conservacao(self):
        """
        Quando o jogador levanta no meio da rodada:
        Ele deve foldar a aposta já feita, e apenas o stack restante é devolvido.
        O pote continua elegível para os bots restantes.
        """
        import tempfile
        from core.perfil import GerenciadorPerfil
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        try:
            gerenciador = GerenciadorPerfil(db_path=temp_db.name)
            gerenciador.definir_bankroll(100000, "Você")

            mesa = Mesa(small_blind=10, big_blind=20)
            humano = Jogador("Você", stack=1000) # Buy-in de 1000
            gerenciador.debitar_bankroll(1000, "Você") # Bankroll: 99.000
            
            bot1 = Jogador("Bot1", stack=1000)
            mesa.adiciona_jogador(humano)
            mesa.adiciona_jogador(bot1)
            mesa.iniciar_mao()

            # Humano aposta mais 50 fichas (stack vai pra 940 ou 950 dependendo do blind)
            stack_antes_levantar = humano.stack
            aposta_humano = mesa.apostas_rodada[humano.nome]
            self.assertEqual(stack_antes_levantar + aposta_humano, 1000)

            # Humano decide levantar com confirmação (forcar=True): dá fold
            mesa.processar_acao("Você", "FOLD")
            self.assertFalse(humano.ativo)

            # Devolve stack restante ao bankroll
            gerenciador.creditar_bankroll(humano.stack, "Você")
            humano.stack = 0
            humano.espectador = True

            # Invariante econômico: Bankroll final + fichas presas no pote da mesa == 100.000 original
            saldo_final = gerenciador.obter_perfil("Você")["bankroll"]
            self.assertEqual(saldo_final + aposta_humano, 100000)
        finally:
            if os.path.exists(temp_db.name):
                try: os.remove(temp_db.name)
                except PermissionError: pass

    def test_sentar_limites_invalidos_buyin(self):
        """
        Garante que valores abaixo do mínimo (10 BBs) ou acima do máximo (1000 BBs)
        são devidamente rejeitados pelo servidor.
        """
        import servidor
        client = servidor.socketio.test_client(servidor.app)
        servidor.humano = Jogador("Você", stack=0)
        servidor.humano.espectador = True
        servidor.mesa = Mesa(small_blind=10, big_blind=20) # Min: 200, Max: 20.000
        servidor.gerenciador_perfil.definir_bankroll(100000, "Você")

        # Tentativa com 100 (abaixo de 200)
        client.emit('sentar_na_mesa', {'valor': 100})
        recebidos = client.get_received()
        nomes_eventos = [e['name'] for e in recebidos]
        self.assertIn('erro_sentar', nomes_eventos)
        self.assertTrue(servidor.humano.espectador)

        # Tentativa com 50.000 (acima de 20.000)
        client.emit('sentar_na_mesa', {'valor': 50000})
        recebidos2 = client.get_received()
        nomes_eventos2 = [e['name'] for e in recebidos2]
        self.assertIn('erro_sentar', nomes_eventos2)
        self.assertTrue(servidor.humano.espectador)

        # Tentativa válida com 1000 (50 BBs)
        client.emit('sentar_na_mesa', {'valor': 1000})
        self.assertEqual(servidor.humano.stack, 1000)
        self.assertFalse(servidor.humano.espectador)

        client.disconnect()

    def test_debito_saldo_exato_limite(self):
        """
        Testa débito exatamente no limite do saldo (deve zerar o bankroll perfeitamente, sem erro).
        """
        import tempfile
        from core.perfil import GerenciadorPerfil
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        try:
            g = GerenciadorPerfil(db_path=temp_db.name)
            g.definir_bankroll(5000, "Você")
            
            # Debita exatamente 5000
            self.assertTrue(g.debitar_bankroll(5000, "Você"))
            self.assertEqual(g.obter_perfil("Você")["bankroll"], 0)

            # Tenta debitar 1 ficha quando saldo é 0
            self.assertFalse(g.debitar_bankroll(1, "Você"))
            self.assertEqual(g.obter_perfil("Você")["bankroll"], 0)
        finally:
            if os.path.exists(temp_db.name):
                try: os.remove(temp_db.name)
                except PermissionError: pass

if __name__ == '__main__':
    unittest.main()
