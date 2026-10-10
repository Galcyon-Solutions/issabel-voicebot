# Guía: de un Issabel actualizado a un voicebot

Este es el orden de trabajo en un servidor Issabel. Cada paso apunta al documento que lo explica y deja algo que se puede comprobar.

| # | Qué se hace | Documento | Se comprueba |
|---|---|---|---|
| 1 | Dominio y certificado HTTPS (Let's Encrypt) | `issabel-instalacion` / `02-dominio-y-ssl.md` | Candado verde en `https://pbx.tu-dominio.com/` |
| 2 | Actualizar Asterisk a 20.18 con `chan_websocket` | [01](01-actualizar-asterisk.md) | `core show version` dice 20.18.0 y existe el canal `WebSocket` |
| 3 | Actualizar el sistema y el Call Center | `issabel-instalacion` / `03` y `04` | Call Center 5.1.13 y `issabeldialer` activo |
| 4 | **Agente de voz puro**: un archivo de Python | [02](02-agente-puro.md) | Marcar 7501: el bot saluda |
| 5 | **Agente con galcymedia** | [03](03-agente-galcymedia.md) | Marcar 7500: el bot saluda; se puede interrumpir y pedir una persona |
| 6 | Por qué Deepgram y qué es Flux | [04](04-por-que-deepgram-y-flux.md) | Cambiar `DEEPGRAM_MODEL` a `flux-general-multi` y repetir la llamada |
| 7 | **Escenario completo**: llamada, IVR, destino personalizado, voicebot | [05](05-escenario-ivr-voicebot.md) | Marcar 7800, pulsar 1 y hablar con el bot |
| 8 | (Plus) Webphone: llamar desde el navegador | repositorio `issabel-webphone-lite` | Llamada de prueba al `*43` y al 7500 |

## La idea de los pasos 4 y 5

Hay **muchas formas** de poner una IA al teléfono. Esta guía hace la misma tarea dos veces para que la diferencia se vea y no se cuente:

- **Puro (paso 4):** unas 200 líneas, solo `websockets`. Se entiende cada mensaje que viaja entre Asterisk y Deepgram. Funciona, pero deja fuera cosas que una llamada real necesita (silencios, transferir, colgar bien).
- **galcymedia (paso 5):** el mismo transporte ya resuelto y probado, con control de flujo, interrupciones, transferencia a una persona, herramientas del modelo y registros útiles.

Después se mira el modelo (paso 6) y se arma el camino completo de una central real (paso 7).

## Si el servidor es compartido: la clave se queda en tu PC

En un servidor al que otras personas entran por SSH, **no dejes tu clave de Deepgram en el `.env` del servidor**. Corre el agente en tu PC y conéctalo con un túnel SSH inverso (documento [06](06-probar-el-bot-desde-tu-pc.md)): Asterisk no necesita ningún cambio.

## Antes de empezar

- Snapshot del VPS (lo único que te salva de verdad si algo sale mal).
- Una clave de Deepgram propia (nunca en un chat ni en un repositorio).
- Una extensión de prueba con su clave para SIPp o un softphone (las que ya tengas en tu Issabel).
- Cero llamadas activas durante las actualizaciones (los scripts se niegan si las hay).

## Y si algo falla

Se diagnostica, no se rodea. Cada documento tiene su tabla "Si algo falla" y cada script deja su respaldo y dice cómo volver atrás. Las herramientas son siempre las mismas:

```bash
asterisk -rvvv                               # lo que hace Asterisk, en vivo
journalctl -u agente-puro -f                 # el agente puro
journalctl -u galcymedia-agent -f            # el agente con galcymedia
asterisk -rx 'dialplan show 7800@from-internal'   # ¿a dónde lleva ese número?
```
