from app.evaluacion.rubrica import calificar, citacion, estructura, formato, herramienta

BUENA = """**Respuesta:** La disponibilidad total es 99.8001 %.
**Explicación:**
- En serie se multiplican las disponibilidades [SDP, §Availability patterns > Availability in numbers]
- Puntos únicos de falla: web, bd.
**Fuentes:** [SDP, §Availability patterns > Availability in numbers]"""


def test_formato():
    assert formato(BUENA) == 1
    assert formato("Respuesta suelta sin etiquetas") == 0


def test_estructura():
    assert estructura(BUENA) == 1
    assert estructura(BUENA.replace("- Puntos únicos de falla: web, bd.\n", "")) == 0  # una sola viñeta


def test_herramienta():
    r = {"disponibilidad_pct": 99.800100, "puntos_unicos_de_falla": ["web", "bd"]}
    assert herramienta(BUENA, r) == 1
    assert herramienta(BUENA.replace("99.8001", "99.5"), r) == 0
    assert herramienta(BUENA, None) is None


def test_citacion():
    permitidas = {"[SDP, §Availability patterns > Availability in numbers]"}
    assert citacion(BUENA, permitidas) == 1
    assert citacion(BUENA, {"[12F, §III. Config]"}) == 0
    assert citacion("**Respuesta:** sin citas", permitidas) == 0


def test_calificar_promedia_solo_aplicables():
    c = calificar(BUENA, {"[SDP, §Availability patterns > Availability in numbers]"}, None)
    assert c["herramienta"] is None and c["puntaje"] == 1.0
