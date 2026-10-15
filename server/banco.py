"""Banco SQLite do placar: partidas, conversas com NPCs, liberações e eventos de auditoria."""

import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS partidas (
    id          TEXT PRIMARY KEY,
    tema        TEXT NOT NULL,
    equipe      TEXT NOT NULL,
    turma       TEXT NOT NULL,
    jogadores   INTEGER NOT NULL,
    inicio      REAL NOT NULL,
    fim         REAL,
    tempo       REAL
);
CREATE TABLE IF NOT EXISTS npc_mensagens (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id  TEXT NOT NULL,
    npc_id      TEXT NOT NULL,
    papel       TEXT NOT NULL CHECK (papel IN ('user', 'assistant')),
    conteudo    TEXT NOT NULL,
    criado      REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS npc_liberacoes (
    partida_id  TEXT NOT NULL,
    npc_id      TEXT NOT NULL,
    via         TEXT NOT NULL,
    motivo      TEXT,
    criado      REAL NOT NULL,
    PRIMARY KEY (partida_id, npc_id)
);
CREATE TABLE IF NOT EXISTS eventos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id  TEXT,
    tipo        TEXT NOT NULL,
    detalhe     TEXT,
    criado      REAL NOT NULL
);
"""


def caminho_banco() -> Path:
    return Path(os.environ.get("DB_CAMINHO", Path(__file__).parent / "placar.db"))


@contextmanager
def conectar():
    con = sqlite3.connect(caminho_banco(), timeout=10)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def inicializar() -> None:
    with conectar() as con:
        con.executescript(ESQUEMA)


def registrar_evento(partida_id: str | None, tipo: str, detalhe: str = "") -> None:
    with conectar() as con:
        con.execute(
            "INSERT INTO eventos (partida_id, tipo, detalhe, criado) VALUES (?, ?, ?, ?)",
            (partida_id, tipo, detalhe, time.time()),
        )


def criar_partida(partida_id: str, tema: str, equipe: str, turma: str, jogadores: int) -> float:
    inicio = time.time()
    with conectar() as con:
        con.execute(
            "INSERT INTO partidas (id, tema, equipe, turma, jogadores, inicio) VALUES (?, ?, ?, ?, ?, ?)",
            (partida_id, tema, equipe, turma, jogadores, inicio),
        )
    return inicio


def buscar_partida(partida_id: str) -> sqlite3.Row | None:
    with conectar() as con:
        return con.execute("SELECT * FROM partidas WHERE id = ?", (partida_id,)).fetchone()


def concluir_partida(partida_id: str) -> sqlite3.Row | None:
    """Registra o fim uma única vez; chamadas repetidas devolvem o mesmo tempo."""
    agora = time.time()
    with conectar() as con:
        con.execute(
            "UPDATE partidas SET fim = ?, tempo = ? - inicio WHERE id = ? AND fim IS NULL",
            (agora, agora, partida_id),
        )
        return con.execute("SELECT * FROM partidas WHERE id = ?", (partida_id,)).fetchone()


def ranking_por_tema(limite: int = 20) -> dict[str, list[dict]]:
    with conectar() as con:
        linhas = con.execute(
            "SELECT tema, equipe, turma, jogadores, tempo FROM partidas "
            "WHERE tempo IS NOT NULL ORDER BY tema, tempo"
        ).fetchall()
    ranking: dict[str, list[dict]] = {}
    for linha in linhas:
        lista = ranking.setdefault(linha["tema"], [])
        if len(lista) < limite:
            lista.append(dict(linha))
    return ranking


def listar_partidas() -> list[dict]:
    with conectar() as con:
        linhas = con.execute("SELECT * FROM partidas ORDER BY inicio DESC").fetchall()
    return [dict(linha) for linha in linhas]


def historico_npc(partida_id: str, npc_id: str) -> list[dict]:
    with conectar() as con:
        linhas = con.execute(
            "SELECT papel, conteudo FROM npc_mensagens WHERE partida_id = ? AND npc_id = ? ORDER BY id",
            (partida_id, npc_id),
        ).fetchall()
    return [{"role": linha["papel"], "content": linha["conteudo"]} for linha in linhas]


def salvar_mensagens_npc(partida_id: str, npc_id: str, fala_equipe: str, fala_npc: str) -> None:
    agora = time.time()
    with conectar() as con:
        con.executemany(
            "INSERT INTO npc_mensagens (partida_id, npc_id, papel, conteudo, criado) VALUES (?, ?, ?, ?, ?)",
            [
                (partida_id, npc_id, "user", fala_equipe, agora),
                (partida_id, npc_id, "assistant", fala_npc, agora),
            ],
        )


def liberacao_npc(partida_id: str, npc_id: str) -> sqlite3.Row | None:
    with conectar() as con:
        return con.execute(
            "SELECT * FROM npc_liberacoes WHERE partida_id = ? AND npc_id = ?", (partida_id, npc_id)
        ).fetchone()


def liberar_npc(partida_id: str, npc_id: str, via: str, motivo: str) -> None:
    with conectar() as con:
        con.execute(
            "INSERT OR IGNORE INTO npc_liberacoes (partida_id, npc_id, via, motivo, criado) VALUES (?, ?, ?, ?, ?)",
            (partida_id, npc_id, via, motivo, time.time()),
        )


def ultimo_evento(partida_id: str, tipo: str) -> float | None:
    with conectar() as con:
        linha = con.execute(
            "SELECT MAX(criado) AS t FROM eventos WHERE partida_id = ? AND tipo = ?", (partida_id, tipo)
        ).fetchone()
    return linha["t"] if linha else None
