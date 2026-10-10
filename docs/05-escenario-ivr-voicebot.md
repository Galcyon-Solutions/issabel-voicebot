# Escenario completo: IVR, destino personalizado y voicebot

Hasta aquí los agentes de voz se marcaban directamente (7500 y 7501). Una central real los pone **detrás de un menú**: la llamada entra por una ruta, pasa por un IVR y, según la tecla, llega al agente. Este documento arma ese camino con las piezas de IssabelPBX, sin escribir una línea de dialplan.

```
 llamada ─► Misc Application 7800 ─► IVR "Demo Voicebot" ─┬─ tecla 1 ─► Custom Destination ─► 7500 voicebot galcymedia
 (o Inbound Route de tu troncal)                       └─ tecla 2 ─► Custom Destination ─► 7501 agente puro
```

> Requisitos: los dos agentes instalados (documentos 02 y 03) y Asterisk 20.18.

## 1. Las tres piezas, por la web

Entra a **PBX > PBX Configuration** (la interfaz de IssabelPBX).

### 1.1 Custom Destinations (menú *Admin > Custom Destinations*)

Un **destino personalizado** es un "puente": convierte un contexto de tu dialplan en algo que los menús de IssabelPBX pueden elegir como destino.

| Campo | Valor |
|---|---|
| Custom Destination | `from-internal-custom,7500,1` |
| Description | `Voicebot galcymedia` |

Es el formato `contexto,extensión,prioridad`. La extensión 7500 vive en `extensions_galcymedia.conf`, que se incluye en el contexto `from-internal-custom` (el de usuario). Repite con `from-internal-custom,7501,1` y la descripción `Agente de voz puro`. Pulsa **Submit** y luego el botón rojo **Apply Config**.

### 1.2 IVR (menú *Applications > IVR*)

| Campo | Valor |
|---|---|
| IVR Name | `Demo Voicebot` (un nombre que **no** exista ya en tu central) |
| IVR Description | `Menu de bienvenida` |
| Announcement | tu grabación de bienvenida (ver 1.4); para probar puede ir en `None` |
| Timeout | 10 segundos |
| Entradas (*IVR Entries*) | `1` ➜ *Custom Destinations*: `Voicebot galcymedia`; `2` ➜ *Custom Destinations*: `Agente de voz puro` |

Deja *Invalid* y *Timeout* en **Hangup** (o en una persona, si quieres que quien no elige hable con alguien). **Submit** y **Apply Config**.

### 1.3 Cómo entra la llamada

- **De la calle (lo real):** en *Connectivity > Inbound Routes*, crea una ruta con tu DID y como destino *IVR > Demo Voicebot*.
- **Para probar sin troncal:** *Applications > Misc Applications*: Description `Menu de bienvenida`, Feature Code `7800`, Destination *IVR > Demo Voicebot*. Ahora marcar 7800 desde cualquier extensión entra al menú.

### 1.4 La grabación de bienvenida

En *Applications > System Recordings* puedes subir un archivo o grabarlo marcando un código desde tu teléfono. Un texto corto y claro, por ejemplo: *"Bienvenido. Para hablar con el asistente con inteligencia artificial, marque uno. Para el asistente en versión simple, marque dos."* El IVR funciona sin grabación (espera la tecla en silencio), pero es una mala experiencia: grábala.

## 2. Lo mismo con un script (para repetirlo rápido)

El script usa **las mismas funciones de IssabelPBX que usa la web** (no escribe archivos a mano), respalda la base antes y aplica con `retrieve_conf`:

```bash
bash escenario/01_crear_escenario.sh                       # menú 7800, galcymedia 7500, puro 7501
bash escenario/01_crear_escenario.sh --menu 7800 --galcymedia 7500 --puro 7501
bash escenario/98_quitar_escenario.sh                      # reversa: quita la Misc Application, el IVR y los destinos
```

Es idempotente: usa su **propio** IVR "Demo Voicebot" (lo reemplaza si ya existe) y **nunca toca otro IVR** de tu central; los destinos que ya existen se saltan. Si el número del menú ya está en uso (una cola, una extensión), se detiene antes de crear nada. Prueba lo que **no** hay que olvidar: el script crea el IVR **sin grabación**; añádela por la web (sección 1.4).

> Elige un número de menú que no choque con una cola o una extensión. En el laboratorio la 7000 ya era una cola y el menú nunca se ejecutaba: el `dialplan show` lo delató. Comprueba siempre con `asterisk -rx 'dialplan show 7800@from-internal'`.

## 3. Probar

Con un teléfono: marca **7800**, espera, pulsa **1** y habla con el asistente de galcymedia. Con **2**, el puro.

Sin teléfono, con SIPp. Las teclas viajan como DTMF por SIP INFO, así que la extensión desde la que llamas debe tener el modo de DTMF en **info** (en la extensión de IssabelPBX, campo *dtmfmode*); con el modo por defecto la tecla va dentro del audio y SIPp no la manda:

```bash
sipp IP:5060 -sf sipp/llamar_ivr.xml -s 7800 -key user 7101 -key tecla 1 -au 7101 -ap CLAVE -d 25000 -m 1
```

Lo que debes ver en el registro del agente de galcymedia (`journalctl -u galcymedia-agent -f`):

```
Call started: channel=WebSocket/voicebot/... format=alaw frame=160B provider=deepgram
[assistant] Hola, gracias por llamar a la clinica. En que te puedo ayudar?
Call hung up normally (code 1000)
```

Y en Asterisk (`asterisk -rvvv`) el recorrido: `app-miscapps` ➜ `ivr-N` ➜ `WaitExten` ➜ `from-internal-custom,7500` ➜ `Gosub(voicebot...)` ➜ `Dial(WebSocket/voicebot...)`.

## 4. Siguientes pasos (ideas)

- **Guardar los datos de la llamada.** El agente ya recibe la transcripción (`ConversationText`); guardarla en un archivo, una base de datos o una API es añadir unas líneas donde hoy solo se imprime.
- **Horarios.** Pon un *Time Condition* delante del IVR: fuera de horario, directo al voicebot.
- **Transferir a una persona** desde el voicebot de galcymedia (documento 03, sección 6).

## 5. Si algo falla

| Síntoma | Dónde mirar |
|---|---|
| Marcas 7800 y entra a otra cosa (una cola, una extensión) | El número choca. `asterisk -rx 'dialplan show 7800@from-internal'` y elige otro |
| El IVR contesta pero la tecla 1 no hace nada | La entrada no tiene destino, o falta **Apply Config**. Revisa `ivr_entries` en la web y recarga |
| Pulsas 1 y se corta | El agente no está arrancado: `systemctl status galcymedia-agent` y `ss -ltn \| grep 9000` |
| "Custom Destination ... DUPLICATE" al crear | Ya existe (por la web o por el script): normal, el script lo salta |
