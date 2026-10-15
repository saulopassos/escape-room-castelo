# Padrões técnicos (o "contrato" entre motor e salas)

Se todos seguirem este documento, as salas dos 5 autores funcionam no mesmo jogo sem retrabalho.
Mudanças aqui só com aprovação em demo, e quem altera são os **gerentes**.

## Estrutura de pastas

```
game/
  project.godot
  core/                 ← SÓ gerentes alteram
    autoload/           ← GameConfig, ServerAPI (e futuramente Rede, Partida)
    menu/               ← menu principal, escolha de tema, lobby
    pecas/              ← catálogo de peças (cenas reutilizáveis)
    jogador/            ← avatar, câmera, interação
    ui/                 ← HUD, inventário, painel de pistas, diálogo do NPC
  rooms/
    _modelo/            ← sala de exemplo para copiar
    mecatronica/  eletrotecnica/  seguranca/  quimica/  informatica/
      sala1/
        sala1.tscn      ← cena principal da sala
        modelos/        ← .glb gerados por IA, já padronizados
        texturas/
        sala1.gd        ← (opcional) lógica local, sem rede
      sala2/ ...
      tema.tres         ← (futuro) metadados do tema: nome, cor, ordem das salas
  assets/shared/        ← modelos e sons comuns a todos (paredes, portas, fontes)
server/                 ← placar + proxy da IA (Python)
  npcs_exemplo/          ← NPC fictício (público)
  npcs/                  ← NPCs reais: IGNORADA pelo git (repo é público)
```

## Nomes

| O quê | Padrão | Exemplo |
|---|---|---|
| Pasta do tema | minúsculas, sem acento | `seguranca` |
| Branch | `<tema>/<assunto>` | `quimica/sala1-npc` |
| Nós na cena | `PascalCase` | `TecladoSenhaCofre` |
| Scripts e arquivos | `snake_case` | `sala1.gd`, `bancada_ph.glb` |
| ID de peça | `<TEMA>_S<n>_<NOME>` | `QUIM_S1_COFRE` |
| ID de NPC | `<tema>_sala<n>` | `quimica_sala1` (igual ao nome do JSON no servidor) |

Siglas de tema: `MECA`, `ELET`, `SEGT`, `QUIM`, `INFO`.

## Escala e desempenho

- **1 unidade do Godot = 1 metro.** Avatar com 1,75 m; porta com 2,1 m × 0,9 m.
- Cada sala: alvo de **até ~50 mil triângulos** no total e texturas de no máximo **1024 px**.
- Iluminação: no máximo 1 luz com sombra por sala; o resto sem sombra.
- Só a sala atual fica carregada; ao trocar de sala, a anterior é liberada.
- Meta: **30+ FPS** no PC mais fraco do laboratório.

## Modelos 3D gerados por IA

1. Gerar o modelo (texto ou imagem → 3D) e exportar em **GLB**.
2. Verificar a licença de uso da ferramenta (uso educacional/comercial) e anotar em
   `rooms/<tema>/CREDITOS.md`: ferramenta, prompt usado, data.
3. **Reduzir polígonos** se passar de ~5 mil triângulos por objeto (Blender → *Decimate*, ou a
   opção de "low poly" da própria ferramenta).
4. Ajustar **escala** (1 un = 1 m), **orientação** (frente para −Z) e **origem** (na base do objeto).
5. Salvar em `rooms/<tema>/salaN/modelos/`.
6. Colisão: usar formas simples (caixa/cápsula) adicionadas no Godot, nunca a malha inteira.

## Catálogo de peças

Construídas e mantidas pelos **gerentes** em `core/pecas/`. Toda peça já sincroniza o estado
entre os jogadores; o autor **só configura** pelo Inspector.

| Peça | O que faz | Configuração pelo autor |
|---|---|---|
| `PortaTrancada` | Abre quando uma condição é cumprida; pode levar à próxima sala | condição (ID de peça resolvida), próxima sala |
| `TecladoSenha` | Painel onde se digita um código | código correto, tamanho, ID |
| `ObjetoExaminavel` | Ao interagir, mostra texto/imagem | texto, imagem, **papéis que podem ver** |
| `ItemColetavel` | Vai para o inventário da equipe | nome, ícone, ID |
| `EncaixeDeItem` | Aceita um item do inventário | item esperado, ID |
| `SequenciaDeBotoes` | Botões/alavancas que precisam de uma ordem | ordem correta, ID |
| `BotaoSimultaneo` | Exige 2 jogadores pressionando ao mesmo tempo | janela de tempo, ID |
| `PainelDeInformacao` | Tela que mostra dados diferentes para cada papel | conteúdo por papel (A, B, C, D) |
| `SelecaoDeAlternativa` | Terminal de múltipla escolha | pergunta, alternativas, correta |
| `NPCComIA` | Personagem que conversa via servidor e libera um código | ID do NPC (= JSON no servidor) |

Peça nova = Issue "Nova peça" → aprovação na demo → gerentes constroem.

## Regra da cooperação (todos os enigmas)

- O motor distribui **papéis A, B, C, D** entre os jogadores presentes.
  - 4 jogadores: um papel cada.
  - 3 jogadores: um deles acumula 2 papéis.
  - 2 jogadores: cada um acumula 2 papéis.
- Cada enigma deve **dividir a informação entre pelo menos 2 papéis diferentes**
  (ex.: A vê o diagrama, B vê o painel de leituras) **ou** exigir 2 jogadores agindo juntos
  (`BotaoSimultaneo`).
- **Teste obrigatório:** todo enigma precisa ser resolvido com **exatamente 2 jogadores**.

## Quem decide o quê (rede)

- O **host** é a autoridade: é ele que confere respostas, abre portas e muda de sala.
- Clientes só enviam intenções ("apertei o botão X", "digitei 1234").
- O **tempo oficial** é do **servidor Python** (início e fim registrados lá).
- O **código do NPC** só existe no servidor Python e chega ao jogo quando a IA aprova.
