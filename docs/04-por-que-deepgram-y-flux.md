# Por qué Deepgram, y qué es Flux

Un agente de voz hace tres trabajos en cada turno: **oír** (voz a texto), **pensar** (un modelo de lenguaje) y **hablar** (texto a voz). Hay dos formas de armarlo y estos manuales usan la segunda.

| Forma | Cómo es | Lo bueno | Lo malo |
|---|---|---|---|
| **Piezas separadas** | Un servicio para oír, otro para pensar, otro para hablar. Tú coordinas los tres | Eliges lo mejor de cada uno | Tres conexiones, tres latencias que se suman, y **tú** decides cuándo terminó de hablar la persona y cuándo interrumpir |
| **Agente integrado** (Deepgram Voice Agent) | **Una sola conexión WebSocket** hace los tres trabajos y maneja los turnos | Mucho menos código; el audio de telefonía entra y sale tal cual | Dependes de un proveedor; el modelo de lenguaje lo eliges dentro de sus opciones |

## 1. Por qué Deepgram encaja con telefonía

- **Habla el audio de la telefonía tal cual.** Acepta y entrega `alaw` y `mulaw` a 8 kHz, que es lo que sale de Asterisk por `chan_websocket`. No hay que convertir ni remuestrear en ninguna dirección. No es exclusivo de Deepgram (otros proveedores de voz en tiempo real también aceptan G.711), pero sí es una condición que conviene verificar antes de elegir uno: si el proveedor pide 16 o 24 kHz, hay que convertir en ambos sentidos.
- **Una conexión, un protocolo.** El *Voice Agent API* (`wss://agent.deepgram.com/v1/agent/converse`) recibe un mensaje de configuración (`Settings`) y de ahí en adelante solo audio binario y eventos JSON. Es lo que hace posible el ejemplo puro en 200 líneas.
- **Los turnos y las interrupciones vienen resueltos.** El servicio avisa cuando la persona empieza a hablar (`UserStartedSpeaking`), cuando el bot terminó (`AgentAudioDone`) y entrega la transcripción (`ConversationText`).
- **Voz en español de verdad.** Las voces Aura-2 tienen variantes por región (en el ejemplo, `aura-2-celeste-es`); el acento va en la voz, no en el prompt.
- **Se puede cambiar de modelo sin tocar la telefonía.** Todo lo que cambia está en el mensaje `Settings`: el oído, el modelo de lenguaje, la voz.

Lo que **no** resuelve y sigue siendo tuyo: las herramientas del bot (agendar, consultar), qué hacer si la persona no contesta, cómo transferir a un humano y colgar bien. Por eso existe galcymedia.

## 2. Qué es Flux

Hasta hace poco, "oír" quería decir transcribir (modelos como Nova-3), y saber **cuándo terminó la persona de hablar** se resolvía aparte con un detector de voz y un temporizador de silencio. Eso causa los dos fallos clásicos de un bot de voz: **interrumpir a quien hace una pausa para pensar** o **tardar en contestar** porque espera demasiado silencio.

**Flux** es el modelo de Deepgram para agentes de voz que **junta la transcripción con la detección de fin de turno en el mismo modelo**: decide que la persona terminó mirando el contexto de lo que dijo, no solo el silencio. Según Deepgram: nació para conversación, detecta el fin de turno en unos 260 ms, tiene una variante `EagerEndOfTurn` para que el modelo de lenguaje empiece a responder antes de que la persona termine del todo, y sus umbrales se pueden ajustar para elegir entre responder rápido o esperar más.

Fuentes (léelas antes de decidir en un proyecto real, las cifras cambian):

- Deepgram: <https://deepgram.com/flux> y la guía <https://developers.deepgram.com/docs/flux/quickstart>
- Variante multilingüe `flux-general-multi` (10 idiomas, entre ellos español): <https://www.implicator.ai/deepgram-launches-flux-multilingual-speech-model-with-10-language-mid-call-switching/>

### Los dos modelos en el mensaje `Settings`

El campo `version` decide qué esquema valida Deepgram y **no son intercambiables**: mezclar campos mata el saludo (el apretón de manos falla y la llamada no se levanta).

| | Nova-3 (v1) | Flux (v2) |
|---|---|---|
| `type` y `version` | `deepgram`, `v1` | `deepgram`, `v2` |
| `model` | `nova-3` | `flux-general-multi` (español incluido) o `flux-general-en` (solo inglés) |
| Idioma | `language: "es"` | `language_hints: ["es"]` |
| Fin de turno | Lo decide el servicio, sin ajuste | **Es tuyo**: `eot_threshold` (0,5 a 0,9; por defecto 0,7) y `eot_timeout_ms` |
| Cuándo conviene | Cuando no quieres afinar nada | Cuando el bot interrumpe a la gente o tarda en contestar |

**Subir `eot_threshold`** hace al bot más paciente (agrupa mejor a quien habla con pausas) a cambio de contestar más tarde. No existe un valor universal: depende de tu tráfico, y la forma seria de decidirlo es medir con llamadas reales.

### Verificado al preparar esta guía

El agente puro (documento 02) se probó con `DEEPGRAM_MODEL=flux-general-multi` en Asterisk 20.18.0: Deepgram aceptó el esquema v2 con pista de idioma español y el bot saludó. **No se midió** la calidad de la detección de turnos con una persona real: eso hay que escucharlo con una llamada real.

## 3. Cuándo NO usar un agente integrado

- Si necesitas **el mejor modelo de lenguaje del mercado** en cada turno, o uno propio o local: piezas separadas.
- Si los datos de las llamadas **no pueden salir** de tu infraestructura: ejecuta modelos propios (por ejemplo, el reconocimiento con Vosk del taller 12).
- Si ya tienes un motor conversacional de negocio (IVR con reglas, colas, reconocimiento de intenciones propio): el agente integrado se vuelve un componente más, no el centro.

Hay **muchas formas** de armar un agente de voz. Los dos ejemplos (puro y galcymedia) usan el mismo proveedor a propósito, para que veas que lo que cambia no es *quién* oye y habla sino **cuánto trabajo de transporte y de casos raros te resuelven**. Cambiar a otro proveedor (OpenAI Realtime, ElevenLabs) es cambiar de adaptador y reescribir el `Settings`, no la telefonía.
