import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any

class GerenciadorPerfil:
    """
    Gerenciador de Perfil e Bankroll do Jogador.
    Persiste dados do jogador (saldo total, mãos jogadas, vitórias e bônus)
    no banco relacional SQLite unificado (historico_partidas.db).
    """
    def __init__(self, db_path: str = "historico_partidas.db"):
        self.db_path = db_path
        self._inicializar_banco()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _inicializar_banco(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS perfil (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE DEFAULT 'Você',
                bankroll INTEGER DEFAULT 10000,
                maos_jogadas INTEGER DEFAULT 0,
                vitorias INTEGER DEFAULT 0,
                ultimo_resgate_bonus DATETIME,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Garante a existência do perfil padrão 'Você'
            cursor.execute("SELECT id FROM perfil WHERE nome = 'Você'")
            if cursor.fetchone() is None:
                cursor.execute("""
                INSERT INTO perfil (nome, bankroll, maos_jogadas, vitorias)
                VALUES ('Você', 10000, 0, 0)
                """)
            conn.commit()

    def obter_perfil(self, nome: str = "Você") -> Dict[str, Any]:
        """
        Retorna o dicionário com os dados do perfil do jogador.
        Cria o jogador com $10.000 de bankroll caso não exista.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, nome, bankroll, maos_jogadas, vitorias, ultimo_resgate_bonus, criado_em
            FROM perfil
            WHERE nome = ?
            """, (nome,))
            row = cursor.fetchone()

            if row is None:
                cursor.execute("""
                INSERT INTO perfil (nome, bankroll, maos_jogadas, vitorias)
                VALUES (?, 10000, 0, 0)
                """, (nome,))
                conn.commit()
                return self.obter_perfil(nome)

            return {
                "id": row[0],
                "nome": row[1],
                "bankroll": row[2],
                "maos_jogadas": row[3],
                "vitorias": row[4],
                "ultimo_resgate_bonus": row[5],
                "criado_em": row[6]
            }

    def debitar_bankroll(self, valor: int, nome: str = "Você") -> bool:
        """
        Debita um valor do bankroll (ex: para entrar em uma mesa ou buy-in).
        Retorna True se o débito foi bem-sucedido, ou False se o saldo for insuficiente.
        """
        if valor <= 0:
            return False

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT bankroll FROM perfil WHERE nome = ?", (nome,))
            row = cursor.fetchone()
            if not row or row[0] < valor:
                return False

            cursor.execute("""
            UPDATE perfil
            SET bankroll = bankroll - ?
            WHERE nome = ?
            """, (valor, nome))
            conn.commit()
            return True

    def creditar_bankroll(self, valor: int, nome: str = "Você") -> bool:
        """
        Credita um valor ao bankroll (ex: ao sair da mesa com as fichas restantes).
        """
        if valor < 0:
            return False

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE perfil
            SET bankroll = bankroll + ?
            WHERE nome = ?
            """, (valor, nome))
            conn.commit()
            return True

    def recarregar_fichas(self, valor: int = 10000, nome: str = "Você") -> Dict[str, Any]:
        """
        Adiciona fichas ao bankroll do jogador (recarga de testes / bônus).
        Atualiza o timestamp do último resgate.
        """
        if valor <= 0:
            return self.obter_perfil(nome)

        agora = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE perfil
            SET bankroll = bankroll + ?,
                ultimo_resgate_bonus = ?
            WHERE nome = ?
            """, (valor, agora, nome))
            conn.commit()

        return self.obter_perfil(nome)

    def registrar_mao_jogada(self, venceu: bool = False, nome: str = "Você") -> None:
        """
        Atualiza o contador de mãos disputadas e vitórias do jogador.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE perfil
            SET maos_jogadas = maos_jogadas + 1,
                vitorias = vitorias + ?
            WHERE nome = ?
            """, (1 if venceu else 0, nome))
            conn.commit()

