# Probar el bot desde tu PC, sin dejar tu clave en el servidor

Los agentes de los documentos 02 y 03 corren **en el servidor Issabel** y leen tu clave de Deepgram de un archivo `.env` ahí. En un servidor compartido (como el de un taller, donde varias personas tienen acceso por SSH) eso significa que **quien entre al servidor puede leer tu clave**. Hay una forma limpia de evitarlo: dejar el agente **en tu PC** y conectarlo al Asterisk del servidor con un **túnel SSH inverso**. La clave no sale de tu máquina.

## 1. Por qué se puede

En esta arquitectura **Asterisk es el cliente**, no el servidor:

- `Dial(WebSocket/voicebot/...)` hace que **Asterisk abra** la conexión WebSocket hacia `ws://127.0.0.1:9000/media` (y el agente puro, hacia el 9001).
- galcymedia además tiene un FastAGI en el 4573 al que **Asterisk también se conecta** (`AGI(agi://127.0.0.1:4573/...)`).

Asterisk solo necesita que, **en el servidor**, haya algo escuchando en `127.0.0.1:9000`, `9001` y `4573`. No le importa si ese algo es un proceso local o un túnel que lleva esos puertos hasta tu PC. Por eso **no se cambia nada en Asterisk**: ni el dialplan, ni `websocket_client.conf`.

```
 servidor Issabel                                   tu PC
 +--------------------------------+   túnel SSH   +----------------------------+
 | Asterisk --> 127.0.0.1:9000 ===|===============|==> agente (con tu .env) ---> Deepgram
 |              127.0.0.1:9001    |  (inverso)    |
 |              127.0.0.1:4573    |               |
 +--------------------------------+               +----------------------------+
```

## 2. Pasos

### 2.1 En el servidor: apaga los agentes

Los puertos tienen que estar libres, o el túnel no se abre:

```bash
systemctl stop galcymedia-agent agente-puro
systemctl disable galcymedia-agent agente-puro         # para que no arranquen solos
ss -ltn | grep -E ':(9000|9001|4573) '                 # no debe salir nada
```

### 2.2 En tu PC: el agente con tu clave

Necesitas Python 3.10 o superior. Con el agente **puro**:

```powershell
pip install websockets
$env:DEEPGRAM_API_KEY = "tu_clave"          # en Linux o Mac: export DEEPGRAM_API_KEY=...
python -u ejemplos\puro\agente_puro.py      # escucha en 127.0.0.1:9001
```

Con **galcymedia** (el ejemplo `02-agent` del repositorio `galcymedia-examples`, que lee su propio `.env`):

```powershell
pip install "galcymedia[deepgram]"
cd examples\02-agent
python -u main.py                           # escucha en 127.0.0.1:9000 y 4573
```

### 2.3 El túnel

Desde tu PC (Windows 10 y 11 traen el cliente `ssh`). **Un solo comando lleva los tres puertos**:

```bash
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=15 \
    -R 9000:127.0.0.1:9000 -R 9001:127.0.0.1:9001 -R 4573:127.0.0.1:4573 \
    usuario@tu-servidor
```

- `-R 9000:127.0.0.1:9000` significa: "en el **servidor**, lo que llegue a `127.0.0.1:9000` mándalo a `127.0.0.1:9000` de **mi PC**".
- `-N`: no abre una terminal, solo el túnel. `ExitOnForwardFailure`: si un puerto del servidor está ocupado, falla en voz alta en vez de quedarse a medias. `ServerAliveInterval`: detecta un túnel muerto.
- Si solo usas uno de los agentes, deja solo su `-R`.

Mientras ese comando esté corriendo, el túnel está arriba. Comprueba en el servidor: `ss -ltn | grep 9000` debe mostrar `127.0.0.1:9000`.

### 2.4 Marcar

Marca el 7500, el 7501 o el 7800 como siempre. En la ventana de tu PC verás el registro del agente (`Asterisk connected from ('127.0.0.1', ...)`, `Call started ...`).

## 3. Verificado

Probado con el laboratorio: el ejemplo `01-echo` de galcymedia corriendo **en Windows**, un túnel `ssh -R 9000:127.0.0.1:9000` hacia el laboratorio, y una llamada SIPp al 7500. Resultado en el registro de la PC: `Asterisk connected`, `Call started: ... format=alaw frame=160B` y `Call hung up normally (code 1000)`. Es decir, el Asterisk del servidor atendió la llamada con un agente que no está en el servidor y sin cambiar una línea de configuración.

**No se midió** la calidad del audio con una persona hablando, ni con Deepgram a través del túnel.

## 4. Lo que hay que saber

| Tema | Detalle |
|---|---|
| **Latencia** | El audio de cada turno va servidor, PC, Deepgram y vuelta. Se suma el tiempo de ida y vuelta entre tu PC y el servidor (`ping tu-servidor`): con un servidor en otro continente se nota en la fluidez de la conversación. Para una demostración basta; para producción, el agente va en el servidor |
| **Si el túnel cae** | La llamada en curso se corta y el bot calla. Con `ServerAliveInterval` lo detectas en segundos; para volver a levantarlo solo hay que repetir el comando (o usar `autossh`) |
| **Quién más puede usar tu agente** | El túnel abre `127.0.0.1:9000` **en el servidor**: cualquier usuario local de ese servidor puede conectarse y hablar con tu agente (gastando tu crédito de Deepgram), aunque **no puede leer tu clave**. Es mucho menos que dejar el `.env` ahí, pero no es aislamiento total |
| **Crédito de Deepgram** | En una demostración o un taller compartido conviene una clave **propia para ese evento**, con límite de uso y fecha de vencimiento (Deepgram permite crear claves con caducidad; revisa las opciones en tu consola) y borrarla al terminar |
| **Tu PC dormida** | Si se suspende, el túnel y el agente se caen. Desactiva la suspensión durante la demostración |
| **Para quien lo monta por su cuenta** | En tu propio VPS usa **tu propia clave** y el agente en su servidor (documentos 02 y 03). El túnel es una comodidad para un servidor compartido, no el camino normal |

## 5. Volver a poner el agente en el servidor

Cuando termines: detén el túnel (Ctrl+C), pon la clave en `/opt/galcymedia-agent/app/.env` y `/opt/agente-puro/.env`, y `systemctl enable --now galcymedia-agent agente-puro`.
