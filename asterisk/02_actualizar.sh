#!/bin/bash
# Actualiza el Asterisk 20 de Issabel 5 (20.12.0 de la ISO) a 20.18.0, con respaldo y verificacion.
#   bash asterisk/02_actualizar.sh <carpeta-con-los-RPM> --si
# La carpeta es ./dist (RPM de este repo) o ~/rpmbuild/RPMS/x86_64 (si los compilaste tu).
# Aborta si hay llamadas activas o si el Asterisk instalado no es el asterisk20 de Issabel.
# Reversa: bash asterisk/99_revertir.sh <carpeta-de-respaldo> --si
set -uo pipefail
RPMDIR="${1:-}"; [ "${2:-}" = "--si" ] || { echo "Uso: $0 <carpeta-con-los-RPM> --si"; exit 1; }
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
ls "$RPMDIR"/asterisk20-20.18.0-*.rpm >/dev/null 2>&1 || { echo "ABORTA: no hay RPM 20.18.0 en $RPMDIR"; exit 1; }
rpm -q asterisk20 >/dev/null 2>&1 || { echo "ABORTA: no hay asterisk20 instalado (este parche es para Issabel 5 con Asterisk 20)"; exit 1; }
n=$(asterisk -rx 'core show channels count' | awk '/active channel/{print $1}')
[ "${n:-0}" = "0" ] || { echo "ABORTA: hay $n canal(es) activo(s)"; exit 1; }

BK=/root/respaldo-asterisk-$(date +%Y%m%d-%H%M%S); install -d -m 700 "$BK"
echo "== Respaldo en $BK =="
asterisk -rx 'module show' | awk 'NR>1 && /\.so/{print $1}' | sort > "$BK/modulos-antes.txt"
rpm -qa 'asterisk20*' | sort > "$BK/paquetes.txt"
tar -C / -cpf "$BK/config.tar" etc/asterisk etc/sysconfig/asterisk 2>/dev/null
tar -C / -cpf "$BK/binarios.tar" usr/sbin/asterisk usr/lib64/asterisk var/lib/asterisk/agi-bin 2>/dev/null
MYSQL_PWD=$(awk -F= '/^mysqlrootpwd/{print $2}' /etc/issabel.conf) mysqldump -uroot --single-transaction asterisk > "$BK/asterisk.sql" 2>/dev/null && chmod 600 "$BK/asterisk.sql"
echo "modulos cargados: $(wc -l < "$BK/modulos-antes.txt")  respaldo: $(du -sh "$BK" | cut -f1)"

echo "== Actualizando paquetes (solo los que ya tienes instalados) =="
ANTES=$(rpm -q asterisk20 --qf '%{VERSION}')
PKGS=$(for p in $(sed -E 's/-[0-9.]+-[0-9]+\.el8\.x86_64$//' "$BK/paquetes.txt"); do ls "$RPMDIR/$p"-20.18.0-*.rpm 2>/dev/null | head -1; done)
echo "$PKGS" | sed 's#.*/##'
systemctl stop asterisk 2>&1 | tail -1
# dnf (no rpm -Uvh): resuelve dependencias, p. ej. freeradius-client, que sale de EPEL
rpm -q epel-release >/dev/null 2>&1 || dnf -y install epel-release 2>&1 | tail -1
dnf -y install $PKGS 2>&1 | tail -25
RC=${PIPESTATUS[0]}
echo "== Arrancando =="
# Con coma decimal en el sistema (es_PE, es_ES...) Asterisk 20 no entiende "3.0" (qualify_timeout) y NO crea los AOR de
# PJSIP: ningun telefono registra. Se le pide que lea los numeros con punto (LC_NUMERIC=C) con un drop-in de systemd.
if [ "$(locale decimal_point 2>/dev/null)" != "." ]; then
  install -d /etc/systemd/system/asterisk.service.d
  printf '[Service]
Environment=LC_NUMERIC=C
' > /etc/systemd/system/asterisk.service.d/locale.conf
  echo "Locale con coma decimal: se agrego /etc/systemd/system/asterisk.service.d/locale.conf (LC_NUMERIC=C)"
fi
# restart (no start): durante la transaccion de dnf algo puede dejar arrancado el Asterisk viejo
systemctl daemon-reload; systemctl restart asterisk; sleep 12
asterisk -rx 'core show version'
EJEC=$(asterisk -rx 'core show version' | awk '{print $2}'); INST=$(rpm -q asterisk20 --qf '%{VERSION}')
[ "$EJEC" = "$INST" ] && echo "OK: ejecutando $EJEC (igual al paquete instalado)" || echo "ATENCION: ejecutando $EJEC pero instalado $INST. Reinicia: systemctl restart asterisk"
AORS=$(asterisk -rx 'pjsip show aors' 2>/dev/null | awk '/Objects found/{print $3}'); ENDP=$(asterisk -rx 'pjsip show endpoints' 2>/dev/null | grep -c 'Endpoint: ')
echo "PJSIP: ${ENDP:-0} endpoints, ${AORS:-0} AOR"
[ "${ENDP:-0}" -gt 0 ] && [ "${AORS:-0}" = "0" ] && echo "ATENCION: hay endpoints PJSIP pero ningun AOR: los telefonos no registraran. Revisa: grep -c 'Unable to set default' /var/log/asterisk/full"
asterisk -rx 'module show' | awk 'NR>1 && /\.so/{print $1}' | sort > "$BK/modulos-despues.txt"
echo "modulos cargados: $(wc -l < "$BK/modulos-despues.txt")   (antes: $(wc -l < "$BK/modulos-antes.txt"), version previa $ANTES)"
echo "--- modulos que estaban y ya no:"; comm -23 "$BK/modulos-antes.txt" "$BK/modulos-despues.txt" | head -20
echo "--- modulos nuevos:"; comm -13 "$BK/modulos-antes.txt" "$BK/modulos-despues.txt" | head -20
echo -n "chan_websocket: "; asterisk -rx 'module show like chan_websocket' | grep -c chan_websocket
echo "RESPALDO EN: $BK   (reversa: bash asterisk/99_revertir.sh $BK --si)"
exit $RC
