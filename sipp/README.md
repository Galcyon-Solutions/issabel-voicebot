# Probar el voicebot con SIPp (sin softphone)

SIPp es un generador de llamadas SIP. Con él puedes marcar la extensión del voicebot desde la línea de comandos y ver en el registro del agente que la llamada llegó, que el canal WebSocket se abrió y que el proveedor (Deepgram) contestó. Sirve para **probar la telefonía y la conexión**; para **hablar de verdad** usa un softphone o el webphone, porque este escenario no envía audio.

## 1. Instalar SIPp (una vez)

SIPp no viene en los repositorios de Rocky ni de Issabel, se compila del código oficial (unos 2 minutos):

```bash
bash sipp/instalar_sipp.sh
sipp -v | head -2        # SIPp v3.7.9 ...
```

Puedes instalarlo en el mismo Issabel o en otra máquina que llegue al puerto 5060/UDP del servidor.

## 2. Una extensión desde la cual llamar

SIPp se registra como una extensión real. Crea una en Issabel (PBX > PBX Configuration > Extensions) o usa una que ya tengas, por ejemplo la **7101**, y apunta su clave. Tiene que existir con la tecnología que uses (PJSIP o chan_sip).

## 3. Llamar al voicebot

```bash
sipp IP_DEL_SERVIDOR:5060 -sf sipp/llamar_bot.xml \
     -s 7500 -key user 7101 -au 7101 -ap CLAVE_DE_LA_7101 \
     -d 25000 -m 1 -trace_err
```

| Parámetro | Qué es |
|---|---|
| `-s 7500` | La extensión que marcas (el voicebot) |
| `-key user 7101` | Desde qué extensión llamas; debe coincidir con `-au` |
| `-au` / `-ap` | Usuario y clave de esa extensión (autenticación SIP) |
| `-d 25000` | Duración de la llamada en milisegundos (25 s) |
| `-m 1` | Una sola llamada |

La clave no la dejes escrita en un script que subas a un repositorio.

## 4. Qué mirar

En otra terminal del servidor, mientras corre la llamada:

```bash
journalctl -u galcymedia-agent -f                       # lo que ve el agente
asterisk -rx 'core show channels'                       # deben verse el canal SIP y un canal WebSocket
asterisk -rx 'websocket client show'                    # el cliente [voicebot]
```

Resultados esperables (el primero es el que se verificó con Asterisk 20.18.0, con el ejemplo `01-echo`):

| Qué ves | Qué significa |
|---|---|
| SIPp termina con código 0 y en el registro del agente aparece `Asterisk connected from ('127.0.0.1', ...)`, luego `Call started: channel=WebSocket/voicebot/... format=alaw frame=160B` y al final `Call hung up normally (code 1000)` | La telefonía, el dialplan y el canal WebSocket funcionan. El agente recibió la llamada |
| Con el bot real, además: `Connecting to Deepgram`, luego `[assistant] Hola, gracias por llamar a la clinica...`, `AgentAudioDone` y `QUEUE_DRAINED` (Asterisk terminó de reproducir el saludo). Si nadie habla, a los 13 s el bot insiste (`nudge 1`: *"Disculpa, sigues ahi?"*). Al final `Provider session closed (0 frames sent)`: es normal, SIPp no envía audio | El proveedor y la clave están bien y el audio del bot llega a Asterisk |
| SIPp termina bien pero el agente no registra nada | `systemctl status galcymedia-agent`; ¿está arrancado? ¿escucha el puerto 9000 (`ss -ltn \| grep 9000`)? |
| `403 Forbidden` o `401` repetido | Usuario o clave de la extensión mal puestos |
| `404 Not Found` | La extensión 7500 no existe en el dialplan: `asterisk -rx 'dialplan show 7500@from-internal'` |

## 5. Si el bot no está listo: aislar con el eco

El repositorio de ejemplos de galcymedia trae `01-echo`, que devuelve tu propio audio sin proveedor. Si el eco funciona y el bot no, el problema es el proveedor (clave, modelo, cuota); si el eco tampoco funciona, el problema es la telefonía o `chan_websocket`.

## Por qué SIPp "marca" y no habla WebSocket

SIPp habla SIP normal, como un teléfono. Es el **dialplan** de Asterisk el que hace `Dial(WebSocket/voicebot/...)` hacia el agente. Por eso la prueba es representativa: es el mismo camino que seguirá un cliente real.
