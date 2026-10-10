#!/bin/bash
# Instala lo necesario para COMPILAR Asterisk 20.18.0 como RPM en un Issabel 5 (Rocky Linux 8).
#   bash build/00_dependencias.sh
# Solo instala paquetes de desarrollo. No toca Asterisk ni Issabel. Ejecutar como root.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
SPEC="$(dirname "$0")/asterisk20.spec"

# dahdi-devel, iksemel-devel, libopenr2-devel y libtonezone-devel NO estan en Rocky: los trae el repositorio de Issabel
dnf repolist 2>/dev/null | grep -qi issabel || { echo "ABORTA: este servidor no tiene los repositorios de Issabel (hazlo en un Issabel 5 instalado)."; exit 1; }

echo "== Herramientas de empaquetado y compilacion =="
dnf -y install rpm-build dnf-plugins-core bzip2 patch wget cpio \
  gcc gcc-c++ make autoconf automake libtool bison flex

echo "== Repositorios que traen las librerias -devel (powertools y EPEL) =="
dnf -y install epel-release 2>&1 | tail -1
dnf config-manager --set-enabled powertools

echo "== Dependencias de compilacion que declara el spec =="
dnf -y builddep "$SPEC"

echo "== Librerias extra que el spec no declara pero que configure detecta =="
# Sin estas, Asterisk compila igual pero SIN esos modulos y el RPM falla por 'File not found'
dnf -y install libedit-devel openssl-devel newt-devel libcurl-devel libuuid-devel libxslt-devel \
  zlib-devel popt-devel bzip2-devel readline-devel binutils-devel uriparser-devel sqlite-devel \
  libsrtp-devel libogg-devel libvorbis-devel unixODBC-devel libical-devel \
  bluez-libs-devel lua-devel neon-devel speex-devel speexdsp-devel \
  codec2-devel unbound-devel freeradius-client-devel 2>&1 | tail -3
echo "Dependencias listas."
