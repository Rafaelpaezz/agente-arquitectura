"""Lectura del corpus y fragmentación por estructura del documento.

Estrategia (ver docs/adr/0002-fragmentacion-e-indexacion.md):
  1. Markdown (.md) y AsciiDoc (.adoc) se cortan por encabezados. Cada fragmento conserva la
     ruta de secciones ("Availability patterns > Availability in numbers"), que es lo que se cita.
  2. PDF se lee página por página; la cita es el número de página.
  3. Si una sección o página supera MAX_CARACTERES se parte por párrafos, con un párrafo de
     solapamiento para no cortar una idea a la mitad.
  4. Se descartan fragmentos de menos de MIN_CARACTERES (encabezados sueltos, listas de enlaces).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

MAX_CARACTERES = 1500
MIN_CARACTERES = 120


@dataclass
class Fragmento:
    id: str
    doc_id: str
    doc_titulo: str
    archivo: str
    seccion: str
    pagina: int | None
    texto: str

    def cita(self) -> str:
        """Referencia corta que el agente pone en la respuesta: [DOC, sección] o [DOC, p. N]."""
        if self.pagina is not None:
            return f"[{self.doc_id}, p. {self.pagina}]"
        return f"[{self.doc_id}, §{self.seccion}]"

    def para_embedding(self) -> str:
        # Se antepone la ruta de secciones: ayuda a recuperar fragmentos cortos por su tema.
        return f"{self.doc_titulo}. {self.seccion}\n{self.texto}"

    def a_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Limpieza
# ---------------------------------------------------------------------------
_ADOC_BASURA = re.compile(
    r"^(ifdef::.*|ifndef::.*|endif::.*|\[\[.*\]\]|\[role=.*\]|\*{4}|image::.*|:[\w-]+:.*|include::.*|\[options=.*\]|\[cols=.*\])$"
)


def _limpiar_linea(linea: str) -> str:
    linea = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", linea)              # imágenes markdown
    linea = re.sub(r"\[\]\([^)]*\)", "", linea)                       # enlaces vacíos (insignias)
    linea = re.sub(r"\[([^\]]+)\]\((?:[^()]|\([^)]*\))*\)", r"\1", linea)  # [texto](url) -> texto
    linea = re.sub(r"https?://\S+\[([^\]]*)\]", r"\1", linea)       # url[texto] (asciidoc)
    linea = re.sub(r"<[^>]+>", "", linea)                            # html
    return linea.rstrip()


def _es_basura_adoc(linea: str) -> bool:
    return bool(_ADOC_BASURA.match(linea.strip()))


# ---------------------------------------------------------------------------
# Cortes por encabezado
# ---------------------------------------------------------------------------
def _secciones_texto(texto: str, marcador: str) -> list[tuple[str, str]]:
    """Devuelve [(ruta_de_seccion, cuerpo)] cortando por encabezados '#' (md) o '=' (adoc)."""
    patron = re.compile(rf"^({re.escape(marcador)}+)\s+(.+?)\s*$")
    pila: list[tuple[int, str]] = []
    resultado: list[tuple[str, list[str]]] = [("", [])]
    en_codigo = False
    for linea_cruda in texto.splitlines():
        if linea_cruda.strip().startswith("```"):
            en_codigo = not en_codigo
        m = None if en_codigo else patron.match(linea_cruda)
        if m:
            nivel = len(m.group(1))
            titulo = _limpiar_linea(m.group(2)).strip("# ").strip()
            if re.fullmatch(r"\{.*\}", titulo):     # encabezados de plantilla: {title of option 1}
                titulo = "Plantilla" if nivel <= 1 else titulo.strip("{}")
            while pila and pila[-1][0] >= nivel:
                pila.pop()
            pila.append((nivel, titulo))
            resultado.append((" > ".join(t for _, t in pila if t), []))
            continue
        if marcador == "=" and _es_basura_adoc(linea_cruda):
            continue
        resultado[-1][1].append(_limpiar_linea(linea_cruda))
    return [(ruta, "\n".join(lineas).strip()) for ruta, lineas in resultado]


def _partir(texto: str) -> list[str]:
    """Parte un texto largo en trozos <= MAX_CARACTERES por párrafos, con 1 párrafo de solapamiento."""
    if len(texto) <= MAX_CARACTERES:
        return [texto]
    parrafos = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    trozos, actual = [], []
    for p in parrafos:
        while len(p) > MAX_CARACTERES:  # párrafo gigante: se corta por oraciones/longitud
            corte = p.rfind(". ", 0, MAX_CARACTERES)
            corte = corte + 1 if corte > MAX_CARACTERES // 2 else MAX_CARACTERES
            parrafos_extra, p = p[:corte], p[corte:].strip()
            if actual:
                trozos.append("\n\n".join(actual))
                actual = []
            trozos.append(parrafos_extra)
        if sum(len(x) for x in actual) + len(p) > MAX_CARACTERES and actual:
            trozos.append("\n\n".join(actual))
            actual = [actual[-1]] if len(actual[-1]) < MAX_CARACTERES // 3 else []
        actual.append(p)
    if actual:
        trozos.append("\n\n".join(actual))
    return trozos


# Secciones que solo son listas de enlaces o noticias: no aportan contenido citable.
_SECCIONES_DE_ENLACES = re.compile(r"(Source\(s\) and further reading|^.*> (News|Contents|Older versions|License)$)", re.I)


def _id_fragmento(doc_id: str, archivo: str, seccion: str, pagina, i: int) -> str:
    base = f"{doc_id}|{archivo}|{seccion}|{pagina}|{i}"
    return f"{doc_id}-" + hashlib.sha1(base.encode()).hexdigest()[:10]


# ---------------------------------------------------------------------------
# Lectura de documentos
# ---------------------------------------------------------------------------
def _fragmentos_de_texto(doc: dict, ruta: Path, marcador: str) -> list[Fragmento]:
    texto = ruta.read_text(encoding="utf-8", errors="ignore")
    salida = []
    for seccion, cuerpo in _secciones_texto(texto, marcador):
        if len(cuerpo) < MIN_CARACTERES or _SECCIONES_DE_ENLACES.search(seccion):
            continue
        seccion = seccion or ruta.stem
        for i, trozo in enumerate(_partir(cuerpo)):
            if len(trozo) < MIN_CARACTERES:
                continue
            salida.append(Fragmento(
                id=_id_fragmento(doc["id"], ruta.name, seccion, None, i),
                doc_id=doc["id"], doc_titulo=doc["titulo"], archivo=ruta.name,
                seccion=seccion, pagina=None, texto=trozo,
            ))
    return salida


def _fragmentos_de_pdf(doc: dict, ruta: Path) -> list[Fragmento]:
    from pypdf import PdfReader

    salida = []
    for num, pagina in enumerate(PdfReader(str(ruta)).pages, start=1):
        texto = (pagina.extract_text() or "").strip()
        texto = re.sub(r"[ \t]+", " ", texto)
        if len(texto) < MIN_CARACTERES:
            continue
        for i, trozo in enumerate(_partir(texto)):
            if len(trozo) < MIN_CARACTERES:
                continue
            salida.append(Fragmento(
                id=_id_fragmento(doc["id"], ruta.name, "", num, i),
                doc_id=doc["id"], doc_titulo=doc["titulo"], archivo=ruta.name,
                seccion=f"página {num}", pagina=num, texto=trozo,
            ))
    return salida


def cargar_manifiesto(dir_corpus: Path) -> list[dict]:
    with open(dir_corpus / "fuentes.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)["documentos"]


def fragmentar_corpus(dir_corpus: Path) -> tuple[list[Fragmento], list[str]]:
    """Recorre el manifiesto y devuelve (fragmentos, avisos)."""
    fragmentos: list[Fragmento] = []
    avisos: list[str] = []
    for doc in cargar_manifiesto(dir_corpus):
        if doc.get("indexado", True) is False:
            continue  # referencia citada en la lista de fuentes, fuera del índice
        ruta = dir_corpus / doc["ruta"]
        if not ruta.exists():
            avisos.append(f"{doc['id']}: no se encontró {ruta.relative_to(dir_corpus)} (ver corpus/externo/README.md)")
            continue
        archivos = sorted(ruta.rglob("*")) if ruta.is_dir() else [ruta]
        antes = len(fragmentos)
        for archivo in archivos:
            if archivo.name.upper().startswith("LICENSE") or archivo.name == "README.md" and archivo.parent.name == "externo":
                continue
            sufijo = archivo.suffix.lower()
            if sufijo == ".md":
                fragmentos += _fragmentos_de_texto(doc, archivo, "#")
            elif sufijo == ".adoc":
                fragmentos += _fragmentos_de_texto(doc, archivo, "=")
            elif sufijo == ".pdf":
                fragmentos += _fragmentos_de_pdf(doc, archivo)
        if len(fragmentos) == antes:
            avisos.append(f"{doc['id']}: no produjo fragmentos")
    return fragmentos, avisos
