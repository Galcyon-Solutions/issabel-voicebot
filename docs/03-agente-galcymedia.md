# Agente de voz con galcymedia sobre Issabel

Es el mismo trabajo que el [agente puro](02-agente-puro.md), pero con una librería que ya resuelve el transporte y los casos raros. Al terminar tienes una extensión (la **7500**) que, al marcarla, te atiende un agente de voz con IA: escucha, entiende, contesta con voz natural y, si se lo pides, te pasa con una persona. Funciona sobre tu Issabel, con Asterisk 20.18 y el canal `chan_websocket`.

## 1. La idea en un minuto

Hasta hace poco, meter la voz de una llamada en un programa de IA obligaba a usar AudioSocket, ARI o servidores RTP. Desde Asterisk 20.16 existe `chan_websocket` (Media over WebSocket): el audio de la llamada viaja por **un WebSocket**, sin RTP, sin puertos UDP y sin lío de NAT hacia tu programa.

```
 Teléfono / webphone / SIPp
          | SIP + RTP
          v
 +-------------------+   WebSocket (audio)   +------------------+   WebSocket   +----------+
 |  Asterisk 20.18   | <-------------------> |    galcymedia    | <-----------> | Deepgram |
 |  (Issabel)        |   ws://127.0.0.1:9000 |  agente Python   |               |  Voice   |
 |  Dial(WebSocket/) |                       |  (02-agent)      |               |  Agent   |
 +-------------------+                       +------------------+               +----------+
          ^   AGI (127.0.0.1:4573): "¿qué hizo el bot al terminar?" -> transferir a una persona
```

Quién hace qué:

| Pieza | Responsabilidad |
|---|---|
| **Asterisk** | La telefonía: SIP, códecs, dialplan y el canal `chan_websocket` |
| **galcymedia** (librería Python, Apache-2.0) | El protocolo del canal y el transporte hacia el proveedor: control de flujo, alineación de tramas, interrupciones (barge-in) y colgado |
| **02-agent** (ejemplo) | Lo que decide este agente: su prompt, sus herramientas, cuánto silencio tolera. Es una asistente de clínica que consulta horarios y agenda citas |
| **Deepgram Voice Agent** | Reconocimiento de voz, el modelo de lenguaje y la síntesis de voz |

## 2. Qué necesitas

| Requisito | Cómo verificarlo |
|---|---|
| Issabel 5 con **Asterisk 20.16 o superior** | `asterisk -rx 'core show version'` y `asterisk -rx 'core show channeltype WebSocket'` (debe existir). Si tienes 18 o 20.12, haz primero el [manual de actualización de Asterisk](manual-actualizar-asterisk.md) |
| Una **clave de Deepgram** (`DEEPGRAM_API_KEY`) | La creas en la consola de Deepgram. Es **tuya**: no se comparte ni se sube a un repositorio |
| Un destino humano en Issabel | El número interno al que pasa el bot cuando piden una persona: una **cola** (por ejemplo la 7000) o una extensión. El número del bot (7500) lo crea el instalador en el dialplan |
| Salida a internet desde el servidor | PyPI (instalar la librería), GitHub (descargar el ejemplo) y Deepgram (`wss://agent.deepgram.com`) |

## 3. Instalar

Desde la carpeta de este repositorio, como root:

```bash
bash voicebot/01_instalar_voicebot.sh --ext-bot 7500 --destino-humano 7000
```

Qué hace, en orden (puedes leerlo en el script):

1. Comprueba que Asterisk tenga `chan_websocket` y que exista el destino humano (`dialplan show <destino>@from-internal`). Hace un **respaldo** de `extensions_custom.conf` y `websocket_client.conf`.
2. Instala Python 3.12 y crea un entorno virtual en `/opt/galcymedia-agent/venv` con `galcymedia[deepgram]` desde PyPI.
3. Descarga el ejemplo `02-agent` de `Galcyon-Solutions/galcymedia-examples` en una versión **fijada por hash** (la que se probó en esta guía) y copia sus 6 archivos a `/opt/galcymedia-agent/app`.
4. Crea el servicio `galcymedia-agent` (systemd) y el `.env` con la clave **vacía**.
5. Agrega la sección `[voicebot]` a `websocket_client.conf` y el dialplan en `extensions_galcymedia.conf`, incluido desde `extensions_custom.conf` (el archivo **de usuario**: nunca se edita `extensions_additional.conf`, que IssabelPBX regenera).
6. Recarga solo `res_websocket_client` y el dialplan (nada de reiniciar Asterisk).

Es **idempotente**: si lo repites, no duplica nada y no pisa tu `.env`.

## 4. Poner tu clave y arrancar

```bash
nano /opt/galcymedia-agent/app/.env        # DEEPGRAM_API_KEY=tu_clave
systemctl enable --now galcymedia-agent
journalctl -u galcymedia-agent -f          # debe mostrar que escucha en el puerto 9000
```

Si arranca sin clave, el agente **se niega a iniciar** y lo dice en el registro: es a propósito (mejor un error al arrancar que una llamada muda).

## 5. Probar

### 5.1 Con SIPp (sin teléfono)

Ver [`sipp/README.md`](../sipp/README.md). En una línea:

```bash
sipp IP_DEL_SERVIDOR:5060 -sf sipp/llamar_bot.xml -s 7500 -key user 7101 -au 7101 -ap CLAVE -d 25000 -m 1
```

### 5.2 Con voz real

Registra un softphone (Zoiper, Linphone, MicroSIP) o usa el **webphone** de Issabel (repositorio `issabel-webphone-lite`) con una extensión, y marca **7500**. Habla en español con naturalidad: *"Hola, quiero una cita de medicina general para mañana"*. Prueba también:

> **Observado:** al llamar al bot desde el **webphone del navegador** el audio hacia el bot se oyó peor que desde un softphone SIP normal (la misma extensión, la misma llamada). No se investigó la causa; el camino del webphone añade el procesamiento del navegador (cancelación de eco, control de ganancia) y una conversión de códec en Asterisk. Si tu primera prueba con voz suena mal, repítela con un softphone SIP antes de culpar al bot.

- **Interrumpir al bot** mientras habla (barge-in): debe callarse y escucharte.
- Pedir **hablar con una persona**: el bot lo anota, se despide, y el dialplan hace `Goto(from-internal,<destino>,1)`: la llamada entra a la cola o a la extensión que indicaste, con todas sus reglas (timbrado, tiempo de espera, música). Con una cola como la 7000, el bot sale de la llamada y la cola le asigna un agente.
- Apretar **0**: también transfiere (el ejemplo activa `forward_dtmf`).

La grabación de cada llamada queda en `/var/spool/asterisk/monitor/` (`<id>-caller.wav` y `<id>-bot.wav`, cada lado por separado).

## 6. Cómo funciona por dentro

El dialplan completo (`/etc/asterisk/extensions_galcymedia.conf`):

```asterisk
[from-internal-custom]
exten => 7500,1,Gosub(voicebot,s,1(deepgram))
 same => n,GotoIf($["${BOT_ACTION}" = "transfer"]?transferir,s,1)
 same => n,Hangup()

[voicebot]
exten => s,1,Answer()
 same => n,Set(_AI_PROVIDER=${ARG1})          ; qué adaptador usa el agente (deepgram)
 same => n,Set(_AI_LANGUAGE=es)
 same => n,Set(_CALL_ID=${UNIQUEID})          ; identifica la llamada ante el agente y el AGI
 same => n,Set(CHANNEL(hangup_handler_push)=galcymedia,s,1)
 same => n,MixMonitor(,r(${UNIQUEID}-caller.wav)t(${UNIQUEID}-bot.wav)i(RECID))
 same => n,Dial(WebSocket/voicebot/c(alaw)f(json),3600,g)   ; el audio de la llamada va al agente
 same => n,StopMixMonitor(${RECID})
 same => n,AGI(agi://127.0.0.1:4573/after-dial,${CALL_ID}) ; ¿qué decidió el bot?
 same => n,Return()
```

Tres cosas que conviene entender:

1. **`Dial(WebSocket/voicebot/c(alaw)f(json),...)`** abre el canal contra la conexión llamada `voicebot` de `websocket_client.conf` (`ws://127.0.0.1:9000/media`, modo `per_call_config`). `c(alaw)` es el códec y `f(json)` el formato de los mensajes de control. Las variables `_AI_PROVIDER` y `_CALL_ID` llevan el guion bajo inicial para que las herede el canal nuevo.
2. **El canal WebSocket no transfiere** (`core show channeltype WebSocket` dice `Transfer: no`, por diseño: es un canal de medios, no de señalización). Por eso el bot **registra su decisión** (`BOT_ACTION=transfer`) y es el **dialplan** quien la lee, por AGI, después del `Dial`, y llama a la persona. Es el patrón de todo el ejemplo.
3. **El bot cierra con `finish()` y no con `hangup()`**: así se escucha completa la despedida antes de colgar.

## 7. Ajustes sin tocar Python

Todo en `/opt/galcymedia-agent/app/.env` (después `systemctl restart galcymedia-agent`):

| Variable | Qué decide |
|---|---|
| `DEEPGRAM_API_KEY` | Tu clave. Obligatoria |
| `AI_LANGUAGE` | Idioma del agente (`es`) |
| `DEEPGRAM_MODEL`, `DEEPGRAM_VOICE` | Modelo y voz |
| `SLOW_REPLY_AFTER_S` | Cuánto esperar antes de rellenar un silencio del bot con "Dame un segundo". `0` lo apaga |
| `NO_REPLY_WAITS_S` | Cuánto espera a una persona que no contesta (`12,8,6`) antes de dar la llamada por perdida |
| `LOG_LEVEL` | `INFO` o `DEBUG` |

## 8. Compatibilidad: qué se sabe y qué se comprueba con una persona

`galcymedia` 0.1.1 declara como mínimo **Asterisk 23.4.0**, porque en versiones anteriores a 22.6.0 había un fallo en `chan_websocket`: tras un `FLUSH_MEDIA` (lo que se manda al interrumpir al bot) el contador de la cola no se reiniciaba, Asterisk creía la cola llena, rechazaba el audio nuevo y nunca mandaba `MEDIA_XON` (issue #1304, arreglado en el PR #1303). Lo que se verificó para esta guía:

- `chan_websocket.c` de **20.16 y 20.17** es **idéntico** al de 22.6.0, que ya trae el arreglo.
- **20.18.0**, la que instala este repositorio, **reorganizó** ese archivo. La conexión, el saludo del bot y el colgado se verificaron con SIPp contra el bot real (sección 5.1). La **interrupción por voz (barge-in)** se comprueba con una persona hablando: es la prueba que falta.
- Cómo se comprueba, con datos y no a ojo: mientras el bot habla, interrúmpelo y mira el registro del agente. Debe verse `UserStartedSpeaking`, luego el audio nuevo del bot y `QUEUE_DRAINED` al terminar. Si el bot se queda mudo, el síntoma típico es que **no llega `MEDIA_XON`**: se confirma con `LOG_LEVEL=DEBUG` y con el comando `GET_STATUS` (devuelve la profundidad real de la cola), y se corrige en el punto exacto que describe `docs/protocol.md` de galcymedia. El código de `chan_websocket.c` es abierto y pequeño: no es una caja negra.
- Dato aparte: la 23.4.1 tiene un fallo con `inhibit escalations` de TLS (afecta funciones peligrosas del dialplan tras un `Dial` saliente). El parche de Issabel ya lo desactiva en este Asterisk.

## 9. Si algo falla

| Síntoma | Dónde mirar |
|---|---|
| Marcas 7500 y se corta enseguida | `systemctl status galcymedia-agent` y `ss -ltn \| grep 9000`: el agente tiene que estar escuchando |
| El agente no arranca | `journalctl -u galcymedia-agent -n 50`. Lo más común: clave vacía, o el puerto 9000 ocupado (`MEDIA_PORT` en el `.env`) |
| No se oye nada pero hay llamada | Prueba el ejemplo `01-echo` del repositorio de ejemplos (devuelve tu audio sin proveedor): si el eco no suena, es la telefonía |
| Conversa pero no transfiere | ¿Está el `AGI(...)` en el dialplan? ¿Existe el destino humano? `asterisk -rx 'dialplan show 7000@from-internal'` (cámbialo por el tuyo) |
| El bot se despide pero no cuelga | Es el modelo, no el canal. Ver la cabecera de `prompt.py` del ejemplo |
| `Transfer: no` en el canal | Es normal y esperado (sección 6, punto 2) |

## 10. Desinstalar

```bash
bash voicebot/98_quitar_voicebot.sh
```

Quita servicio, aplicación, entorno virtual, dialplan y la sección `[voicebot]`. No toca Asterisk 20.18 (para eso, `asterisk/99_revertir.sh`).
