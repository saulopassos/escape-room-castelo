"""Servidor da gincana: placar por tema + proxy dos NPCs com IA.

Roda no "PC placar" da rede do laboratório:
    uvicorn app:app --host 0.0.0.0 --port 8000
"""

import os
import secrets
import time
import uuid

from dotenv import load_dotenv

load_dotenv()  # lê server/.env antes de qualquer configuração

from fastapi import Depends, FastAPI, Header, HTTPException  # noqa: E402
from fastapi.responses import HTMLResponse  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

import banco  # noqa: E402
import npc_ia  # noqa: E402

TEMAS = {
    "mecatronica": "Mecatrônica",
    "eletrotecnica": "Eletrotécnica",
    "seguranca": "Segurança do Trabalho",
    "quimica": "Química",
    "informatica": "Informática",
}
INTERVALO_QUIZ_SEGUNDOS = 5  # evita "chutar" todas as alternativas em sequência

app = FastAPI(title="Placar do Escape Room")
banco.inicializar()


def exigir_token(x_token_evento: str = Header(default="")) -> None:
    esperado = os.environ.get("TOKEN_EVENTO", "troque-este-token")
    if not secrets.compare_digest(x_token_evento, esperado):
        raise HTTPException(401, "token do evento inválido")


def partida_em_andamento(partida_id: str):
    partida = banco.buscar_partida(partida_id)
    if partida is None:
        raise HTTPException(404, "partida não encontrada")
    if partida["fim"] is not None:
        raise HTTPException(409, "partida já concluída")
    return partida


# ---------- Saúde ----------

@app.get("/saude")
def saude() -> dict:
    return {"status": "ok", "ia_configurada": npc_ia.ia_configurada()}


# ---------- Partidas e placar ----------

class NovaPartida(BaseModel):
    tema: str
    equipe: str = Field(min_length=1, max_length=40)
    turma: str = Field(min_length=1, max_length=20)
    jogadores: int = Field(ge=2, le=4)


@app.post("/api/partidas", dependencies=[Depends(exigir_token)])
def criar_partida(dados: NovaPartida) -> dict:
    if dados.tema not in TEMAS:
        raise HTTPException(422, f"tema inválido; use um destes: {', '.join(TEMAS)}")
    partida_id = uuid.uuid4().hex[:12]
    banco.criar_partida(partida_id, dados.tema, dados.equipe.strip(), dados.turma.strip(), dados.jogadores)
    banco.registrar_evento(partida_id, "partida_criada", dados.model_dump_json())
    return {"partida_id": partida_id}


@app.post("/api/partidas/{partida_id}/concluir", dependencies=[Depends(exigir_token)])
def concluir_partida(partida_id: str) -> dict:
    partida = banco.concluir_partida(partida_id)
    if partida is None:
        raise HTTPException(404, "partida não encontrada")
    banco.registrar_evento(partida_id, "partida_concluida", f"{partida['tempo']:.1f}s")
    return {"partida_id": partida_id, "tempo_segundos": round(partida["tempo"], 1)}


@app.get("/api/partidas", dependencies=[Depends(exigir_token)])
def listar_partidas() -> list[dict]:
    """Para o professor/gerentes conferirem todas as partidas, inclusive as em andamento."""
    return banco.listar_partidas()


@app.get("/api/placar")
def placar() -> dict:
    ranking = banco.ranking_por_tema()
    return {
        tema: {"nome": nome, "ranking": ranking.get(tema, [])}
        for tema, nome in TEMAS.items()
    }


@app.get("/placar", response_class=HTMLResponse)
def pagina_placar() -> str:
    return PAGINA_PLACAR


# ---------- NPCs com IA ----------

class FalaEquipe(BaseModel):
    partida_id: str
    mensagem: str = Field(min_length=1, max_length=500)


class RespostaQuiz(BaseModel):
    partida_id: str
    alternativa: int = Field(ge=0)


def carregar_npc_da_partida(npc_id: str, partida) -> npc_ia.FichaNPC:
    npc = npc_ia.carregar_npc(npc_id)
    if npc is None:
        raise HTTPException(404, "NPC não encontrado")
    if npc.tema != partida["tema"]:
        raise HTTPException(403, "este NPC não pertence ao tema da partida")
    return npc


def resposta_quiz(npc: npc_ia.FichaNPC, aviso: str) -> dict:
    return {
        "modo": "quiz",
        "aviso": aviso,
        "pergunta": npc.quiz.pergunta,
        "alternativas": npc.quiz.alternativas,
    }


@app.get("/api/npc/{npc_id}/abertura", dependencies=[Depends(exigir_token)])
def abertura_npc(npc_id: str, partida_id: str) -> dict:
    """Primeira fala do NPC (não usa IA)."""
    npc = carregar_npc_da_partida(npc_id, partida_em_andamento(partida_id))
    return {"nome": npc.nome, "fala": npc.abertura}


@app.post("/api/npc/{npc_id}/conversar", dependencies=[Depends(exigir_token)])
def conversar(npc_id: str, dados: FalaEquipe) -> dict:
    partida = partida_em_andamento(dados.partida_id)
    npc = carregar_npc_da_partida(npc_id, partida)

    if banco.liberacao_npc(dados.partida_id, npc_id):
        return {"modo": "ia", "fala": "Vocês já provaram o que sabem. Usem o código!",
                "aprovado": True, "codigo": npc.codigo}

    historico = banco.historico_npc(dados.partida_id, npc_id)
    if len(historico) // 2 >= npc.max_mensagens:
        banco.registrar_evento(dados.partida_id, "npc_limite", npc_id)
        return resposta_quiz(npc, "Limite de conversa atingido. Respondam a pergunta abaixo.")

    try:
        avaliacao = npc_ia.avaliar(npc, historico, dados.mensagem)
    except npc_ia.IAIndisponivel as erro:
        banco.registrar_evento(dados.partida_id, "ia_falhou", f"{npc_id}: {erro}")
        return resposta_quiz(npc, "O comunicador falhou! Respondam a pergunta abaixo.")

    banco.salvar_mensagens_npc(dados.partida_id, npc_id, dados.mensagem, avaliacao.fala)
    resposta = {"modo": "ia", "fala": avaliacao.fala, "aprovado": avaliacao.aprovado}
    if avaliacao.aprovado:
        banco.liberar_npc(dados.partida_id, npc_id, "ia", avaliacao.motivo)
        banco.registrar_evento(dados.partida_id, "npc_liberado", f"{npc_id} via ia: {avaliacao.motivo}")
        resposta["codigo"] = npc.codigo
    return resposta


@app.post("/api/npc/{npc_id}/quiz", dependencies=[Depends(exigir_token)])
def responder_quiz(npc_id: str, dados: RespostaQuiz) -> dict:
    partida = partida_em_andamento(dados.partida_id)
    npc = carregar_npc_da_partida(npc_id, partida)

    if banco.liberacao_npc(dados.partida_id, npc_id):
        return {"correta": True, "codigo": npc.codigo}

    tipo_evento = f"quiz_tentativa:{npc_id}"
    ultima = banco.ultimo_evento(dados.partida_id, tipo_evento)
    if ultima is not None and time.time() - ultima < INTERVALO_QUIZ_SEGUNDOS:
        raise HTTPException(429, f"aguardem {INTERVALO_QUIZ_SEGUNDOS} segundos entre tentativas")
    banco.registrar_evento(dados.partida_id, tipo_evento, str(dados.alternativa))

    if dados.alternativa != npc.quiz.correta:
        return {"correta": False}
    banco.liberar_npc(dados.partida_id, npc_id, "quiz", "quiz reserva")
    banco.registrar_evento(dados.partida_id, "npc_liberado", f"{npc_id} via quiz")
    return {"correta": True, "codigo": npc.codigo}


PAGINA_PLACAR = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Placar do Escape Room</title>
<style>
  body { font-family: system-ui, sans-serif; background: #10131a; color: #f1f3f5; margin: 24px; }
  h1 { text-align: center; margin: 0 0 24px; }
  .grade { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
  .tema { background: #1b2030; border-radius: 12px; padding: 16px; }
  .tema h2 { margin: 0 0 12px; font-size: 1.3rem; }
  table { width: 100%; border-collapse: collapse; }
  td { padding: 6px 4px; border-top: 1px solid #2c3347; }
  td.pos { width: 2em; color: #adb5bd; }
  td.tempo { text-align: right; font-variant-numeric: tabular-nums; font-weight: bold; }
  .vazio { color: #868e96; }
</style>
</head>
<body>
<h1>Placar do Escape Room</h1>
<div class="grade" id="grade"></div>
<script>
function formatar(segundos) {
  const m = Math.floor(segundos / 60), s = Math.floor(segundos % 60);
  return m + ":" + String(s).padStart(2, "0");
}
function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}
async function atualizar() {
  try {
    const dados = await (await fetch("/api/placar")).json();
    document.getElementById("grade").innerHTML = Object.values(dados).map(tema => {
      const linhas = tema.ranking.map((r, i) =>
        `<tr><td class="pos">${i + 1}º</td><td>${escapar(r.equipe)} <small>(${escapar(r.turma)})</small></td>` +
        `<td class="tempo">${formatar(r.tempo)}</td></tr>`).join("");
      return `<section class="tema"><h2>${tema.nome}</h2>` +
        (linhas ? `<table>${linhas}</table>` : `<p class="vazio">Nenhuma equipe concluiu ainda.</p>`) +
        `</section>`;
    }).join("");
  } catch (e) { /* servidor reiniciando: tenta de novo no próximo ciclo */ }
}
atualizar();
setInterval(atualizar, 5000);
</script>
</body>
</html>
"""
