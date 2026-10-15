extends Control
## Menu inicial PROVISÓRIO: escolha do tema + teste de conexão com o placar.
## Os gerentes vão substituir por: tema -> criar/entrar na partida -> lobby (Etapa 3).

var _status: Label


func _ready() -> void:
	var caixa := VBoxContainer.new()
	caixa.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	caixa.add_theme_constant_override("separation", 12)
	add_child(caixa)

	var titulo := Label.new()
	titulo.text = "Escape Room dos Cursos Técnicos\nEscolha o tema da sua equipe"
	titulo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	caixa.add_child(titulo)

	for tema in GameConfig.TEMAS:
		var botao := Button.new()
		botao.text = tema["nome"]
		botao.custom_minimum_size = Vector2(320, 44)
		botao.modulate = tema["cor"].lightened(0.4)
		botao.pressed.connect(_ao_escolher_tema.bind(tema["id"]))
		caixa.add_child(botao)

	var botao_teste := Button.new()
	botao_teste.text = "Testar conexão com o placar"
	botao_teste.pressed.connect(_testar_servidor)
	caixa.add_child(botao_teste)

	_status = Label.new()
	_status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	caixa.add_child(_status)


func _ao_escolher_tema(id_tema: String) -> void:
	GameConfig.tema_escolhido = id_tema
	_status.text = "Tema escolhido: %s\n(o lobby será construído pelos gerentes na Etapa 3)" % \
		GameConfig.dados_do_tema(id_tema)["nome"]


func _testar_servidor() -> void:
	_status.text = "Testando " + GameConfig.url_servidor + " ..."
	var r: Dictionary = await ServerAPI.verificar_servidor()
	if r["ok"]:
		_status.text = "Placar OK! IA configurada: %s" % ("sim" if r.get("ia_configurada") else "não (modo quiz)")
	else:
		_status.text = "Falhou: " + str(r["erro"])
