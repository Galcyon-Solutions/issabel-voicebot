#!/bin/bash
# Reversa de 01_instalar_voicebot.sh: quita servicio, aplicacion, entorno virtual, dialplan y la seccion [voicebot].
# No toca Asterisk 20.18 (ver asterisk/99_revertir.sh).
set -uo pipefail
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
systemctl disable --now galcymedia-agent 2>/dev/null; rm -f /etc/systemd/system/galcymedia-agent.service; systemctl daemon-reload
rm -rf /opt/galcymedia-agent /etc/asterisk/extensions_galcymedia.conf
sed -i '/^#include extensions_galcymedia.conf$/d' /etc/asterisk/extensions_custom.conf
sed -i '/^; --- galcymedia voicebot ---$/,/^tls_enabled = no$/d' /etc/asterisk/websocket_client.conf
asterisk -rx 'dialplan reload' | tail -1; asterisk -rx 'module reload res_websocket_client.so' | tail -1
echo "Voicebot retirado"
