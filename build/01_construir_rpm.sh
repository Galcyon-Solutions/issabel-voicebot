#!/bin/bash
# Construye los RPM de Asterisk 20.18.0 para Issabel 5 (Rocky 8), con los MISMOS parches que Issabel
# aplica a su Asterisk 20.12.0. Deja los RPM en ~/rpmbuild/RPMS/x86_64 y los copia a ./dist.
#   bash build/00_dependencias.sh && bash build/01_construir_rpm.sh
# Tarda entre 20 minutos (16 nucleos) y 90 minutos (2 nucleos). No toca el Asterisk instalado.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
HERE="$(cd "$(dirname "$0")" && pwd)"
VERSION=${VERSION:-20.18.0}      # otra version 20.x: VERSION=20.17.0 bash build/01_construir_rpm.sh (solo 20.18.0 esta probada)
BASE=https://downloads.asterisk.org/pub/telephony/asterisk/releases
SRPM_URL=http://repo.issabel.org/issabel/5/base/SRPMS/asterisk18-18.12.0-1.el8.src.rpm
TOP=${HOME}/rpmbuild
mkdir -p "$TOP"/{SOURCES,SPECS,BUILD,RPMS,SRPMS}

echo "== 1. Archivos de apoyo y parches de Issabel (salen del SRPM de su Asterisk 18) =="
# De ahi vienen: parche que desactiva 'inhibit escalations' de tcptls, parche del ping de WebSocket, el modulo
# res_speech_vosk con varios servidores, la unidad de systemd, logrotate y las confs de CDR/ODBC.
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
( cd "$W" && wget -q "$SRPM_URL" && rpm2cpio asterisk18-*.src.rpm | cpio -idm 2>/dev/null )
for f in asterisk-logrotate asterisk.service asterisk8.odbc.ini cdr.conf cdr_adaptive_odbc.conf cdr_sqlite3_custom.conf \
         disable.inhibit.tcptls.patch res_speech_vosk.c.multiserver_grammar websocket.diff; do
  cp -f "$W/$f" "$TOP/SOURCES/$f"
done

echo "== 2. Codigo fuente oficial de Asterisk $VERSION (con verificacion de hash) =="
cd "$TOP/SOURCES"
[ -f asterisk-$VERSION.tar.gz ] || wget -q "$BASE/asterisk-$VERSION.tar.gz"
# El hash sale del archivo .sha256 que publica Asterisk junto al codigo (20.18.0: 277d3fbf...a39d)
wget -q -O - "$BASE/asterisk-$VERSION.sha256" | grep -q "$(sha256sum asterisk-$VERSION.tar.gz | cut -d" " -f1)" && echo "asterisk-$VERSION.tar.gz: hash OK" || { echo "ABORTA: el hash no coincide con el publicado por Asterisk"; exit 1; }

echo "== 3. Spec y compilacion =="
sed "s/^Version: .*/Version: $VERSION/" "$HERE/asterisk20.spec" > "$TOP/SPECS/asterisk20.spec"
rm -rf "$TOP/BUILD/asterisk-$VERSION" "$TOP/BUILDROOT"
cd "$TOP"
rpmbuild -bb SPECS/asterisk20.spec 2>&1 | tee "$TOP/build-asterisk-$VERSION.log" | grep -E "^(Wrote:|error|Error)" || true
ls RPMS/x86_64/asterisk20-core-$VERSION-*.rpm >/dev/null

echo "== 4. Copia a ./dist =="
mkdir -p "$HERE/../dist"
cp -f RPMS/x86_64/asterisk20*-$VERSION-*.rpm "$HERE/../dist/"
( cd "$HERE/../dist" && sha256sum *.rpm > SHA256SUMS )
echo "Listo: $(ls "$HERE"/../dist/*.rpm | wc -l) RPM en dist/. Siguiente: bash asterisk/02_actualizar.sh dist"
