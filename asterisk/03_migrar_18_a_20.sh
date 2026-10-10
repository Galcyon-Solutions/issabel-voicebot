#!/bin/bash
# Migra un Issabel 5 con Asterisk 18 (paquetes asterisk18-*) a Asterisk 20.18.0 (paquetes asterisk20-*).
#   bash asterisk/03_migrar_18_a_20.sh <carpeta-con-los-RPM> --si
# Los paquetes asterisk18 y asterisk20 se pisan archivos entre si (/usr/sbin/asterisk, los .h, los modulos),
# asi que primero se quitan los asterisk18 (solo ellos, con rpm -e --nodeps para NO arrastrar a Issabel) y luego
# se instalan los asterisk20. Aborta si hay llamadas activas. Hace respaldo completo antes.
# Reversa: bash asterisk/99_revertir_a_18.sh <carpeta-de-respaldo> --si
set -uo pipefail
RPMDIR="${1:-}"; [ "${2:-}" = "--si" ] || { echo "Uso: $0 <carpeta-con-los-RPM> --si"; exit 1; }
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
ls "$RPMDIR"/asterisk20-20.18.0-*.rpm >/dev/null 2>&1 || { echo "ABORTA: no hay RPM 20.18.0 en $RPMDIR"; exit 1; }
rpm -q asterisk18 >/dev/null 2>&1 || { echo "ABORTA: no hay asterisk18 instalado. Si ya tienes Asterisk 20 usa asterisk/02_actualizar.sh"; exit 1; }
n=$(asterisk -rx 'core show channels count' | awk '/active channel/{print $1}')
[ "${n:-0}" = "0" ] || { echo "ABORTA: hay $n canal(es) activo(s)"; exit 1; }

BK=/root/respaldo-migracion18-$(date +%Y%m%d-%H%M%S); install -d -m 700 "$BK"
echo "== Respaldo en $BK =="
asterisk -rx 'module show' | awk 'NR>1 && /\.so/{print $1}' | sort > "$BK/modulos-antes.txt"
rpm -qa 'asterisk18*' | sort > "$BK/paquetes.txt"
tar -C / -cpf "$BK/config.tar" etc/asterisk etc/sysconfig/asterisk 2>/dev/null
tar -C / -cpf "$BK/binarios.tar" usr/sbin/asterisk usr/lib64/asterisk var/lib/asterisk/agi-bin 2>/dev/null
MYSQL_PWD=$(awk -F= '/^mysqlrootpwd/{print $2}' /etc/issabel.conf) mysqldump -uroot --single-transaction asterisk > "$BK/asterisk.sql" 2>/dev/null && chmod 600 "$BK/asterisk.sql"
echo "modulos cargados: $(wc -l < "$BK/modulos-antes.txt")  respaldo: $(du -sh "$BK" | cut -f1)"

# Mismo conjunto de paquetes, con nombre asterisk20 (mas sqlite3, que forma parte del conjunto de Issabel con Asterisk 20)
NUEVOS=$( { sed -E 's/^asterisk18/asterisk20/; s/-18\.[0-9]+\.[0-9]+-[0-9]+\.el8\.x86_64$//' "$BK/paquetes.txt"; echo asterisk20-sqlite3; } | sort -u | while read -r p; do ls "$RPMDIR/$p"-20.18.0-*.rpm 2>/dev/null | head -1; done)
echo "Se instalaran:"; echo "$NUEVOS" | sed 's#.*/##'
rpm -q epel-release >/dev/null 2>&1 || dnf -y install epel-release 2>&1 | tail -1
# Se bajan ANTES las dependencias externas (freeradius-client, codec2...) para no dejar el servidor sin Asterisk si
# alguna no aparece cuando ya se quito el viejo. (dnf no puede simular el paquete completo: asterisk18 y asterisk20 chocan.)
DEPS=$(rpm -qp --requires $NUEVOS 2>/dev/null | awk '{print $1}' | grep -vE '^(rpmlib|config|/|asterisk20|libasteriskpj|libasteriskssl)' | sort -u)
echo "-- dependencias externas:"; echo $DEPS | fold -w 120; echo
if ! dnf -y install --downloadonly $DEPS 2>&1 | tee "$BK/dependencias.log" | tail -3 | grep -q .; then :; fi
if grep -qiE "no match|no se encontr|unable to find|nothing provides" "$BK/dependencias.log"; then
  echo "ABORTA: falta alguna dependencia en los repositorios (nada se ha tocado todavia):"; grep -iE "no match|no se encontr|unable to find|nothing provides" "$BK/dependencias.log" | head -5; exit 1
fi

echo "== Quitando asterisk18 e instalando asterisk20 =="
systemctl stop asterisk 2>&1 | tail -1
rpm -e --nodeps $(rpm -qa 'asterisk18*') 2>&1 | tail -5
dnf -y install $NUEVOS 2>&1 | tail -25
RC=${PIPESTATUS[0]}
# Con coma decimal en el sistema (es_PE, es_ES...) Asterisk 20 no entiende "3.0" (qualify_timeout) y NO crea los AOR de
# PJSIP: ningun telefono registra. Se le pide que lea los numeros con punto (LC_NUMERIC=C) con un drop-in de systemd.
if [ "$(locale decimal_point 2>/dev/null)" != "." ]; then
  install -d /etc/systemd/system/asterisk.service.d
  printf '[Service]
Environment=LC_NUMERIC=C
' > /etc/systemd/system/asterisk.service.d/locale.conf
  echo "Locale con coma decimal: se agrego /etc/systemd/system/asterisk.service.d/locale.conf (LC_NUMERIC=C)"
fi
# El RPM viejo deja sus .conf modificados como .rpmsave; el nuevo respeta los *.conf que ya existen
echo "== Arrancando =="
systemctl daemon-reload; systemctl restart asterisk; sleep 15
asterisk -rx 'core show version'
EJEC=$(asterisk -rx 'core show version' | awk '{print $2}'); INST=$(rpm -q asterisk20 --qf '%{VERSION}')
[ "$EJEC" = "$INST" ] && echo "OK: ejecutando $EJEC (igual al paquete instalado)" || echo "ATENCION: ejecutando $EJEC pero instalado $INST. Reinicia: systemctl restart asterisk"
AORS=$(asterisk -rx 'pjsip show aors' 2>/dev/null | awk '/Objects found/{print $3}'); ENDP=$(asterisk -rx 'pjsip show endpoints' 2>/dev/null | grep -c 'Endpoint: ')
echo "PJSIP: ${ENDP:-0} endpoints, ${AORS:-0} AOR"
[ "${ENDP:-0}" -gt 0 ] && [ "${AORS:-0}" = "0" ] && echo "ATENCION: hay endpoints PJSIP pero ningun AOR: los telefonos no registraran. Revisa: grep -c 'Unable to set default' /var/log/asterisk/full"
asterisk -rx 'module show' | awk 'NR>1 && /\.so/{print $1}' | sort > "$BK/modulos-despues.txt"
# El modules.conf del paquete nuevo trae "noload" para chan_sip y res_hep*. Si estaban cargados antes y el modulo
# existe en disco, se restaura el comportamiento anterior (sin esto, las extensiones chan_sip dejan de registrar).
for m in $(comm -23 "$BK/modulos-antes.txt" "$BK/modulos-despues.txt"); do
  if [ -f "/usr/lib64/asterisk/modules/$m" ] && grep -qE "^noload *= *$m" /etc/asterisk/modules.conf; then
    sed -i -E "s/^(noload *= *$m)/;\1   ; comentado por la migracion 18 a 20 (estaba cargado en Asterisk 18)/" /etc/asterisk/modules.conf
    asterisk -rx "module load $m" | tail -1
    echo "restaurado: $m"
  fi
done
asterisk -rx 'module show' | awk 'NR>1 && /\.so/{print $1}' | sort > "$BK/modulos-despues.txt"
echo "modulos cargados: $(wc -l < "$BK/modulos-despues.txt")   (antes: $(wc -l < "$BK/modulos-antes.txt"))"
echo "--- modulos que estaban y ya no:"; comm -23 "$BK/modulos-antes.txt" "$BK/modulos-despues.txt" | head -30
echo "--- modulos nuevos:"; comm -13 "$BK/modulos-antes.txt" "$BK/modulos-despues.txt" | head -30
echo -n "chan_websocket: "; asterisk -rx 'module show like chan_websocket' | grep -c chan_websocket
echo "--- configuracion que Asterisk 20 rechaza (revisa si sale algo):"
grep -E "ERROR|WARNING" /var/log/asterisk/full 2>/dev/null | tail -n 400 | grep -vE "declined to load|rpmsave" | tail -8 | cut -c1-200
echo "RESPALDO EN: $BK   (reversa: bash asterisk/99_revertir_a_18.sh $BK --si)"
exit $RC
