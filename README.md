# Escape Room dos Cursos Técnicos

Jogo 3D cooperativo (Godot 4, 2 a 4 jogadores em rede local) com **5 escape rooms**, uma por
curso técnico: Mecatrônica, Eletrotécnica, Segurança do Trabalho, Química e Informática.
Ao entrar, a equipe escolhe o tema e precisa escapar das salas no menor tempo. O ranking é
separado por tema.

## Comece por aqui

| Documento | Para quê |
|---|---|
| [docs/01_PASSO_A_PASSO.md](docs/01_PASSO_A_PASSO.md) | As etapas do projeto, do zero até a gincana |
| [docs/02_DECISOES.md](docs/02_DECISOES.md) | O que já foi decidido e por quê |
| [docs/03_PADROES.md](docs/03_PADROES.md) | Regras técnicas: pastas, nomes, escala, catálogo de peças |
| [docs/fichas/](docs/fichas/) | Fichas para professores das áreas e para os autores |
| [CLAUDE.md](CLAUDE.md) | Regras que a IA de programação deve seguir neste projeto |
| [server/README.md](server/README.md) | Como rodar o placar e o proxy da IA |

## Estrutura

```
game/     projeto Godot 4 (abra a pasta game/ no Godot)
server/   placar da gincana + proxy da IA dos NPCs (Python/FastAPI)
docs/     planejamento, padrões e fichas
```

## Equipe

| Papel | Nome | GitHub | Tema |
|---|---|---|---|
| Professor (supervisão) | | | |
| Gerente 1 (rede, lobby, servidor) | | | |
| Gerente 2 (avatar, interação, peças, UI) | | | |
| Autor | | | Mecatrônica |
| Autor | | | Eletrotécnica |
| Autor | | | Segurança do Trabalho |
| Autor | | | Química |
| Autor | | | Informática |

## Fluxo de trabalho

1. Crie uma branch: `git switch -c <tema>/<assunto>` (ex.: `quimica/sala1`).
2. Trabalhe **só na sua pasta** (`game/rooms/<tema>/` e `server/npcs/<tema>_*.json`).
3. `git add`, `git commit -m "..."`, `git push -u origin <branch>`.
4. Abra um Pull Request no GitHub e preencha o checklist.
5. Um gerente revisa e faz o merge. Features e etapas são aprovadas pelo professor em demo.
