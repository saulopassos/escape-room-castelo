# Decisões do projeto

Registro das decisões tomadas na entrevista de planejamento (15/10/2026).
Este documento **substitui** o plano original `Plano_Escape_Room_3D_Estufa_Aurora.docx`
nos pontos em que os dois divergem. Qualquer mudança aqui precisa ser aprovada pelo
professor em demo e registrada com data.

## O produto

| Tema | Decisão |
|---|---|
| Conceito | Portal com **5 escape rooms independentes**, um por curso técnico |
| Escolha | Ao entrar, a equipe escolhe o tema: Mecatrônica, Eletrotécnica, Segurança do Trabalho, Química ou Informática |
| Tamanho de cada tema | **3 ou mais salas encadeadas, ~40 min** de partida |
| Narrativa | **Universo comum** (mesmo cenário-mãe e identidade visual), mas **cada curso tem seu próprio caso** e final |
| Engine | **Godot 4.7.2 (stable, standard), 3D**, mesma versão em todos os PCs |
| Jogadores | **Multiplayer cooperativo, 2 a 4 jogadores** por partida |
| Rede | **LAN, um PC da equipe é o host** (sem servidor de jogo dedicado) |
| Cooperação | **Todos os enigmas são cooperativos**: informações divididas entre jogadores |
| Enigmas | Montados a partir de um **catálogo de peças prontas** feito pelos gerentes |
| Modelos 3D | **Gerados por IA** (texto/imagem → 3D), seguindo o padrão de escala e polígonos |
| Hardware | PCs **médios** (8–16 GB RAM, vídeo integrado recente ou placa básica) |

## Gincana

| Tema | Decisão |
|---|---|
| Uso final | **Gincana com ranking** entre equipes de outras turmas |
| Ranking | **Um ranking por tema** (Química compete com Química etc.) |
| Placar | **PC "placar" na rede** rodando um **mini-servidor Python** (FastAPI + SQLite), exibido num telão |
| Tempo oficial | Medido **pelo servidor** (início e fim registrados nele), nunca pelo relógio do jogo |

## IA dentro do jogo

| Tema | Decisão |
|---|---|
| NPC com IA | **Sim, inclusive na gincana** |
| Papel do NPC | **Faz parte do enigma**: guarda um código e só o libera se a equipe **provar conhecimento** |
| Avaliação | A IA avalia a explicação dos jogadores com uma **rubrica** escrita pelo autor e validada pela área |
| Segredo | O código **nunca** vai para o modelo; o servidor o entrega só quando a IA aprova |
| Chave da API | Fica **só no servidor Python** (proxy); o jogo nunca vê a chave |
| Modelo | `claude-haiku-5-5` |
| Se a IA falhar | O NPC vira um **quiz de múltipla escolha** fixo; a partida não trava |

## Pessoas e processo

| Papel | Quem | Responsabilidade |
|---|---|---|
| Professor | Você | **Supervisiona**: aprova etapas e features em **reunião/demo em aula** |
| Gerentes / orquestradores | **2 alunos de TI** | Constroem o **motor comum** (rede, lobby, avatar, interação, catálogo de peças, cronômetro, servidor Python), revisam PRs, registram as aprovações |
| Autores | **5 alunos de TI** | Um tema cada; constroem as salas com as peças do catálogo |
| Validação de conteúdo | **Professores + alunos das áreas** | Alunos do curso sugerem e testam; professor da área dá o aceite final |

| Tema | Decisão |
|---|---|
| Nível da turma | Lógica + Python básico; **nunca usaram engine nem Git** |
| IA dos alunos | **Claude Code (Haiku 5.5 via API)** ou Muse Spark |
| Repositório | **1 repositório**, uma pasta por tema (`game/rooms/<tema>/`); `game/core/` só para gerentes |
| Fluxo Git | **Branch + Pull Request**, revisado e mesclado por um gerente; `main` protegida |
| Entrega das salas | **Incremental**: sala 1 completa e aprovada → sala 2 → sala 3 |
| Avaliação (nota) | **Só o produto final** |

## Riscos assumidos conscientemente

Estes riscos foram aceitos nas decisões acima. Vale revisitá-los se algo travar.

1. **Iniciantes + Godot 3D + multiplayer.** É a combinação mais difícil. Mitigação: o
   multiplayer fica **inteiro no motor comum** (gerentes). Autores não escrevem código de rede.
2. **Tudo nas mãos de 2 gerentes.** Se o motor atrasar, os 5 autores param. Mitigação: a
   Etapa 1 (prova técnica) existe para descobrir isso cedo. Enquanto o motor não sai, os autores
   trabalham em roteiro, modelos 3D e greybox.
3. **3+ salas e 40 min por aluno iniciante.** Mitigação: entrega incremental, sempre com um jogo
   funcionando. Se faltar fôlego, o tema vai à gincana com as salas que estiverem aprovadas.
4. **IA ao vivo na competição.** Mitigação: rubrica objetiva, código fora do modelo, limite de
   mensagens por equipe e quiz reserva. Ensaiar com a internet real do laboratório.
5. **Todos os enigmas cooperativos com 2 a 4 jogadores.** Mitigação: o motor distribui
   **papéis** (A, B, C, D). Com menos de 4 jogadores, uma pessoa acumula papéis. Todo enigma
   precisa funcionar com 2 jogadores.
6. **Modelos 3D por IA.** Saem com escala, orientação e polígonos variados. Mitigação: padrão
   de importação em `docs/03_PADROES.md` e revisão pelo gerente antes do merge.
7. **Nota só pelo produto final.** O aluno pode entregar sem entender o código que a IA
   escreveu. Sugestão (opcional): na demo, pedir que o autor altere uma regra ao vivo.
