#!/bin/bash
# Reversa de 03_migrar_18_a_20.sh: quita asterisk20 y reinstala asterisk18 desde el repositorio de Issabel.
#   bash asterisk/99_revertir_a_18.sh /root/respaldo-migracion18-<fecha> --si
# Despues restaura /etc/asterisk del respaldo. La base de datos NO se toca (el volcado queda en el respaldo por si acaso).
set -uo pipefail
BK="${1:-}"; [ "${2:-}" = "--si" ] || { echo "Uso: $0 <respaldo> --si"; exit 1; }
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
[ -d "$BK" ] && [ -f "$BK/paquetes.txt" ] || { echo "ABORTA: respaldo invalido: $BK"; exit 1; }
n=$(asterisk -rx 'core show channels count' 2>/dev/null | awk '/active channel/{print $1}')
[ "${n:-0}" = "0" ] || { echo "ABORTA: hay $n canal(es) activo(s)"; exit 1; }
VIEJOS=$(sed -E 's/-18\.[0-9]+\.[0-9]+-[0-9]+\.el8\.x86_64$//' "$BK/paquetes.txt" | tr '\n' ' ')
echo "== Volviendo a Asterisk 18: $VIEJOS =="
systemctl stop asterisk 2>&1 | tail -1
rpm -e --nodeps $(rpm -qa 'asterisk20*') 2>&1 | tail -3
dnf -y install $VIEJOS 2>&1 | tail -6
if ! rpm -q asterisk18 >/dev/null 2>&1; then
  echo "dnf no pudo instalar asterisk18 (repositorios): restauro binarios desde el respaldo"
  tar -C / -xpf "$BK/binarios.tar"
fi
tar -C / -xpf "$BK/config.tar" && echo "config restaurada"
systemctl daemon-reload; systemctl restart asterisk; sleep 15
asterisk -rx 'core show version'
echo -n "modulos cargados: "; asterisk -rx 'module show' | awk 'NR>1 && /\.so/{print $1}' | wc -l
