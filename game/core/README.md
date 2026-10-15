# core/ — motor comum (gerentes)

Só os gerentes alteram esta pasta. Ordem sugerida de construção (Etapas 1 e 3 do passo a passo):

## Já existe
- `autoload/game_config.gd`: temas, IP do placar, token do evento.
- `autoload/server_api.gd`: chamadas ao servidor Python (partida, conclusão, NPC, quiz).
- `menu/menu_principal.tscn`: menu provisório com escolha de tema e teste de conexão.

## A construir

### Gerente 1: rede, lobby e servidor
1. `autoload/rede.gd`: criar partida (host) com `ENetMultiplayerPeer.create_server(7777, 4)`
   e entrar (`create_client(ip, 7777)`). Sinais de jogador entrou/saiu.
2. `menu/lobby.tscn`: apelido, lista de jogadores, botão Iniciar (só host, 2–4 jogadores).
   Ao iniciar: `ServerAPI.criar_partida(...)` e guardar `GameConfig.partida_id` em todos.
3. `autoload/partida.gd`: estado compartilhado decidido pelo host: papéis A–D, peças
   resolvidas, inventário, sala atual. Clientes recebem uma "foto" do estado ao (re)entrar.
4. Troca de sala sem desconectar (`MultiplayerSpawner` para a sala atual).
5. Fim: a última porta chama `ServerAPI.concluir_partida()` e todos veem o tempo oficial.

### Gerente 2: avatar, interação, peças e interface
1. `jogador/jogador.tscn`: `CharacterBody3D` em 3ª pessoa, câmera, colisão, tecla `E`
   para interagir, posição replicada com `MultiplayerSynchronizer`.
2. `pecas/`: catálogo descrito em `docs/03_PADROES.md`. Cada peça:
   - tem propriedades `@export` para o autor configurar no Inspector;
   - envia a ação ao host por RPC; o host valida e replica o resultado;
   - emite o sinal `resolvida(id_peca)` que portas podem escutar.
3. `ui/`: HUD com papel do jogador, inventário da equipe, painel de pistas e
   janela de diálogo do NPC (com o modo quiz).
4. `../rooms/_modelo/`: sala de exemplo usando **todas** as peças.

## Teste de multiplayer no editor
*Debug → Customize Run Instances* → habilitar múltiplas instâncias → 2 a 4.
