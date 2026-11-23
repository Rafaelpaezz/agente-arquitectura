"""Pruebas del ciclo de decisión con un modelo simulado (no llama a ninguna API)."""
from pathlib import Path

import pytest

from app.agent.agente import Agente, extraer_expresion_explicita
from app.agent.clasificador import clasificar, clasificar_por_reglas
from app.agent.fewshot import SelectorEjemplos, cargar_banco
from app.config import Config, RAIZ
from app.rag.fragmentacion import fragmentar_corpus
from app.rag.indice import Recuperador, construir_indice


class LLMSimulado:
    """Devuelve una respuesta con el formato pedido y cita el primer fragmento que reciba."""
    nombre = "simulado"

    def __init__(self):
        self.ultimos_mensajes = None

    def chat(self, mensajes, **_):
        self.ultimos_mensajes = mensajes
        usuario = mensajes[-1]["content"]
        cita = usuario.split('cita="')[1].split('"')[0] if 'cita="' in usuario else ""
        return (f"**Respuesta:** respuesta simulada.\n**Explicación:**\n- punto uno {cita}\n- punto dos {cita}\n"
                f"**Fuentes:** {cita}", 0.01)


@pytest.fixture(scope="module")
def agente(tmp_path_factory):
    dir_indice = tmp_path_factory.mktemp("indice")
    fragmentos, _ = fragmentar_corpus(RAIZ / "corpus")
    construir_indice(fragmentos, "tfidf", "", dir_indice)
    cfg = Config(dir_indice=dir_indice, embeddings_backend="tfidf", rag_umbral=0.05,
                 dir_trazas=tmp_path_factory.mktemp("trazas"))
    rec = Recuperador(dir_indice, "tfidf", "")
    selector = SelectorEjemplos(cargar_banco(cfg.dir_banco), rec.fragmentos, rec.embedder)
    return Agente(cfg, rec, selector, cliente_decision=None, cliente_redaccion=LLMSimulado())


@pytest.mark.parametrize("pregunta,tipo", [
    ("¿Qué es el teorema CAP?", "conceptual"),
    ("hola", "saludo"),
    ("Calcula serie(a=0.99, b=0.99)", "calculo"),
    ("Latencia vs consistencia: ¿qué se sacrifica?", "compromisos"),
    ("¿Qué patrón de caché me conviene usar para un sistema con muchas lecturas?", "seleccion"),
])
def test_reglas(pregunta, tipo):
    c = clasificar_por_reglas(pregunta)
    assert c is not None and c.tipo == tipo


def test_fuera_de_dominio_sin_modelo():
    assert clasificar("¿Cuál es la capital de Francia?").tipo == "fuera_de_dominio"


def test_extraer_expresion():
    assert extraer_expresion_explicita("calcule serie(a=1, paralelo(b=0.9, c=0.9)) por favor") == \
        "serie(a=1, paralelo(b=0.9, c=0.9))"
    assert extraer_expresion_explicita("sin expresión") is None


def test_rag_cita_fragmento(agente):
    t = agente.responder("¿Qué es el patrón write-through?", guardar=False)
    assert t.accion == "rag" and t.fragmentos
    revisar = [p for p in t.traza.datos["pasos"] if p["paso"] == "revisar_citas"][0]
    assert not revisar["citas_invalidas"] and not revisar["sin_citas"]


def test_herramienta(agente):
    t = agente.responder("serie(api=99.9%, bd=99.9%)", guardar=False)
    assert t.accion == "herramienta"
    assert "99.8001" in t.resultado_herramienta


def test_correccion_calculo_sin_numeros(agente):
    t = agente.responder("¿Cómo se calcula la disponibilidad en serie?", guardar=False)
    pasos = [p["paso"] for p in t.traza.datos["pasos"]]
    assert "corregir" in pasos and t.accion == "rag"


def test_error_de_topologia(agente):
    t = agente.responder("serie(api=99.9%, paralelo(bd1=99.5%, bd2=99.5%)", guardar=False)
    assert t.accion == "herramienta_error" and "No pude calcular" in t.respuesta


def test_directa_no_llama_al_modelo(agente):
    agente.cliente_redaccion.ultimos_mensajes = None
    t = agente.responder("hola", guardar=False)
    assert t.accion == "directa" and agente.cliente_redaccion.ultimos_mensajes is None


def test_fewshot_cambia_segun_la_pregunta(agente):
    agente.responder("¿Qué es una CDN?", fewshot=True, guardar=False)
    ids_1 = [p for p in agente.cliente_redaccion.ultimos_mensajes if p["role"] == "assistant"]
    agente.responder("¿Qué es la replicación maestro-esclavo?", fewshot=True, guardar=False)
    ids_2 = [p for p in agente.cliente_redaccion.ultimos_mensajes if p["role"] == "assistant"]
    assert ids_1 and ids_2 and ids_1 != ids_2


def test_sin_fewshot_no_hay_ejemplos(agente):
    agente.responder("¿Qué es una CDN?", fewshot=False, guardar=False)
    roles = [m["role"] for m in agente.cliente_redaccion.ultimos_mensajes]
    assert roles == ["system", "user"]
