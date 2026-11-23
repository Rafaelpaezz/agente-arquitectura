"""Canal de mensajería: Telegram Bot API con long polling (no necesita dominio, IP pública ni certificado).

Comandos:
  /start, /ayuda     presentación
  /fuentes           documentos indexados en el corpus
  /traza             decisiones que tomó el agente en la última pregunta de este chat
  /fewshot on|off    activa o desactiva el banco de ejemplos en este chat (para la demostración)
"""
from __future__ import annotations

import asyncio
import html
import logging
import re
from collections import Counter

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.agent.prompts import RESPUESTA_DIRECTA
from app.config import cargar_config
from app.fabrica import construir_agente

log = logging.getLogger(__name__)
LIMITE_TELEGRAM = 4000


def a_html(texto: str) -> str:
    """Convierte el **negrita** del modelo a HTML de Telegram, escapando todo lo demás."""
    seguro = html.escape(texto)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", seguro)


def partir(texto: str) -> list[str]:
    partes = []
    while len(texto) > LIMITE_TELEGRAM:
        corte = texto.rfind("\n", 0, LIMITE_TELEGRAM)
        corte = corte if corte > 0 else LIMITE_TELEGRAM
        partes.append(texto[:corte])
        texto = texto[corte:]
    return partes + [texto]


async def _mantener_escribiendo(chat, parar: asyncio.Event) -> None:
    """Telegram borra la acción 'escribiendo…' a los 5 s: se renueva cada 4 s mientras el agente trabaja."""
    while not parar.is_set():
        await chat.send_action(ChatAction.TYPING)
        try:
            await asyncio.wait_for(parar.wait(), timeout=4)
        except asyncio.TimeoutError:
            pass


class BotArquitectura:
    def __init__(self):
        self.cfg = cargar_config()
        self.agente = construir_agente(self.cfg)
        self.ultima_traza: dict[int, str] = {}
        self.fewshot_por_chat: dict[int, bool] = {}

    async def inicio(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(RESPUESTA_DIRECTA["saludo"])

    async def fuentes(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        conteo = Counter((f.doc_id, f.doc_titulo) for f in self.agente.recuperador.fragmentos)
        lineas = [f"• {d}: {t} ({n} fragmentos)" for (d, t), n in sorted(conteo.items())]
        await update.message.reply_text("Documentos indexados:\n" + "\n".join(lineas))

    async def traza(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        texto = self.ultima_traza.get(update.effective_chat.id, "Aún no hay preguntas en este chat.")
        for parte in partir(texto):
            await update.message.reply_text(parte)

    async def fewshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        valor = (context.args[0].lower() if context.args else "")
        if valor not in ("on", "off"):
            actual = self.fewshot_por_chat.get(update.effective_chat.id, self.cfg.fewshot_activo)
            await update.message.reply_text(f"Few-shot está {'activo' if actual else 'inactivo'}. Use /fewshot on o /fewshot off.")
            return
        self.fewshot_por_chat[update.effective_chat.id] = valor == "on"
        await update.message.reply_text(f"Few-shot {'activado' if valor == 'on' else 'desactivado'} para este chat.")

    async def mensaje(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        pregunta = update.message.text or ""
        parar = asyncio.Event()
        indicador = asyncio.create_task(_mantener_escribiendo(chat, parar))
        try:
            # El agente es síncrono (llamadas HTTP al modelo): se ejecuta en un hilo para no bloquear el bot.
            turno = await asyncio.to_thread(self.agente.responder, pregunta, chat.id,
                                            self.fewshot_por_chat.get(chat.id))
        except Exception:  # noqa: BLE001
            log.exception("Error respondiendo")
            parar.set()
            await update.message.reply_text("Ocurrió un error inesperado. Intente de nuevo.")
            return
        finally:
            parar.set()
            await indicador
        self.ultima_traza[chat.id] = turno.traza.resumen_legible()
        for parte in partir(turno.respuesta):
            try:
                await update.message.reply_text(a_html(parte), parse_mode=ParseMode.HTML)
            except Exception:  # noqa: BLE001 - si el HTML falla, se envía como texto plano
                await update.message.reply_text(parte)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    bot = BotArquitectura()
    if not bot.cfg.telegram_token:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN en el archivo .env")
    app = Application.builder().token(bot.cfg.telegram_token).concurrent_updates(True).build()
    app.add_handler(CommandHandler(["start", "ayuda"], bot.inicio))
    app.add_handler(CommandHandler("fuentes", bot.fuentes))
    app.add_handler(CommandHandler("traza", bot.traza))
    app.add_handler(CommandHandler("fewshot", bot.fewshot))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.mensaje))
    log.info("Bot iniciado con long polling")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
