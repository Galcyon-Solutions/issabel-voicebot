#!/bin/bash
# Reversa de 01_crear_escenario.sh: quita la Misc Application, el IVR "Demo Voicebot" y los destinos personalizados.
#   bash escenario/98_quitar_escenario.sh [--galcymedia 7500] [--puro 7501]
set -uo pipefail
GAL=7500; PURO=7501
while [ $# -gt 0 ]; do
  case "$1" in
    --galcymedia) GAL="$2"; shift ;; --puro) PURO="$2"; shift ;;
    *) echo "Argumento desconocido: $1"; exit 2 ;;
  esac; shift
done
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
install -m 644 "$HERE/quitar_escenario.php" /var/tmp/quitar_escenario.php
sudo -u asterisk php /var/tmp/quitar_escenario.php "$GAL" "$PURO"; rm -f /var/tmp/quitar_escenario.php
sudo -u asterisk /var/lib/asterisk/bin/retrieve_conf >/dev/null 2>&1 || /var/lib/asterisk/bin/retrieve_conf >/dev/null 2>&1
asterisk -rx 'dialplan reload' | tail -1
echo "Escenario retirado"
