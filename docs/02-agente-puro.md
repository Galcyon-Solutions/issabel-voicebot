# Agente de voz puro: Asterisk y Deepgram en un solo archivo de Python

El ejemplo más simple posible de un agente de voz sobre Issabel: **un archivo (`ejemplos/puro/agente_puro.py`, unas 200 líneas, de las cuales 60 son comentarios), una dependencia (`websockets`) y ninguna librería de telefonía**. Sirve para ver con tus propios ojos qué pasa en una llamada. En el siguiente documento haces lo mismo con galcymedia y comparas.

> Requisito: Asterisk **20.16 o superior** con `chan_websocket` (documento 01) y una clave de Deepgram.

## 1. Qué va a pasar

```
 persona ──SIP/RTP──► Asterisk ──WebSocket (audio binario + eventos JSON)──► agente_puro.py ──WebSocket──► Deepgram Voice Agent
                      Dial(WebSocket/voicepuro/c(alaw)f(json))   ws://127.0.0.1:9001/media             wss://agent.deepgram.com
```

Asterisk **marca** hacia tu programa (como si tu programa fuera un teléfono). Tu programa es el servidor WebSocket, y a su vez abre **otro** WebSocket hacia Deepgram. En medio solo hay que copiar bytes de un lado a otro, con cuatro cuidados que el archivo explica uno por uno.

## 2. Instalar

```bash
bash ejemplos/puro/01_instalar_puro.sh --ext 7501
nano /opt/agente-puro/.env                 # DEEPGRAM_API_KEY=tu_clave
systemctl enable --now agente-puro
journalctl -u agente-puro -f               # escuchando en ws://127.0.0.1:9001
```

El instalador crea el entorno virtual con `websockets`, el servicio `agente-puro`, la conexión `[voicepuro]` en `websocket_client.conf` y la extensión **7501** en `extensions_custom.conf` (el archivo de usuario; los `*_additional.conf` los regenera IssabelPBX). Reversa: `bash ejemplos/puro/98_quitar_puro.sh`.

## 3. Probar

Marca **7501** desde un softphone o el webphone, o con SIPp (ver `sipp/README.md`). En el registro:

```
12:39:57 llamada: formato=alaw trama=160B
12:39:58 [assistant] Hola, gracias por llamar. En que te puedo ayudar?
```

## 4. El archivo, por dentro

Léelo en este orden; está dividido en secciones numeradas.

### 4.1 La conexión que Asterisk abre

El dialplan hace `Dial(WebSocket/voicepuro/c(alaw)f(json))`. `voicepuro` es una conexión definida en `websocket_client.conf`:

```ini
[voicepuro]
type = websocket_client
uri = ws://127.0.0.1:9001/media
connection_type = per_call_config
protocols = media
```

`c(alaw)` es el códec del audio y `f(json)` el formato de los mensajes de control. **El servidor tiene que ofrecer el subprotocolo `media`** (`websockets.serve(..., subprotocols=["media"])`): si no, Asterisk recibe un HTTP 400 y la llamada ni empieza. Es un error clásico.

### 4.2 `MEDIA_START`: el primer mensaje

Lo primero que llega es un mensaje de texto JSON: `{"event": "MEDIA_START", "format": "alaw", "optimal_frame_size": 160, ...}`. Dice el códec y el tamaño de trama (160 bytes = 20 ms de audio a 8 kHz). Todo el audio viaja en mensajes **binarios**; todo el control, en mensajes **de texto**. Nunca se mezclan.

### 4.3 `ANSWER`

El agente responde `{"command": "ANSWER"}`. Sin esto la pata WebSocket no contesta y `Dial` nunca une las dos patas: la persona escucharía silencio.

### 4.4 La configuración de Deepgram (`Settings`)

Es el primer mensaje que Deepgram espera. Define el audio (el mismo códec y 8 kHz que entrega Asterisk, así **no hay que convertir nada**), el oído (`listen`), el cerebro (`think`, con tu `prompt`), la voz (`speak`) y el saludo (`greeting`).

### 4.5 Los dos sentidos del audio

```python
persona -> Deepgram :  deepgram.send(trama_de_asterisk)                      # tal cual
Deepgram -> persona :  asterisk.send(trama_completa_de_160_bytes)            # alineada
```

### 4.6 Los cuatro cuidados (lo que separa un juguete de algo que funciona)

| Cuidado | Qué pasa si no lo haces |
|---|---|
| **Tramas completas.** Asterisk acepta el audio en múltiplos exactos de 160 bytes y **tira el resto** de cada mensaje | Voz entrecortada, sin ningún error en ningún registro. Es de lo más difícil de diagnosticar |
| **Interrupciones (barge-in).** Cuando Deepgram dice `UserStartedSpeaking`, se manda `FLUSH_MEDIA` a Asterisk y se **descarta** la voz del bot que aún venga en camino | El bot sigue hablando encima de la persona |
| **Control de flujo.** Asterisk avisa `MEDIA_XOFF` cuando su cola pasa de 900 tramas; hay que parar hasta `MEDIA_XON` | Se pierde audio |
| **Una llamada rota no tumba el servidor.** Cada llamada va en su propio `try` | Un error en una llamada corta todas |

## 5. Lo que NO hace (a propósito) y por qué existe galcymedia

El archivo es corto porque deja fuera cosas que una llamada real termina necesitando:

| Falta en el puro | Qué se nota |
|---|---|
| **Relleno de silencio.** Deepgram solo avanza si recibe audio; si Asterisk no manda tramas (por ejemplo una llamada de prueba con SIPp, que no envía audio) a los ~13 s responde `We did not receive audio within our timeout` y la llamada se cae | Con una persona hablando no pasa; con SIPp sí |
| **Transferir a una persona.** El canal WebSocket **no transfiere** (`Transfer: no`); hay que registrar la decisión del bot y ejecutarla en el dialplan por AGI al terminar | El puro solo conversa |
| **Herramientas del modelo** (agendar citas, consultar datos) | No hay `functions` en `Settings` |
| **Colgar bien.** Despedirse y colgar sin cortar la última frase | Se corta la despedida |
| **Silencios largos**, recordatorios, tiempo máximo sin respuesta | Una llamada olvidada cuesta dinero |
| **Pruebas automáticas** y registro útil | Depurar a ciegas |

Eso es exactamente lo que resuelve **galcymedia** (documento 03): el mismo trabajo de transporte, ya hecho, probado y con los casos raros cubiertos.

## 6. Cambiar el modelo de oído (Flux)

Sin tocar código, con una variable de entorno:

```bash
# /opt/agente-puro/.env
DEEPGRAM_MODEL=flux-general-multi
```

`nova-3` y `flux-general-multi` usan dos esquemas distintos (`version: v1` y `v2`) y el archivo ya los distingue en `configuracion()`. Verificado: Deepgram acepta `flux-general-multi` con pista de idioma español y saluda igual. Qué es Flux y por qué importa: documento 04.

## 7. Ejercicios

1. Cambia `SALUDO` y `PROMPT`, reinicia el servicio y vuelve a llamar.
2. Quita el `FLUSH_MEDIA` y compara qué pasa al interrumpir al bot.
3. Manda la transcripción a un archivo (`ConversationText`): ya tienes la base para guardar datos de la llamada.
