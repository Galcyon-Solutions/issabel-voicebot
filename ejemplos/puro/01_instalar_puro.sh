#!/bin/bash
# Instala el agente de voz PURO (un archivo de Python + websockets) en un Issabel con Asterisk 20.16 o superior.
#   bash ejemplos/puro/01_instalar_puro.sh --ext 7501
# Idempotente. No pide ni guarda claves: tu DEEPGRAM_API_KEY la pones en /opt/agente-puro/.env
# Reversa: bash ejemplos/puro/98_quitar_puro.sh
set -uo pipefail
EXT=7501
while [ $# -gt 0 ]; do
  case "$1" in
    --ext) EXT="$2"; shift ;;
    *) echo "Argumento desconocido: $1"; exit 2 ;;
  esac; shift
done
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
APP=/opt/agente-puro
BK=/root/respaldo-puro-$(date +%Y%m%d-%H%M%S)

echo "== Comprobaciones =="
asterisk -rx 'core show version' | head -1
asterisk -rx 'core show channeltype WebSocket' | grep -q 'Device State' || { echo "ABORTA: este Asterisk no tiene chan_websocket (necesitas 20.16 o superior)"; exit 1; }
install -d -m 700 "$BK"; cp -a /etc/asterisk/extensions_custom.conf /etc/asterisk/websocket_client.conf "$BK/"

echo "== Python 3.12, entorno virtual y websockets =="
rpm -q python3.12 >/dev/null 2>&1 || dnf -y install python3.12 python3.12-pip 2>&1 | tail -1
install -d -o asterisk -g asterisk "$APP"
[ -x "$APP/venv/bin/python" ] || python3.12 -m venv "$APP/venv"
"$APP/venv/bin/pip" install -q --upgrade pip 2>&1 | tail -1
"$APP/venv/bin/pip" install -q "websockets>=14" 2>&1 | tail -1
"$APP/venv/bin/pip" list 2>/dev/null | grep -iE "^websockets"
cp -f "$HERE/agente_puro.py" "$APP/agente_puro.py"
[ -f "$APP/.env" ] || printf 'DEEPGRAM_API_KEY=\n' > "$APP/.env"
chown -R asterisk:asterisk "$APP"; chmod 600 "$APP/.env"
cp -f "$HERE/conf/agente-puro.service" /etc/systemd/system/agente-puro.service; systemctl daemon-reload

echo "== Asterisk: cliente WebSocket y dialplan =="
grep -q '^\[voicepuro\]' /etc/asterisk/websocket_client.conf || cat "$HERE/conf/websocket_client_voicepuro.conf" >> /etc/asterisk/websocket_client.conf
sed "s/@EXT@/$EXT/g" "$HERE/conf/extensions_agente_puro.conf" > /etc/asterisk/extensions_agente_puro.conf
chown asterisk:asterisk /etc/asterisk/extensions_agente_puro.conf; chmod 644 /etc/asterisk/extensions_agente_puro.conf
grep -q 'extensions_agente_puro.conf' /etc/asterisk/extensions_custom.conf || printf '\n#include extensions_agente_puro.conf\n' >> /etc/asterisk/extensions_custom.conf
n=$(asterisk -rx 'core show channels count' | awk '/active channel/{print $1}')
if [ "${n:-0}" = "0" ]; then
  asterisk -rx 'module reload res_websocket_client.so' | tail -1; asterisk -rx 'dialplan reload' | tail -1
else
  echo "AVISO: hay $n canal(es) activo(s); recarga luego: asterisk -rx 'dialplan reload'"
fi
echo "== Verificacion =="
asterisk -rx "dialplan show $EXT@from-internal" | sed -n 1,4p
cat <<MSG

Falta tu clave. Edita $APP/.env, pon DEEPGRAM_API_KEY y arranca:
    nano $APP/.env
    systemctl enable --now agente-puro
    journalctl -u agente-puro -f
Prueba: marca $EXT. (Respaldo: $BK)
MSG
