# Instruções para a IA de programação

Projeto escolar: escape room 3D cooperativo em **Godot 4 (GDScript)** com servidor
**Python (FastAPI)**. Os alunos são **iniciantes** (lógica + Python básico). Leia
`docs/03_PADROES.md` antes de qualquer alteração.

## Quem é quem

- **Autores** (5 alunos): cada um é dono de um tema e só altera:
  - `game/rooms/<seu-tema>/`
  - o JSON do próprio NPC (`<seu-tema>_sala<n>.json`), que fica **fora** deste repositório
- **Gerentes** (2 alunos): donos de `game/core/`, `game/assets/shared/`, `server/` e `docs/`.
- Pergunte ao usuário qual é o papel e o tema dele se não estiver claro.

## Regras obrigatórias

1. **Não altere arquivos fora da área do usuário.** Se a tarefa exigir mudar `core/` e o
   usuário for autor, pare e explique que ele deve abrir uma Issue "Nova peça" para os gerentes.
2. **Autores não escrevem código de rede** (RPC, `MultiplayerSynchronizer`, `multiplayer.*`).
   Salas usam as peças de `game/core/pecas/`, configuradas pelo Inspector ou por propriedades
   `@export`.
3. **Todo enigma é cooperativo** e precisa funcionar com exatamente 2 jogadores
   (ver "Regra da cooperação" em `docs/03_PADROES.md`).
4. **Nunca** coloque chave de API, senha ou o `codigo` dos NPCs dentro de `game/`.
   **Este repositório é público.** Nunca crie nem commite arquivos em `server/npcs/` (o git ignora
   essa pasta): os NPCs reais ficam no repositório privado de NPCs. O modelo fictício é
   `server/npcs_exemplo/informatica_sala1.json`.
5. Siga a escala (1 unidade = 1 metro) e os nomes do padrão (`QUIM_S1_COFRE` etc.).
6. GDScript com tipos estáticos (`var x: int = 0`, `func f(a: String) -> void`) e comentários
   em português.
7. Não adicione plugins, addons ou dependências sem aprovação dos gerentes.
8. Mudanças pequenas e explicadas. Depois de gerar código, **explique o que cada parte faz** em
   linguagem simples: o aluno precisa entender para apresentar na demo.

## Comandos úteis

- Servidor: `cd server && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && uvicorn app:app --host 0.0.0.0 --port 8000`
- Testes do servidor: `cd server && pytest`
- Testar multiplayer no editor Godot: *Debug → Customize Run Instances* → 2 instâncias.

## Antes do Pull Request

Revise o diff do usuário contra estas regras e o checklist em
`.github/pull_request_template.md`. Aponte qualquer arquivo alterado fora da área dele.
