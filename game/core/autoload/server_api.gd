extends Node
## Comunicação com o servidor Python (placar + NPC com IA).
## Disponível em qualquer script como "ServerAPI". Todas as funções usam "await":
##
##     var r := await ServerAPI.criar_partida("quimica", "Equipe Azul", "2B", 3)
##     if r["ok"]:
##         GameConfig.partida_id = r["partida_id"]
##
## Toda resposta é um Dictionary com "ok" (true/false). Se "ok" for false, "erro" explica.
## IMPORTANTE: só o HOST deve chamar criar_partida e concluir_partida.


func verificar_servidor() -> Dictionary:
	return await _requisitar(HTTPClient.METHOD_GET, "/saude")


## Chame quando o host clicar em "Iniciar". O tempo oficial começa no servidor.
func criar_partida(tema: String, equipe: String, turma: String, jogadores: int) -> Dictionary:
	return await _requisitar(HTTPClient.METHOD_POST, "/api/partidas", {
		"tema": tema,
		"equipe": equipe,
		"turma": turma,
		"jogadores": jogadores,
	})


## Chame quando a última porta abrir. Devolve "tempo_segundos" calculado pelo servidor.
func concluir_partida(partida_id: String) -> Dictionary:
	return await _requisitar(HTTPClient.METHOD_POST, "/api/partidas/%s/concluir" % partida_id)


## Envia a fala da equipe ao NPC. Resposta:
##   modo = "ia"   -> "fala" (texto do NPC) e, se aprovado, "codigo"
##   modo = "quiz" -> a IA está indisponível: mostrar "pergunta" e "alternativas"
func conversar_npc(npc_id: String, partida_id: String, mensagem: String) -> Dictionary:
	return await _requisitar(HTTPClient.METHOD_POST, "/api/npc/%s/conversar" % npc_id, {
		"partida_id": partida_id,
		"mensagem": mensagem,
	})


## Responde o quiz reserva. "alternativa" começa em 0. Se correta, vem "codigo".
func responder_quiz(npc_id: String, partida_id: String, alternativa: int) -> Dictionary:
	return await _requisitar(HTTPClient.METHOD_POST, "/api/npc/%s/quiz" % npc_id, {
		"partida_id": partida_id,
		"alternativa": alternativa,
	})


func _requisitar(metodo: HTTPClient.Method, caminho: String, corpo: Dictionary = {}) -> Dictionary:
	var http := HTTPRequest.new()
	http.timeout = 25.0  # a IA pode demorar alguns segundos
	add_child(http)

	var cabecalhos := PackedStringArray([
		"Content-Type: application/json",
		"X-Token-Evento: " + GameConfig.token_evento,
	])
	var dados: String = "" if corpo.is_empty() else JSON.stringify(corpo)
	var erro := http.request(GameConfig.url_servidor + caminho, cabecalhos, metodo, dados)
	if erro != OK:
		http.queue_free()
		return {"ok": false, "erro": "não foi possível enviar (%s)" % error_string(erro)}

	# request_completed entrega: [resultado, status_http, cabecalhos, corpo]
	var resposta: Array = await http.request_completed
	http.queue_free()

	var resultado: int = resposta[0]
	var status: int = resposta[1]
	var texto: String = (resposta[3] as PackedByteArray).get_string_from_utf8()

	if resultado != HTTPRequest.RESULT_SUCCESS:
		return {"ok": false, "erro": "sem conexão com o servidor em " + GameConfig.url_servidor}

	var json = JSON.parse_string(texto)
	if status >= 400 or typeof(json) != TYPE_DICTIONARY:
		return {"ok": false, "erro": "servidor respondeu %d: %s" % [status, texto]}

	json["ok"] = true
	return json
