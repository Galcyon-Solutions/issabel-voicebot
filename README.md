# issabel-voicebot

Pon **Asterisk 20.18 con `chan_websocket`** en tu Issabel 5 y conéctale un **voicebot con IA** (galcymedia + Deepgram). Scripts probados y manuales paso a paso. Sin Docker: todo corre directamente en tu servidor.

> Es parte de un conjunto de tres repositorios para aprender Issabel y voz con IA. Los otros: `issabel-instalacion` (instalar Issabel y Call Center) e `issabel-webphone-lite` (teléfono en el navegador).

## Qué consigues

```
Marcas 7500  ->  Asterisk 20.18 (Issabel)  --WebSocket-->  galcymedia (Python)  --WebSocket-->  Deepgram Voice Agent
                      ^                                                                              |
                      +---- si el bot decide "pasar a una persona", el dialplan lo pasa a una cola o extensión <-+
```

## Contenido

| Carpeta | Qué hay |
|---|---|
| [`docs/00-guia.md`](docs/00-guia.md) | El orden de trabajo, de punta a punta |
| [`docs/01-actualizar-asterisk.md`](docs/01-actualizar-asterisk.md) | Llegar a Asterisk 20.18 desde Issabel con Asterisk 18 o 20.12, construir el RPM y volver atrás |
| [`docs/02-agente-puro.md`](docs/02-agente-puro.md) | Agente de voz en **un solo archivo de Python**: se entiende cada mensaje entre Asterisk y Deepgram |
| [`docs/03-agente-galcymedia.md`](docs/03-agente-galcymedia.md) | El mismo agente con galcymedia: qué resuelve la librería |
| [`docs/04-por-que-deepgram-y-flux.md`](docs/04-por-que-deepgram-y-flux.md) | Por qué un agente integrado, por qué Deepgram y qué es Flux |
| [`docs/05-escenario-ivr-voicebot.md`](docs/05-escenario-ivr-voicebot.md) | Llamada, IVR, destino personalizado y voicebot, con IssabelPBX |
| [`docs/06-probar-el-bot-desde-tu-pc.md`](docs/06-probar-el-bot-desde-tu-pc.md) | Correr el agente **en tu PC** con un túnel SSH inverso, sin dejar tu clave en el servidor |
| `build/` | El `spec` de RPM (derivado del de Issabel) y los scripts para compilar |
| `dist/` | **Los 26 RPM ya construidos** (7,6 MB) con su `SHA256SUMS` (los `.rpm` van como archivos de Release, no en git; ver `dist/LEEME.md`) |
| `asterisk/` | `02_actualizar.sh` (20.12 a 20.18), `03_migrar_18_a_20.sh` (18 a 20.18) y sus reversas `99_*` |
| `ejemplos/puro/` | `agente_puro.py` y su instalador (`01_instalar_puro.sh`, `98_quitar_puro.sh`) |
| `voicebot/` | El agente con galcymedia: `01_instalar_voicebot.sh`, `98_quitar_voicebot.sh` |
| `escenario/` | `01_crear_escenario.sh`: crea con las funciones de IssabelPBX el IVR, los destinos y la Misc Application |
| [`sipp/`](sipp/README.md) | Probar con llamadas SIPp, sin softphone: escenarios (`llamar_bot.xml`, `llamar_ivr.xml`) y compilación de SIPp |

## Camino rápido

```bash
# 1. Asterisk 20.18 (elige UNO según tu punto de partida)
( cd dist && sha256sum -c SHA256SUMS )
bash asterisk/02_actualizar.sh dist --si          # si tienes Asterisk 20.12 (ISO 2026)
bash asterisk/03_migrar_18_a_20.sh dist --si      # si tienes Asterisk 18 (ISO 2024 o netinstall)

# 2. El agente puro (7501) y el de galcymedia (7500)
bash ejemplos/puro/01_instalar_puro.sh --ext 7501
bash voicebot/01_instalar_voicebot.sh --ext-bot 7500 --destino-humano 7000
nano /opt/agente-puro/.env                        # tu DEEPGRAM_API_KEY
nano /opt/galcymedia-agent/app/.env               # la misma clave
systemctl enable --now agente-puro galcymedia-agent

# 3. El escenario: marcar 7800, pulsar 1 o 2
bash escenario/01_crear_escenario.sh
```

## Qué se probó y qué no

Probado en Issabel desechables, en un laboratorio y en un **servidor real** (Rocky 8.8 con Asterisk 18.19, Call Center 5.1.1, 11 extensiones PJSIP, idioma `es_PE` y bloqueo GeoIP):

| Prueba | Resultado |
|---|---|
| Compilar los RPM con `build/` en un Rocky 8 con repositorios de Issabel | 26 RPM; el mismo conjunto que se había construido en el laboratorio |
| `02_actualizar.sh` 20.12 a 20.18 con Call Center instalado | OK: módulos iguales menos STIR/SHAKEN; `chan_websocket` carga; el marcador sigue activo |
| `03_migrar_18_a_20.sh` en el **servidor real** (Asterisk 18.19 a 20.18.0) y en un Issabel por netinstall, y su reversa | OK. En el servidor real apareció un fallo que ningún contenedor mostró: con idioma `es_PE` Asterisk 20 no crea los AOR de PJSIP (coma decimal). Corregido en los dos scripts y verificado (0 a 11 AOR) |
| Actualizar el sistema (662 paquetes pendientes, kernel nuevo) y reiniciar | OK; Asterisk 20.18 intacto, todos los servicios arrancan solos |
| Call Center 5.1.1 a 5.1.13 en el servidor real | OK, código de salida 0 |
| `ejemplos/puro/agente_puro.py` en Asterisk 20.18.0 con Deepgram | OK: el bot saluda; con `flux-general-multi` también. SIPp no envía audio y Deepgram corta a los ~13 s (explicado en `docs/02-agente-puro.md`) |
| Bot de galcymedia (02-agent) con Deepgram | OK: saluda, Asterisk reproduce el audio completo, el recordatorio por silencio funciona, cuelgue normal |
| Escenario `7800 -> IVR -> tecla 1 -> destino personalizado -> bot` (SIPp con tecla) | OK en el laboratorio; en el servidor real el escenario está creado y falta probarlo con las claves |

**No probado (lo comprueba una persona):**

- Una **persona hablando** con cada bot y la **interrupción por voz (barge-in)** en Asterisk 20.18.0 (SIPp no envía audio). `galcymedia` 0.1.1 declara como mínimo Asterisk 23.4.0; `chan_websocket.c` de 20.16 y 20.17 es idéntico al de 22.6.0, pero 20.18 lo reorganizó. Detalle en `docs/03-agente-galcymedia.md`, sección 8.
- El audio de una llamada real por un VPS con NAT.
- Compilar con una versión distinta de 20.18.0.

## De dónde sale cada cosa

- **Asterisk**: `asterisk-20.18.0.tar.gz` de `downloads.asterisk.org`; el script verifica el hash que publica Asterisk.
- **Parches de Issabel** (desactivar `inhibit escalations` de TLS, ping de WebSocket, `res_speech_vosk` con varios servidores, unidad de systemd): del SRPM público `asterisk18-18.12.0-1.el8.src.rpm` de `repo.issabel.org`. El SRPM del Asterisk 20 de Issabel no es público; el `spec` de este repositorio está derivado del de la versión 18 y adaptado.
- **Voicebot**: `galcymedia` (PyPI, Apache-2.0) y el ejemplo `02-agent` de `Galcyon-Solutions/galcymedia-examples`, fijado por hash de commit.

## Licencia

Apache-2.0 (ver `LICENSE`), salvo `build/asterisk20.spec`, que se deriva de un spec GPL de Issabel y conserva GPL-2.0-or-later (`build/LICENSE-GPL-2.0`). `galcymedia` y sus ejemplos tienen su propia licencia (Apache-2.0). Autor: Gian Diego Javes, Galcyon Solutions.
