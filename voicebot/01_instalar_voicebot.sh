#!/bin/bash
# Instala el voicebot galcymedia (ejemplo 02-agent) en un Issabel 5 con Asterisk 20.16 o superior (chan_websocket).
#   bash voicebot/01_instalar_voicebot.sh --ext-bot 7500 --destino-humano 7000   (una cola o una extension)
# Idempotente. No pide ni guarda claves: tu DEEPGRAM_API_KEY la pones tu en /opt/galcymedia-agent/app/.env
# Reversa: bash voicebot/98_quitar_voicebot.sh
set -uo pipefail
EXT_BOT=7500; EXT_HUMANO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --ext-bot) EXT_BOT="$2"; shift ;;
    --destino-humano|--ext-humano) EXT_HUMANO="$2"; shift ;;
    *) echo "Argumento desconocido: $1"; exit 2 ;;
  esac; shift
done
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
[ -n "$EXT_HUMANO" ] || { echo "Falta --destino-humano (el numero interno al que pasa el bot cuando piden una persona: una cola como 7000 o una extension)"; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
APP=/opt/galcymedia-agent
# Version del repo de ejemplos que se probo en esta guia (fijada; cambiala solo si revisaste el cambio)
EJEMPLOS_REF=211d9582a541b54b8ddf18696272e4103ad140c5
BK=/root/respaldo-voicebot-$(date +%Y%m%d-%H%M%S)

echo "== Comprobaciones =="
asterisk -rx 'core show version' | head -1
asterisk -rx 'core show channeltype WebSocket' | grep -q 'Device State' || { echo "ABORTA: este Asterisk no tiene chan_websocket (necesitas 20.16 o superior: ver asterisk/02_actualizar.sh)"; exit 1; }
DESTINO_INFO=$(asterisk -rx "dialplan show $EXT_HUMANO@from-internal" 2>/dev/null)   # en una variable: grep -q con pipefail daria falso aviso por SIGPIPE
grep -qE "Gosub|Macro|Goto|Dial|Queue" <<< "$DESTINO_INFO" || echo "AVISO: $EXT_HUMANO no existe como destino en from-internal; la transferencia fallara hasta que lo crees."
install -d -m 700 "$BK"; cp -a /etc/asterisk/extensions_custom.conf /etc/asterisk/websocket_client.conf "$BK/"

echo "== Python 3.12 y entorno virtual =="
rpm -q python3.12 >/dev/null 2>&1 || dnf -y install python3.12 python3.12-pip 2>&1 | tail -1
install -d -o asterisk -g asterisk "$APP" "$APP/app"
[ -x "$APP/venv/bin/python" ] || python3.12 -m venv "$APP/venv"
"$APP/venv/bin/pip" install -q --upgrade pip 2>&1 | tail -1
"$APP/venv/bin/pip" install -q "galcymedia[deepgram]" 2>&1 | tail -2
"$APP/venv/bin/pip" list 2>/dev/null | grep -iE "^(galcymedia|websockets|deepgram)"

echo "== Ejemplo 02-agent (Galcyon-Solutions/galcymedia-examples @ ${EJEMPLOS_REF:0:7}) =="
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
curl -fsSL "https://github.com/Galcyon-Solutions/galcymedia-examples/archive/$EJEMPLOS_REF.tar.gz" | tar xz -C "$W" --strip-components=1
for f in main.py config.py agent.py tools.py prompt.py __init__.py; do cp -f "$W/examples/02-agent/$f" "$APP/app/$f"; done
[ -f "$APP/app/.env" ] || sed -E 's/^DEEPGRAM_API_KEY=.*/DEEPGRAM_API_KEY=/' "$W/examples/02-agent/.env.example" > "$APP/app/.env"
chown -R asterisk:asterisk "$APP"; chmod 600 "$APP/app/.env"
cp -f "$HERE/conf/galcymedia-agent.service" /etc/systemd/system/galcymedia-agent.service; systemctl daemon-reload

echo "== Asterisk: cliente WebSocket y dialplan =="
grep -q '^\[voicebot\]' /etc/asterisk/websocket_client.conf || cat "$HERE/conf/websocket_client_voicebot.conf" >> /etc/asterisk/websocket_client.conf
sed -e "s/@EXT_BOT@/$EXT_BOT/g" -e "s/@EXT_HUMANO@/$EXT_HUMANO/g" "$HERE/conf/extensions_galcymedia.conf" > /etc/asterisk/extensions_galcymedia.conf
chown asterisk:asterisk /etc/asterisk/extensions_galcymedia.conf; chmod 644 /etc/asterisk/extensions_galcymedia.conf
grep -q 'extensions_galcymedia.conf' /etc/asterisk/extensions_custom.conf || printf '\n#include extensions_galcymedia.conf\n' >> /etc/asterisk/extensions_custom.conf
n=$(asterisk -rx 'core show channels count' | awk '/active channel/{print $1}')
if [ "${n:-0}" = "0" ]; then
  asterisk -rx 'module reload res_websocket_client.so' | tail -1; asterisk -rx 'dialplan reload' | tail -1
else
  echo "AVISO: hay $n canal(es) activo(s); recarga luego: asterisk -rx 'dialplan reload'"
fi

echo "== Verificacion =="
asterisk -rx "dialplan show $EXT_BOT@from-internal" | sed -n 1,4p
"$APP/venv/bin/python" -c "import galcymedia,sys; print('galcymedia', getattr(galcymedia,'__version__','?'), '| python', sys.version.split()[0])"
cat <<MSG

Falta tu clave del proveedor. Edita $APP/app/.env, pon DEEPGRAM_API_KEY y arranca:
    nano $APP/app/.env
    systemctl enable --now galcymedia-agent
    journalctl -u galcymedia-agent -f
Prueba: marca $EXT_BOT desde un softphone registrado (o con SIPp: sipp/README.md).
Respaldo: $BK
MSG
