extends Node
## Configurações globais do jogo. Disponível em qualquer script como "GameConfig".

## Os 5 temas. "id" é o nome da pasta em res://rooms/ e o tema usado no servidor.
const TEMAS: Array = [
	{"id": "mecatronica", "nome": "Mecatrônica", "sigla": "MECA", "cor": Color("#e07a1f")},
	{"id": "eletrotecnica", "nome": "Eletrotécnica", "sigla": "ELET", "cor": Color("#f2c230")},
	{"id": "seguranca", "nome": "Segurança do Trabalho", "sigla": "SEGT", "cor": Color("#2f9e44")},
	{"id": "quimica", "nome": "Química", "sigla": "QUIM", "cor": Color("#7048e8")},
	{"id": "informatica", "nome": "Informática", "sigla": "INFO", "cor": Color("#1c7ed6")},
]

const MIN_JOGADORES: int = 2
const MAX_JOGADORES: int = 4

var url_servidor: String = "http://127.0.0.1:8000"
var token_evento: String = ""

## Preenchidos durante a partida.
var tema_escolhido: String = ""
var partida_id: String = ""


func _ready() -> void:
	_carregar_config_evento()


## Lê evento.cfg: primeiro ao lado do executável (jogo exportado), depois res://config/.
func _carregar_config_evento() -> void:
	var caminhos: Array[String] = [
		OS.get_executable_path().get_base_dir().path_join("evento.cfg"),
		"res://config/evento.cfg",
	]
	for caminho in caminhos:
		var cfg := ConfigFile.new()
		if cfg.load(caminho) == OK:
			url_servidor = cfg.get_value("servidor", "url", url_servidor)
			token_evento = cfg.get_value("servidor", "token", token_evento)
			print("Configuração do evento carregada de ", caminho)
			return
	push_warning("evento.cfg não encontrado; usando servidor padrão " + url_servidor)


func dados_do_tema(id_tema: String) -> Dictionary:
	for tema in TEMAS:
		if tema["id"] == id_tema:
			return tema
	return {}
