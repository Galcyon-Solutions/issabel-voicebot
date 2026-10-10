# Actualizar el Asterisk de Issabel 5 a 20.18 (con chan_websocket)

Issabel trae su propio Asterisk empaquetado en RPM y se queda atrás: la ISO de abril de 2024 instala **Asterisk 18.19**, la ISO de octubre de 2026 instala **20.12**. El canal `chan_websocket` (audio por WebSocket, la base del voicebot) existe desde **Asterisk 20.16**. Este manual te lleva a **20.18.0** sin salirte del sistema de paquetes de Issabel: se construye un RPM con **el mismo spec y los mismos parches** que usa Issabel, y se instala encima.

> Regla de oro del manual: **nunca compiles Asterisk con `make install` encima de un Issabel.** Pisa archivos que pertenecen a RPM, deja la base de paquetes mentirosa y la próxima actualización de Issabel lo rompe. Un RPM se instala, se verifica, se actualiza y se **revierte**.

## 1. Qué cambia y qué se pierde

| | 20.12.0 (ISO 2026) | 20.18.0 (este manual) |
|---|---|---|
| `chan_websocket` y `res_websocket_client` | no existen | **sí** |
| Parches de Issabel (`inhibit escalations` de tcptls, ping de WebSocket, Vosk con varios servidores) | sí | **sí, los mismos** |
| `res_stir_shaken` y `res_pjsip_stir_shaken` | sí | **no**: piden una `libjwt` más nueva que la de EPEL 8, y IssabelPBX no los usa |
| Módulos que Asterisk eliminó (`app_url`, `app_image`, `chan_oss`, `app_ices`, `app_nbscat`, `app_dahdiras`, `chan_misdn`, `app_mysql`, `cdr_mysql`) | los que hubiera | ya no existen en ninguna 20.x nueva |
| Módulos desactivados por defecto en 20.18 que Issabel sí usa (`chan_sip`, `res_monitor`, `chan_skinny`, `chan_alsa`) | sí | **se reactivan** con `menuselect` en el spec |

En un Issabel real de prueba la actualización cargó **los mismos módulos** que antes (menos los dos de STIR/SHAKEN), y se verificaron: llamadas SIP con autenticación, el marcador del Call Center (conexión AMI y ECCP), la extensión WebRTC con `transport-wss`, DTLS e ICE.

## 2. Antes de empezar

- Servidor **sin llamadas activas**. Es una actualización con reinicio de Asterisk (unos 15 segundos sin servicio).
- Acceso `root` y los repositorios de Issabel habilitados (`dnf repolist | grep -i issabel`).
- Una copia de seguridad **fuera del servidor** (snapshot del VPS). El script hace además la suya, pero el snapshot es lo que te salva de verdad.
- Sabe con qué partes: `rpm -qa 'asterisk*' | sort`.

Tu punto de partida decide el camino:

| Versión actual | Camino |
|---|---|
| Asterisk **20.x de Issabel** (20.12) | Sección 3 o 4: `02_actualizar.sh` |
| Asterisk **18.x** (ISO 2024 o netinstall) | Sección 6: `03_migrar_18_a_20.sh` |

## 3. Camino rápido: instalar los RPM ya construidos

La carpeta `dist/` (26 RPM, 7,6 MB, con su `SHA256SUMS`) se descarga de los archivos de la Release del repositorio, o se construye con la sección 4.

```bash
cd issabel-voicebot
( cd dist && sha256sum -c SHA256SUMS )         # todos deben decir OK (o 'La suma coincide', segun el idioma)
bash asterisk/02_actualizar.sh dist --si
```

El script, en orden:

1. Aborta si hay **llamadas activas** o si no hay un `asterisk20` de Issabel instalado.
2. **Respaldo** en `/root/respaldo-asterisk-<fecha>`: lista de módulos cargados, lista de paquetes, `/etc/asterisk`, binarios y módulos, volcado de la base `asterisk` y los RPM.
3. Instala con `dnf` (no con `rpm -Uvh`: `dnf` resuelve dependencias, por ejemplo `freeradius-client`, que sale de EPEL).
4. **Reinicia** Asterisk y compara la versión que corre con la instalada.
5. Muestra los módulos que **estaban y ya no**, y los **nuevos**, y si `chan_websocket` cargó.

Resultado esperado:

```
Asterisk 20.18.0 built by root @ ...
OK: ejecutando 20.18.0 (igual al paquete instalado)
--- modulos que estaban y ya no:
res_pjsip_stir_shaken.so
res_stir_shaken.so
chan_websocket: 1
```

Si algo sale distinto, no sigas: revisa la sección 7.

## 4. Camino completo: construir tú el RPM

Para entender qué se instala (o para otra versión 20.x). Tarda unos 20 minutos con 16 núcleos y hasta 90 con 2.

```bash
bash build/00_dependencias.sh        # paquetes -devel (powertools, EPEL e Issabel)
bash build/01_construir_rpm.sh       # descarga, verifica el hash, compila y empaqueta
ls dist/                             # 26 RPM + SHA256SUMS
```

Qué hace `01_construir_rpm.sh`:

- Baja el **SRPM del Asterisk 18 de Issabel** (`repo.issabel.org`) solo para sacar de ahí lo que Issabel le añade: el parche que desactiva `inhibit escalations`, el parche del ping de WebSocket, el módulo `res_speech_vosk` con varios servidores, la unidad de systemd, el logrotate y las confs de CDR/ODBC. **El SRPM del Asterisk 20 de Issabel no es público**, por eso el spec de este repositorio (`build/asterisk20.spec`) está derivado del de la versión 18.
- Baja `asterisk-20.18.0.tar.gz` de `downloads.asterisk.org` y **verifica el SHA-256** contra el archivo `.sha256` que publica Asterisk.
- Compila con `rpmbuild -bb`.

El spec ya trae los cambios necesarios respecto al de la versión 18: `menuselect` reactiva `chan_sip`, `res_monitor`, `chan_skinny` y `chan_alsa`; `%files` quita los módulos eliminados y añade los nuevos (`chan_websocket`, `res_websocket_client`, `app_if`, `func_uuid`, `res_geolocation`, `codec_codec2`, `res_resolver_unbound`, y otros); el `make config` crea antes `/etc/rc.d/init.d`.

## 5. Verificar (siempre)

```bash
asterisk -rx 'core show version'                    # Asterisk 20.18.0
asterisk -rx 'core show channeltype WebSocket'      # debe existir
asterisk -rx 'module show like websocket'           # chan_websocket, res_websocket_client...
asterisk -rx 'pjsip show transports'                # si usas el webphone: transport-wss
asterisk -rx 'sip show peers' | tail -1             # si usas chan_sip
systemctl status issabeldialer                      # si usas el Call Center
```

Haz **una llamada de prueba** entre dos extensiones y marca `*43` (eco): si oyes tu voz, el audio está bien.

## 6. Migración desde Asterisk 18

Es el caso de un Issabel instalado con la ISO de 2024 o con `netinstall`, con **Asterisk 18.19** y paquetes `asterisk18-*`. Los paquetes `asterisk18` y `asterisk20` **se pisan archivos entre sí** (`/usr/sbin/asterisk`, las cabeceras, los módulos), así que no se puede "actualizar": hay que quitar los 18 e instalar los 20. El script lo hace de forma segura:

```bash
bash asterisk/03_migrar_18_a_20.sh dist --si
```

Qué hace, y por qué así:

1. Respaldo completo (`/root/respaldo-migracion18-<fecha>`): módulos cargados, lista de paquetes, `/etc/asterisk`, binarios, volcado de la base `asterisk`.
2. **Descarga antes** los RPM nuevos y sus dependencias (`--downloadonly`): si falta algo, lo descubres con el servidor todavía sano.
3. Quita **solo** los `asterisk18*` con `rpm -e --nodeps`. No uses `dnf remove asterisk18`: arrastraría `issabel-pbx` y media Issabel por las dependencias.
4. Instala el mismo conjunto en versión 20 (más `asterisk20-sqlite3`), reinicia y compara la versión que corre con la instalada.
5. **Restaura lo que Asterisk 18 tenía cargado y el módulo nuevo deshabilita**: el `modules.conf` que trae el paquete 20 pone `noload = chan_sip.so` (y `res_hep*`). Si tus extensiones son `chan_sip`, sin este paso dejarían de registrarse. El script comenta ese `noload` solo para los módulos que estaban cargados antes y existen en disco.

Resultado verificado (Issabel por `netinstall` con Asterisk 18.19 y Call Center 5.1.1):

```
OK: ejecutando 20.18.0 (igual al paquete instalado)
--- modulos que estaban y ya no:
app_dahdiras  app_ices  app_image  app_mysql  app_nbscat  app_url      <- eliminados por Asterisk en 19/20
res_pjsip_stir_shaken  res_stir_shaken                                    <- necesitan libjwt nuevo (no se usan)
--- modulos nuevos:
chan_websocket  res_websocket_client  codec_codec2  func_uuid  res_geolocation ...
```

Después de migrar, **actualiza el Call Center** (`issabel-instalacion/scripts/actualizar-callcenter.sh --si`): la versión 5.1.13 detecta Asterisk 20 y usa el modo `app_agent_pool`.

Cosas esperables en el registro, que **no son fallos**:

- `ERROR ... chan_local.so ... cannot open shared object file`: `modules.conf` tiene `preload => chan_local.so`, y en Asterisk 20 `chan_local` ya viene dentro del núcleo. El canal `Local/` funciona igual.
- `WARNING ... app_macro ... deprecated`: el dialplan de IssabelPBX todavía usa `Macro`. Desaparece en Asterisk 21; por eso no se pasa de la 20 en Issabel.
- `ERROR ... Declined modules which depend on res_xmpp: chan_motif`: no se usa.

Volver atrás de la migración: `bash asterisk/99_revertir_a_18.sh /root/respaldo-migracion18-<fecha> --si` (quita los `asterisk20*` y reinstala los `asterisk18` del repositorio de Issabel). Se probó: queda Asterisk 18.19.0 con los 347 módulos de antes y el marcador del Call Center activo.


## 7. Volver atrás

```bash
bash asterisk/99_revertir.sh /root/respaldo-asterisk-<fecha> --si
```

- Camino principal: `dnf downgrade` a la versión anterior desde un repositorio que la tenga. Con la ISO de Issabel 5 la tienes si **conservas el archivo ISO** y lo montas como repositorio (ver el manual de instalación): por eso se recomienda no borrarla.
- Alternativa (si el repositorio ya no tiene esa versión): el script restaura binarios y módulos del respaldo. Funciona, pero deja la base de RPM diciendo "20.18" aunque corran los binarios viejos y puede quedar algún módulo suelto de la versión nueva. Úsala como emergencia y, cuando puedas, reinstala los paquetes de verdad.
- El cambio de **configuración** es mínimo: `02_actualizar.sh` no edita archivos de `/etc/asterisk` (el RPM respeta los `*.conf` que ya existen).

## 8. Cosas que enseñan los fallos de esta guía

1. **`rpm -Uvh` falla en seco y `dnf` no**: el RPM de Asterisk necesita `libfreeradius-client.so.2`, que está en EPEL. `rpm` solo dice "Failed dependencies"; `dnf` lo instala solo.
2. **`start` no es `restart`**: durante la transacción de `dnf` algo puede dejar arrancado el Asterisk viejo; con `systemctl start` creerías que actualizaste mientras sigue corriendo el 20.12. El script reinicia y comprueba la versión en ejecución.
3. **`rpmbuild -bl` solo informa de un subpaquete por pasada** cuando faltan archivos: para encontrar todo lo que falta hay que repetir, o comparar la lista de archivos del RPM viejo con la del nuevo (así se encontraron los módulos nuevos de 20.16 a 20.18).
4. **Windows escribe CRLF**: un `spec` con finales de línea de Windows da `Illegal char 0xd`. Convierte con `sed -i 's/\r$//'`.
5. **Compilar es lento: trabaja en segundo plano** (`setsid nohup ... &`) y mira el registro, no te quedes colgado en el terminal.
6. **La coma decimal te deja sin teléfonos.** En un servidor con idioma español (`es_PE`, `es_ES`: `locale decimal_point` devuelve `,`), Asterisk 20.18 **no entiende `qualify_timeout=3.0`** del `pjsip_additional.conf` y no crea ningún AOR de PJSIP: los endpoints existen pero **ningún teléfono registra**. El síntoma está en el registro (`Unable to set default for 1000, qualify_timeout=3.0`) y en `pjsip show aors` (`No objects found`). Con Asterisk 18 no pasaba. Se arregla pidiéndole a Asterisk que lea los números con punto, con un drop-in de systemd (`/etc/systemd/system/asterisk.service.d/locale.conf` con `Environment=LC_NUMERIC=C`) y reiniciándolo; **los scripts `02_actualizar.sh` y `03_migrar_18_a_20.sh` ya lo hacen** cuando detectan coma decimal y al final imprimen cuántos endpoints y AOR hay. Verificado en un servidor real: tras el arreglo `pjsip show aors` pasó de 0 a 11 objetos.
