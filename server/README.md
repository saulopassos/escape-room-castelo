# Servidor do placar + NPCs com IA

Roda **num único PC** da rede (o "PC placar"). Faz três coisas:

1. **Mede o tempo oficial** de cada partida (início e fim registrados aqui, não no jogo).
2. **Mostra o placar** por tema em `http://IP-DO-PLACAR:8000/placar` (abrir no telão).
3. **Conversa com os NPCs**: recebe a fala da equipe, pede ao Claude (`claude-haiku-5-5`) para
   avaliar com a rubrica e, se aprovado, devolve o código. A chave da API **só existe aqui**.

## Instalar e rodar (Windows)

```bat
cd server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
:: edite .env: ANTHROPIC_API_KEY e TOKEN_EVENTO
uvicorn app:app --host 0.0.0.0 --port 8000
```

- Liberar a porta **TCP 8000** no Firewall do Windows desse PC.
- Descobrir o IP com `ipconfig` e colocá-lo em `evento.cfg` nos PCs dos jogadores.
- Testes: `pytest` (a IA é simulada, não gasta créditos).

## Endpoints

| Método | Caminho | Quem usa | Token? |
|---|---|---|---|
| GET | `/saude` | botão "Testar conexão" | não |
| POST | `/api/partidas` | host, ao clicar Iniciar | sim |
| POST | `/api/partidas/{id}/concluir` | host, na última porta | sim |
| GET | `/api/partidas` | professor/gerentes (auditoria) | sim |
| GET | `/api/placar` e `/placar` | telão | não |
| GET | `/api/npc/{npc}/abertura?partida_id=` | primeira fala do NPC | sim |
| POST | `/api/npc/{npc}/conversar` | diálogo com o NPC | sim |
| POST | `/api/npc/{npc}/quiz` | quiz reserva | sim |

Documentação interativa: `http://localhost:8000/docs`.

## Como funciona o NPC

```
Jogo ──fala da equipe──▶ Servidor ──instruções + rubrica + histórico──▶ Claude
                                   ◀──{fala, aprovado, motivo}──────────
Jogo ◀──fala (+ código se aprovado)──
```

- O **código nunca é enviado ao modelo**. Mesmo que um jogador "convença" a IA a falar um
  código, ela não o conhece; só o servidor entrega, e apenas quando `aprovado = true`.
- A fala da equipe vai marcada como dado (`<fala_da_equipe>`), e as instruções mandam ignorar
  pedidos para mudar de papel.
- Se a IA falhar (sem chave, sem internet, erro, recusa) ou a equipe passar de `max_mensagens`,
  a resposta vem com `"modo": "quiz"` e o jogo mostra a pergunta de múltipla escolha.
- Quiz: no máximo uma tentativa a cada 5 segundos por NPC (evita chutar todas).
- Tudo fica registrado nas tabelas `npc_mensagens`, `npc_liberacoes` e `eventos` de `placar.db`
  (inclusive o `motivo` dado pela IA), para o professor auditar uma liberação contestada.

## Entrega dos NPCs (fora do repositório público)

O repositório principal é **público**, então o JSON dos NPCs (código secreto e rubrica) **nunca**
vai para ele: o git ignora `server/npcs/`. Os NPCs reais ficam num **segundo repositório,
privado**: `escape-room-castelo-npcs` (repositório privado é gratuito; só não tem proteção de
branch, o que aqui não faz falta).

```
escape-room-castelo       (público)  → jogo, servidor, docs, NPC fictício de exemplo
escape-room-castelo-npcs  (privado)  → mecatronica_sala1.json, quimica_sala1.json, ...
```

**Autor (criar e testar o NPC da sua sala):**

1. Clone o repositório privado **ao lado** do principal:
   `git clone https://github.com/saulopassos/escape-room-castelo-npcs`
2. Copie `server/npcs_exemplo/informatica_sala1.json` para o repositório privado com o nome
   `<tema>_sala<n>.json` (o nome do arquivo **é** o ID) e preencha a partir da
   [ficha do NPC](../docs/fichas/ficha_npc.md) aprovada.
3. Para testar no seu PC, no `server/.env` coloque `PASTA_NPCS=` com o caminho completo do clone
   privado, rode o servidor e converse com o NPC em `http://localhost:8000/docs`.
   (Alternativa rápida: copiar o JSON para `server/npcs/`, que o git ignora.)
4. Rode `pytest`: `test_todas_as_fichas_de_npc_sao_validas` confere o formato.
5. `git add`, `commit` e `push` **no repositório privado** (direto na `main` dele).

**Gerente / PC placar:** clonar o repositório privado no PC placar, apontar `PASTA_NPCS` no
`server/.env` para ele e dar `git pull` antes de cada ensaio e da gincana. O servidor lê o JSON a
cada mensagem, então não precisa reiniciar.

> Os autores conseguem ver as respostas uns dos outros no repositório privado. Tudo bem: autores
> não competem; na gincana atuam como suporte.

## Antes da gincana

- Fazer backup de `placar.db` (copiar o arquivo) antes e depois de cada rodada.
- Ensaiar com a internet real do laboratório e medir quanto tempo o NPC demora para responder.
