#!/bin/bash
# Reversa de 01_instalar_puro.sh.
set -uo pipefail
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
systemctl disable --now agente-puro 2>/dev/null; rm -f /etc/systemd/system/agente-puro.service; systemctl daemon-reload
rm -rf /opt/agente-puro /etc/asterisk/extensions_agente_puro.conf
sed -i '/^#include extensions_agente_puro.conf$/d' /etc/asterisk/extensions_custom.conf
sed -i '/^; --- agente puro ---$/,/^tls_enabled = no$/d' /etc/asterisk/websocket_client.conf
asterisk -rx 'dialplan reload' | tail -1; asterisk -rx 'module reload res_websocket_client.so' | tail -1
echo "Agente puro retirado"
