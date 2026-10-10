#!/bin/bash
# Crea el escenario completo de estos manuales en IssabelPBX: Misc Application -> IVR -> Custom Destinations -> voicebots.
#   bash escenario/01_crear_escenario.sh [--menu 7800] [--galcymedia 7500] [--puro 7501]
# Usa las funciones de IssabelPBX (como la web), respalda la base antes y aplica con retrieve_conf.
# Reversa: bash escenario/98_quitar_escenario.sh
set -uo pipefail
MENU=7800; GAL=7500; PURO=7501
while [ $# -gt 0 ]; do
  case "$1" in
    --menu) MENU="$2"; shift ;; --galcymedia) GAL="$2"; shift ;; --puro) PURO="$2"; shift ;;
    *) echo "Argumento desconocido: $1"; exit 2 ;;
  esac; shift
done
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
# El numero del menu no puede estar ya en uso (una cola, una extension...): en una central real la 7000 suele ser una cola
if ! asterisk -rx "dialplan show $MENU@from-internal" | grep -q "No such"; then
  if ! asterisk -rx "dialplan show $MENU@from-internal" | grep -q "app-miscapps"; then echo "ABORTA: el numero $MENU ya existe en tu central (usa --menu con otro, por ejemplo 7800):"; asterisk -rx "dialplan show $MENU@from-internal" | sed -n 1,3p; exit 1; fi
fi
BK=/root/respaldo-escenario-$(date +%Y%m%d-%H%M%S); install -d -m 700 "$BK"
MYSQL_PWD=$(awk -F= '/^mysqlrootpwd/{print $2}' /etc/issabel.conf) mysqldump -uroot --single-transaction asterisk > "$BK/asterisk.sql" 2>/dev/null && chmod 600 "$BK/asterisk.sql"
echo "Respaldo de la base: $BK"

# El usuario asterisk no lee /root: el PHP se copia a /var/tmp
install -m 644 "$HERE/crear_escenario.php" /var/tmp/crear_escenario.php
sudo -u asterisk php /var/tmp/crear_escenario.php "$MENU" "$GAL" "$PURO" || { echo "Fallo al crear el escenario (la base no se toco por completo: respaldo en $BK)"; rm -f /var/tmp/crear_escenario.php; exit 1; }
rm -f /var/tmp/crear_escenario.php

echo "== Aplicando =="
sudo -u asterisk /var/lib/asterisk/bin/retrieve_conf >/dev/null 2>&1 || /var/lib/asterisk/bin/retrieve_conf >/dev/null 2>&1
n=$(asterisk -rx 'core show channels count' | awk '/active channel/{print $1}')
if [ "${n:-0}" = "0" ]; then asterisk -rx 'dialplan reload' | tail -1; else echo "AVISO: hay $n llamada(s); recarga luego con: asterisk -rx 'dialplan reload'"; fi
asterisk -rx "dialplan show $MENU@from-internal" | sed -n 1,4p
echo "Prueba: marca $MENU y pulsa 1 (galcymedia) o 2 (agente puro)."
