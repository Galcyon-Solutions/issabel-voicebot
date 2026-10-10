#!/usr/bin/env python3
"""Agente de voz PURO: Asterisk (chan_websocket) <-> Deepgram Voice Agent.

Un solo archivo, sin librerias de telefonia de por medio: solo `websockets`.
Sirve para entender QUE pasa en una llamada. El ejemplo con galcymedia hace lo
mismo con mas cuidado (control de flujo, transferencia, silencios, pruebas).

    DEEPGRAM_API_KEY=... python3 -u agente_puro.py

El dialplan marca el canal WebSocket y Asterisk se conecta aqui:

    Dial(WebSocket/voicepuro/c(alaw)f(json))     ->  ws://127.0.0.1:9001/media

Lo que hace, en orden:

    1. Escucha en el puerto 9001 y espera a que Asterisk se conecte.
    2. Asterisk manda un evento de texto MEDIA_START (formato del audio).
    3. Abrimos otra conexion hacia Deepgram y le mandamos la configuracion.
    4. Respondemos ANSWER a Asterisk (sin esto la llamada no se une).
    5. Dos cosas en paralelo, hasta que cuelguen:
         voz de la persona (Asterisk, binario) -> Deepgram
         voz del bot       (Deepgram, binario) -> Asterisk
    6. Si la persona habla encima del bot: FLUSH_MEDIA y se descarta su voz.
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime

import websockets

# ----------------------------------------------------------------------------
# 0. Configuracion (todo por variables de entorno)
# ----------------------------------------------------------------------------
API_KEY = os.environ.get("DEEPGRAM_API_KEY", "")
HOST = os.environ.get("MEDIA_HOST", "127.0.0.1")   # solo local: este servidor no autentica
PORT = int(os.environ.get("MEDIA_PORT", "9001"))   # 9000 lo usa el ejemplo de galcymedia
MODELO_OIDO = os.environ.get("DEEPGRAM_MODEL", "nova-3")        # o flux-general-multi
VOZ = os.environ.get("DEEPGRAM_VOICE", "aura-2-celeste-es")
IDIOMA = os.environ.get("AI_LANGUAGE", "es")
DEPURAR = os.environ.get("DEBUG_EVENTOS", "") == "1"   # imprime el tipo de cada evento de Deepgram

DEEPGRAM_URL = "wss://agent.deepgram.com/v1/agent/converse"

SALUDO = "Hola, gracias por llamar. En que te puedo ayudar?"
PROMPT = (
    "Eres una asistente telefonica amable. Hablas en espanol, con frases cortas "
    "porque la persona te escucha por telefono. Si no sabes algo, dilo. "
    "No uses listas ni simbolos: todo lo que escribes se pronuncia en voz alta."
)

# Asterisk entrega el audio por el canal en el codec del Dial (alaw o ulaw, 8 kHz).
# Deepgram usa otro nombre para ulaw.
CODEC_DEEPGRAM = {"alaw": "alaw", "ulaw": "mulaw"}


def log(*partes):
    print(datetime.now().strftime("%H:%M:%S"), *partes, flush=True)


# ----------------------------------------------------------------------------
# 1. El mensaje de configuracion que Deepgram espera primero
# ----------------------------------------------------------------------------
def configuracion(formato: str) -> dict:
    codec = CODEC_DEEPGRAM[formato]
    if MODELO_OIDO.startswith("flux"):
        # Flux (esquema v2): el propio modelo decide cuando terminaste de hablar.
        # Usa language_hints, no language. flux-general-en solo entiende ingles.
        oido = {"type": "deepgram", "version": "v2", "model": MODELO_OIDO,
                "language_hints": [IDIOMA], "eot_threshold": 0.7}
    else:
        # nova-3 (esquema v1): lo de siempre.
        oido = {"type": "deepgram", "version": "v1", "model": MODELO_OIDO,
                "language": IDIOMA}
    return {
        "type": "Settings",
        "audio": {
            "input": {"encoding": codec, "sample_rate": 8000},
            "output": {"encoding": codec, "sample_rate": 8000, "container": "none"},
        },
        "agent": {
            "listen": {"provider": oido},
            "think": {"provider": {"type": "open_ai", "model": "gpt-4o-mini"},
                      "prompt": PROMPT},
            "speak": {"provider": {"type": "deepgram", "model": VOZ}},
            "greeting": SALUDO,
        },
    }


# ----------------------------------------------------------------------------
# 2. Una llamada
# ----------------------------------------------------------------------------
async def atender_llamada(asterisk):
    # 2.1 Primer mensaje de Asterisk: MEDIA_START con el formato del audio
    inicio = json.loads(await asterisk.recv())
    if inicio.get("event") != "MEDIA_START":
        log("se esperaba MEDIA_START y llego:", inicio)
        return
    formato = inicio["format"]                      # "alaw" o "ulaw"
    tamano_trama = inicio["optimal_frame_size"]     # 160 bytes = 20 ms de audio a 8 kHz
    if formato not in CODEC_DEEPGRAM or tamano_trama == 0:
        log("formato no soportado en este ejemplo:", formato)
        return
    log(f"llamada: formato={formato} trama={tamano_trama}B")

    # 2.2 Conectar con Deepgram y mandar la configuracion
    async with websockets.connect(
        DEEPGRAM_URL, additional_headers={"Authorization": f"Token {API_KEY}"}
    ) as deepgram:
        await deepgram.send(json.dumps(configuracion(formato)))

        # 2.3 Contestar la pata WebSocket: sin ANSWER Asterisk no une las dos patas
        await asterisk.send(json.dumps({"command": "ANSWER"}))

        # Estado compartido entre las dos tareas
        puede_enviar = asyncio.Event()     # Asterisk avisa con XOFF/XON si su cola esta llena
        puede_enviar.set()
        estado = {"descartar_hasta": 0.0}  # hasta cuando se tira la voz vieja del bot ya interrumpido

        # 2.4 Persona -> Deepgram, y eventos de Asterisk
        async def desde_asterisk():
            async for mensaje in asterisk:
                if isinstance(mensaje, bytes):
                    await deepgram.send(mensaje)            # la voz, tal cual
                    continue
                evento = json.loads(mensaje).get("event")
                if evento == "MEDIA_XOFF":
                    puede_enviar.clear()                    # cola llena: parar de mandar
                elif evento == "MEDIA_XON":
                    puede_enviar.set()                      # hay lugar otra vez
                elif evento == "DTMF_END":
                    log("tecla:", json.loads(mensaje).get("digit"))

        # 2.5 Deepgram -> Asterisk
        sobrante = bytearray()

        async def enviar_a_asterisk(audio: bytes):
            # Asterisk SOLO acepta tramas completas de `tamano_trama` bytes: lo que sobra
            # al final de un mensaje lo TIRA (voz entrecortada sin ningun error).
            # Por eso se acumula y se manda en multiplos exactos.
            sobrante.extend(audio)
            while len(sobrante) >= tamano_trama:
                n = len(sobrante) - len(sobrante) % tamano_trama
                try:
                    await asyncio.wait_for(puede_enviar.wait(), timeout=3)
                except asyncio.TimeoutError:
                    log("Asterisk no mando XON en 3 s: sigo igual")
                    puede_enviar.set()
                await asterisk.send(bytes(sobrante[:n]))
                del sobrante[:n]

        async def desde_deepgram():
            async for mensaje in deepgram:
                if isinstance(mensaje, bytes):              # la voz del bot
                    if time.monotonic() >= estado["descartar_hasta"]:
                        await enviar_a_asterisk(mensaje)
                    continue
                evento = json.loads(mensaje)
                tipo = evento.get("type")
                if DEPURAR:
                    log("evento Deepgram:", tipo)
                if tipo == "UserStartedSpeaking":
                    # La persona hablo encima: vaciar lo que Asterisk tenia en cola y
                    # descartar la voz del bot que todavia viene en camino. El descarte dura
                    # solo medio segundo: si fuera una bandera que espera a AgentStartedSpeaking
                    # y ese aviso llegara tarde o no llegara, el bot hablaria sin que nadie lo oiga.
                    estado["descartar_hasta"] = time.monotonic() + 0.5
                    sobrante.clear()
                    await asterisk.send(json.dumps({"command": "FLUSH_MEDIA"}))
                elif tipo == "AgentStartedSpeaking":
                    estado["descartar_hasta"] = 0.0           # empieza una respuesta nueva
                elif tipo == "ConversationText":
                    log(f"[{evento.get('role')}] {evento.get('content')}")
                elif tipo in ("Error", "Warning"):
                    log("Deepgram", tipo, evento)

        # 2.6 Las dos tareas hasta que una termine (la persona cuelga o Deepgram se cae)
        tareas = [asyncio.create_task(desde_asterisk()), asyncio.create_task(desde_deepgram())]
        _, pendientes = await asyncio.wait(tareas, return_when=asyncio.FIRST_COMPLETED)
        for t in pendientes:
            t.cancel()
    log("llamada terminada")


# ----------------------------------------------------------------------------
# 3. El servidor que espera a Asterisk
# ----------------------------------------------------------------------------
async def manejar(asterisk):
    try:
        await atender_llamada(asterisk)
    except websockets.ConnectionClosed:
        log("conexion cerrada")
    except Exception as error:                      # una llamada rota no debe tumbar el servidor
        log("error en la llamada:", repr(error))


async def main():
    if not API_KEY:
        sys.exit("Falta DEEPGRAM_API_KEY (export DEEPGRAM_API_KEY=...)")
    # subprotocols=["media"]: es lo que anuncia websocket_client.conf con "protocols = media".
    # Si no se ofrece, Asterisk recibe un HTTP 400 y la llamada ni empieza.
    async with websockets.serve(manejar, HOST, PORT, subprotocols=["media"]):
        log(f"escuchando en ws://{HOST}:{PORT}  (modelo {MODELO_OIDO}, voz {VOZ})")
        await asyncio.Future()                      # para siempre


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
