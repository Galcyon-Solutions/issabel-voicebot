#!/bin/bash
# Reversa de 02_actualizar.sh: vuelve a los paquetes que tenias antes (20.12.0 de Issabel).
#   bash asterisk/99_revertir.sh /root/respaldo-asterisk-<fecha> --si
# Camino principal: dnf downgrade desde los repositorios de Issabel. Si el repositorio ya no tiene esa version,
# restaura los binarios y la configuracion del respaldo.
set -uo pipefail
BK="${1:-}"; [ "${2:-}" = "--si" ] || { echo "Uso: $0 <respaldo> --si"; exit 1; }
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
[ -d "$BK" ] && [ -f "$BK/paquetes.txt" ] || { echo "ABORTA: respaldo invalido: $BK"; exit 1; }
n=$(asterisk -rx 'core show channels count' 2>/dev/null | awk '/active channel/{print $1}')
[ "${n:-0}" = "0" ] || { echo "ABORTA: hay $n canal(es) activo(s)"; exit 1; }
systemctl stop asterisk 2>&1 | tail -1
VER_ANTES=$(sed -n 's/^asterisk20-\([0-9.]*\)-.*/\1/p' "$BK/paquetes.txt" | head -1)
PKGS=$(sed -E 's/-[0-9.]+-[0-9]+\.el8\.x86_64$//' "$BK/paquetes.txt" | tr '\n' ' ')
echo "== Volviendo a $VER_ANTES: $PKGS =="
dnf -y --allowerasing downgrade $PKGS 2>&1 | tail -8 || true
if ! rpm -q asterisk20 | grep -q "$VER_ANTES"; then
  echo "dnf no pudo (repos sin $VER_ANTES): restauro binarios desde el respaldo"
  tar -C / -xpf "$BK/binarios.tar"
fi
tar -C / -xpf "$BK/config.tar" && echo "config restaurada"
systemctl daemon-reload; systemctl restart asterisk; sleep 12
asterisk -rx 'core show version'
echo -n "modulos cargados: "; asterisk -rx 'module show' | awk 'NR>1 && /\.so/{print $1}' | wc -l
