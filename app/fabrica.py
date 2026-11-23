"""Arma el agente con sus dependencias a partir de la configuración."""
from __future__ import annotations

import logging

from app.agent.agente import Agente
from app.agent.fewshot import SelectorEjemplos, cargar_banco
from app.agent.trazas import RegistroTrazas
from app.config import Config, cargar_config
from app.llm import ClienteLLM
from app.rag.indice import Recuperador

log = logging.getLogger(__name__)


def construir_agente(cfg: Config | None = None, cliente_redaccion=None, cliente_decision=None) -> Agente:
    cfg = cfg or cargar_config()
    recuperador = Recuperador(cfg.dir_indice, cfg.embeddings_backend, cfg.embeddings_modelo, cfg.dir_cache_modelos)
    banco = cargar_banco(cfg.dir_banco)
    selector = SelectorEjemplos(banco, recuperador.fragmentos, recuperador.embedder)
    if cliente_decision is None and cfg.decision.api_key:
        cliente_decision = ClienteLLM(cfg.decision, timeout=30)
    if cliente_decision is None:
        log.warning("Sin DECISION_API_KEY: la clasificación usará solo reglas y la herramienta solo expresiones explícitas")
    cliente_redaccion = cliente_redaccion or ClienteLLM(cfg.redaccion)
    log.info("Agente listo: %d fragmentos, %d ejemplos, redactor=%s, few-shot=%s (%s)",
             len(recuperador.fragmentos), len(banco), cliente_redaccion.nombre, cfg.fewshot_activo, cfg.fewshot_criterio)
    return Agente(cfg, recuperador, selector, cliente_decision, cliente_redaccion, RegistroTrazas(cfg.dir_trazas))
