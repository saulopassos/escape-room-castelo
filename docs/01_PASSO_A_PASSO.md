# Passo a passo de implementação

Guia em etapas, **sem cronograma**. Cada etapa termina numa **demo em aula** onde o professor
aprova (ou devolve) a entrega. Uma etapa só começa quando a anterior for aprovada, exceto onde
está indicado que dá para trabalhar em paralelo.

Decisões que embasam este guia: [02_DECISOES.md](02_DECISOES.md).
Padrões técnicos (nomes, escala, peças): [03_PADROES.md](03_PADROES.md).

```
Etapa 0  Preparação ............ professor + gerentes
Etapa 1  Prova técnica ......... gerentes            ┐
Etapa 2  Roteiro da sala 1 ..... autores + áreas     ┘ em paralelo
Etapa 3  Motor comum v1 ........ gerentes            ┐
         Aprender Godot + arte . autores             ┘ em paralelo
Etapa 4  Sala 1 jogável ........ autores (gerentes revisam)
Etapa 5  Validação da área ..... áreas
Etapa 6  Salas 2, 3, ... ....... repete 2 → 4 → 5 para cada sala
Etapa 7  Ensaio geral .......... todos + turmas convidadas
Etapa 8  Gincana ............... todos
```

---

## Etapa 0: Preparação

**Quem:** professor e os 2 gerentes.

1. **Escolher os 2 gerentes.** Critérios sugeridos: quem tem mais facilidade com lógica e
   organização. Um gerente cuida de **rede, lobby e servidor Python**; o outro cuida de
   **avatar, interação, interface e catálogo de peças**.
2. **Distribuir os 5 temas** entre os autores (de preferência, por afinidade com a área).
3. **GitHub:**
   - Criar uma *Organization* gratuita (ex.: `escape-room-castelo`) e o repositório **privado**
     a partir desta pasta.
   - Convidar os 7 alunos e o professor.
   - Proteger a `main`: *Settings → Branches → Add rule* → exigir Pull Request com 1 aprovação.
   - Preencher `.github/CODEOWNERS` com os usuários reais.
4. **Instalar nos PCs do laboratório** (pedir ao suporte se precisar de administrador):
   - **Godot 4.7.2 stable** (versão "standard", não a .NET). É só descompactar, sem instalador
     (ex.: `C:\Godot_v4.7.2\`). Todos usam exatamente essa versão.
   - **Git** e **Python 3.11+**.
   - **VS Code** (opcional, para Python e Markdown).
   - **Claude Code** (ou Muse Spark), configurado com a chave/conta que o professor fornecer.
5. **Chave da API para o NPC:** o professor cria a chave e a coloca **apenas** no PC placar
   (arquivo `server/.env`). Nunca no repositório, nunca nos PCs dos jogadores.
6. **Aula de Git (1 encontro):** clone, branch, commit, push, Pull Request, resolver um
   conflito simples. Cada aluno abre um PR adicionando o próprio nome ao `README.md`.

✅ **Demo de aprovação:** os 7 alunos têm um PR mesclado na `main`, e Godot abre o projeto
`game/` em todos os PCs.

---

## Etapa 1: Prova técnica (o "pior risco primeiro")

**Quem:** gerentes. **Objetivo:** provar, antes de qualquer sala bonita, que o multiplayer,
o placar e a IA funcionam **na rede real do laboratório**.

1. **Dois PCs, uma sala cinza:** o PC A clica "Criar partida", o PC B digita o IP de A e entra.
   Os dois veem o avatar (uma cápsula) um do outro se movendo.
   Usar `ENetMultiplayerPeer` + `MultiplayerSpawner` + `MultiplayerSynchronizer` do Godot 4.
2. **Ação compartilhada:** o jogador B aperta um botão e **a porta abre para os dois**.
   A abertura é decidida **pelo host** e replicada.
3. **Servidor Python:** subir o `server/` no PC placar (ver `server/README.md`). Do Godot,
   criar uma partida, concluí-la e vê-la aparecer em `http://IP-DO-PLACAR:8000/placar`.
4. **NPC:** do Godot, mandar uma mensagem para o NPC de exemplo e mostrar a resposta na tela.
   Desligar a internet e confirmar que o **quiz reserva** aparece.
5. **Medir:** anotar FPS na sala cinza no PC mais fraco e se o firewall do Windows bloqueou
   alguma porta (jogo: UDP, ex. 7777; placar: TCP 8000).

✅ **Demo de aprovação:** os 4 itens acima ao vivo, em PCs diferentes do laboratório.
❌ Se falhar: **não avançar**. Resolver rede/firewall com o suporte antes de qualquer outra coisa.

---

## Etapa 2: Roteiro da sala 1 (em paralelo com a Etapa 1)

**Quem:** cada autor, com o professor e alunos da área do seu tema.

1. **Universo comum:** a turma inteira define, numa aula, o cenário-mãe (ex.: um campus
   técnico fictício), a identidade visual e o tom. Cada tema terá **seu próprio caso**.
   Registrar em `docs/universo.md`.
2. **Ficha da área** ([fichas/ficha_area.md](fichas/ficha_area.md)): o professor da área
   escolhe os conceitos, os valores corretos e o que **não** pode aparecer (segurança).
3. **Roteiro da sala** ([fichas/ficha_roteiro_sala.md](fichas/ficha_roteiro_sala.md)): o autor
   transforma o conteúdo em enigmas **cooperativos** usando só peças do catálogo
   ([03_PADROES.md](03_PADROES.md#catálogo-de-peças)).
4. **Ficha do NPC** ([fichas/ficha_npc.md](fichas/ficha_npc.md)): persona, desafio, rubrica,
   código secreto e quiz reserva.
5. **Teste em papel:** outra dupla joga o roteiro em papel, **sem o autor explicar nada**.
   Toda informação necessária precisa estar "na sala".

✅ **Demo de aprovação:** cada autor apresenta o roteiro da sala 1 e o resultado do teste em
papel. O professor da área já assinou a ficha.

---

## Etapa 3: Motor comum v1 + preparação dos autores (em paralelo)

### Gerentes: motor comum

Tudo em `game/core/`. Lista completa das peças em [03_PADROES.md](03_PADROES.md).

1. **Menu principal:** escolher tema → criar partida (host) ou entrar (IP).
2. **Lobby:** apelido, lista de jogadores, botão "Iniciar" (só o host, com 2 a 4 jogadores).
   Ao iniciar: chama `POST /api/partidas` no placar, e o **servidor** começa a contar o tempo.
3. **Papéis:** o motor sorteia os papéis A–D entre os jogadores presentes (com 2 jogadores,
   cada um fica com 2 papéis). As peças usam o papel para decidir quem vê qual informação.
4. **Avatar em 3ª pessoa** + câmera + colisão + tecla de interação (`E`).
5. **Catálogo de peças v1** (cada peça é uma cena `.tscn` configurável pelo Inspector).
6. **Inventário compartilhado** da equipe e painel de pistas.
7. **Troca de sala:** a porta final de uma sala carrega a próxima (sem desconectar ninguém).
8. **Fim da partida:** a última porta chama `POST /api/partidas/{id}/concluir` e mostra o tempo
   oficial devolvido pelo servidor.
9. **`rooms/_modelo/`:** uma sala de exemplo completa, usando todas as peças, que os autores
   vão **copiar**.

✅ **Demo de aprovação:** 2 a 4 PCs jogam a sala modelo do início ao fim, incluindo o NPC, e o
tempo aparece no placar.

### Autores: enquanto o motor não fica pronto

1. Fazer o tutorial oficial do Godot *"Your first 3D game"* (documentação do Godot).
2. **Gerar os modelos 3D** da sala 1 com IA, seguindo o padrão de importação
   ([03_PADROES.md](03_PADROES.md#modelos-3d-gerados-por-ia)).
3. Montar o **greybox** da sala 1 (paredes, mesas, posições) com caixas simples.

---

## Etapa 4: Sala 1 jogável

**Quem:** cada autor, na pasta `game/rooms/<tema>/`.

1. Criar a branch `<tema>/sala1` (ex.: `quimica/sala1`).
2. Copiar `rooms/_modelo/` para `rooms/<tema>/sala1/` e trocar cenário, textos e configuração
   das peças pelo roteiro aprovado.
3. Criar o NPC `<tema>_sala1.json` a partir da ficha e enviá-lo ao **repositório privado de
   NPCs** (nunca ao repositório público). Ver "Entrega dos NPCs" em `server/README.md`.
4. **Testar sozinho com 2 janelas** do Godot (*Debug → Customize Run Instances → 2*).
5. Abrir o **Pull Request** com o checklist do template preenchido.
6. **Revisão cruzada:** outro autor joga a sala com um colega **sem saber a resposta**.
   O autor só observa e anota onde travaram.
7. Gerente revisa: só mexeu na própria pasta? Usou peças do catálogo? Roda no PC mais fraco?
   → merge.

**Pediu uma peça nova?** (ex.: "preciso de um enigma de arrastar fios"). Abrir uma *Issue* com o
template "Nova peça". Os gerentes avaliam, o professor aprova na demo, e os **gerentes** constroem
a peça no `core/` para todos usarem. Autor não cria peça própria com código de rede.

✅ **Demo de aprovação:** a sala 1 de cada tema é jogada por uma dupla de fora, do início ao fim.

---

## Etapa 5: Validação da área

1. Alunos do curso correspondente jogam a sala 1 e apontam termos, valores ou situações
   incorretas.
2. O professor da área joga (ou assiste) e **assina** a ficha da área ("versão jogável aprovada").
3. Correções viram Issues para o autor.

✅ **Aprovação:** ficha assinada pelo professor da área.

---

## Etapa 6: Salas 2, 3, ...

Repetir **Etapa 2 → Etapa 4 → Etapa 5** para cada nova sala, uma por vez. Regra de ouro:
**a `main` sempre tem um jogo que funciona**. Uma sala só entra quando está completa e aprovada.

Os gerentes, nesse período: corrigem bugs do motor, constroem peças novas aprovadas, melhoram
a tela de placar e ajudam os autores que travarem.

---

## Etapa 7: Ensaio geral

1. **Congelar conteúdo:** nada de sala nova. Só correções.
2. **Teste com turmas convidadas** (que não vão competir no mesmo tema, para não vazar respostas):
   medir tempo por sala, onde travam, se a IA aprovou/reprovou de forma justa.
3. **Balancear** para ~40 min por tema. Temas muito mais longos ou curtos devem ser ajustados,
   mesmo com ranking separado.
4. **Ensaio de carga:** todas as equipes simultâneas que a gincana terá, cada uma com seu host,
   todas falando com o mesmo PC placar. Conferir: rede, placar, custo e velocidade da IA.
5. **Ensaiar falhas:** derrubar a internet (quiz reserva funciona?), fechar o jogo de um jogador
   (os outros continuam?), reiniciar o PC placar (resultados preservados?).
6. **Exportar** o jogo (*Project → Export → Windows Desktop*), gerar a versão `v1.0` (tag no
   Git) e copiar o executável para os PCs da gincana.

✅ **Demo de aprovação:** uma rodada completa simulada, com placar no telão.

---

## Etapa 8: Gincana

**Roteiro do organizador**

1. Ligar o PC placar e rodar o servidor. Abrir `/placar` no telão.
2. Conferir que cada PC tem a versão `v1.0` e o IP do placar configurado.
3. Equipes de 2 a 4 escolhem o tema. Um PC por equipe é o host.
4. Autores atuam como **suporte técnico** e não podem dar respostas.
5. Ao final, conferir o ranking de cada tema e exportar o banco (`server/placar.db`).
6. Depois das rodadas: conversa curta explicando os casos e os conceitos de cada tema.

---

## Como a IA (Claude Code / Muse Spark) entra no trabalho dos alunos

- Antes de pedir código, a IA deve ler `CLAUDE.md` (o Claude Code faz isso automaticamente).
  Lá estão as regras: cada um só mexe na própria pasta, usa peças do catálogo etc.
- Bons pedidos: *"Configure a peça TecladoSenha na sala1 de química para o código 7425"*,
  *"Explique linha a linha este script"*, *"Por que minha porta não abre para o outro jogador?"*.
- Pedidos ruins: *"Faça meu escape room de química"* (gera algo fora do padrão, que não integra).
- Antes de abrir o PR: pedir à IA *"Revise meu diff contra as regras do CLAUDE.md"*.
