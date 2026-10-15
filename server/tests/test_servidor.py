"""Testes do servidor. A IA é simulada: nenhum teste gasta créditos da API.

Rodar dentro de server/:  pytest
"""

import os
import sys
from pathlib import Path

import pytest

PASTA_SERVIDOR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PASTA_SERVIDOR))
TOKEN = {"X-Token-Evento": "token-de-teste"}


@pytest.fixture()
def cliente(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_CAMINHO", str(tmp_path / "teste.db"))
    monkeypatch.setenv("TOKEN_EVENTO", "token-de-teste")
    monkeypatch.setenv("PASTA_NPCS", str(PASTA_SERVIDOR / "npcs_exemplo"))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from fastapi.testclient import TestClient

    import app as modulo_app
    import banco

    banco.inicializar()
    return TestClient(modulo_app.app)


def criar_partida(cliente, tema="informatica") -> str:
    r = cliente.post("/api/partidas", headers=TOKEN,
                     json={"tema": tema, "equipe": "Azul", "turma": "2B", "jogadores": 3})
    assert r.status_code == 200, r.text
    return r.json()["partida_id"]


def test_token_obrigatorio(cliente):
    r = cliente.post("/api/partidas", json={"tema": "quimica", "equipe": "A", "turma": "1", "jogadores": 2})
    assert r.status_code == 401


def test_tema_e_jogadores_validados(cliente):
    r = cliente.post("/api/partidas", headers=TOKEN,
                     json={"tema": "culinaria", "equipe": "A", "turma": "1", "jogadores": 2})
    assert r.status_code == 422
    r = cliente.post("/api/partidas", headers=TOKEN,
                     json={"tema": "quimica", "equipe": "A", "turma": "1", "jogadores": 5})
    assert r.status_code == 422


def test_concluir_uma_vez_e_aparecer_no_placar(cliente):
    pid = criar_partida(cliente)
    t1 = cliente.post(f"/api/partidas/{pid}/concluir", headers=TOKEN).json()["tempo_segundos"]
    t2 = cliente.post(f"/api/partidas/{pid}/concluir", headers=TOKEN).json()["tempo_segundos"]
    assert t1 == t2  # concluir de novo não muda o tempo
    placar = cliente.get("/api/placar").json()
    assert placar["informatica"]["ranking"][0]["equipe"] == "Azul"
    assert placar["mecatronica"]["ranking"] == []


def test_sem_chave_npc_vira_quiz_sem_revelar_resposta(cliente):
    pid = criar_partida(cliente)
    r = cliente.post("/api/npc/informatica_sala1/conversar", headers=TOKEN,
                     json={"partida_id": pid, "mensagem": "É ácida"}).json()
    assert r["modo"] == "quiz"
    assert "correta" not in r and "codigo" not in r


def test_quiz_libera_codigo_e_limita_chutes(cliente):
    pid = criar_partida(cliente)
    errada = cliente.post("/api/npc/informatica_sala1/quiz", headers=TOKEN,
                          json={"partida_id": pid, "alternativa": 0})
    assert errada.json() == {"correta": False}
    chute_rapido = cliente.post("/api/npc/informatica_sala1/quiz", headers=TOKEN,
                                json={"partida_id": pid, "alternativa": 1})
    assert chute_rapido.status_code == 429


def test_quiz_correto(cliente):
    pid = criar_partida(cliente)
    r = cliente.post("/api/npc/informatica_sala1/quiz", headers=TOKEN,
                     json={"partida_id": pid, "alternativa": 1}).json()
    assert r == {"correta": True, "codigo": "0000"}


def test_npc_de_outro_tema_bloqueado(cliente):
    pid = criar_partida(cliente, tema="mecatronica")
    r = cliente.post("/api/npc/informatica_sala1/conversar", headers=TOKEN,
                     json={"partida_id": pid, "mensagem": "oi"})
    assert r.status_code == 403


def test_id_de_npc_malicioso(cliente):
    pid = criar_partida(cliente)
    r = cliente.post("/api/npc/..%2F.env/conversar", headers=TOKEN,
                     json={"partida_id": pid, "mensagem": "oi"})
    assert r.status_code == 404


def test_ia_aprova_entrega_codigo_e_guarda_historico(cliente, monkeypatch):
    import npc_ia

    chamadas = []

    def avaliar_falso(npc, historico, mensagem):
        chamadas.append(list(historico))
        aprovado = "neutro" in mensagem
        return npc_ia.AvaliacaoNPC(fala="Hum...", aprovado=aprovado, motivo="teste")

    monkeypatch.setattr(npc_ia, "avaliar", avaliar_falso)
    pid = criar_partida(cliente)

    r1 = cliente.post("/api/npc/informatica_sala1/conversar", headers=TOKEN,
                      json={"partida_id": pid, "mensagem": "É ácida"}).json()
    assert r1 == {"modo": "ia", "fala": "Hum...", "aprovado": False}

    r2 = cliente.post("/api/npc/informatica_sala1/conversar", headers=TOKEN,
                      json={"partida_id": pid, "mensagem": "abaixo de 7 é ácido, 7 é neutro"}).json()
    assert r2["aprovado"] is True and r2["codigo"] == "0000"
    assert len(chamadas[1]) == 2  # a segunda chamada recebeu a primeira troca de mensagens


def test_partida_concluida_nao_conversa(cliente):
    pid = criar_partida(cliente)
    cliente.post(f"/api/partidas/{pid}/concluir", headers=TOKEN)
    r = cliente.post("/api/npc/informatica_sala1/conversar", headers=TOKEN,
                     json={"partida_id": pid, "mensagem": "oi"})
    assert r.status_code == 409


def test_instrucoes_nunca_contem_o_codigo(monkeypatch):
    import npc_ia

    monkeypatch.setenv("PASTA_NPCS", str(PASTA_SERVIDOR / "npcs_exemplo"))
    npc = npc_ia.carregar_npc("informatica_sala1")
    assert npc.codigo not in npc_ia.montar_instrucoes(npc)


@pytest.mark.parametrize("pasta", ["npcs_exemplo", "npcs"])
def test_todas_as_fichas_de_npc_sao_validas(pasta, monkeypatch):
    """Valida o exemplo e também as fichas reais que estiverem no PC (server/npcs/)."""
    import npc_ia

    monkeypatch.setenv("PASTA_NPCS", str(PASTA_SERVIDOR / pasta))
    for arquivo in (PASTA_SERVIDOR / pasta).glob("*.json"):
        npc = npc_ia.carregar_npc(arquivo.stem)
        assert npc is not None, f"{arquivo.name}: nome inválido (use <tema>_sala<n>.json)"
        assert npc.id == arquivo.stem
        assert 0 <= npc.quiz.correta < len(npc.quiz.alternativas)
