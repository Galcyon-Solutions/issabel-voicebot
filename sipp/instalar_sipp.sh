#!/bin/bash
# Compila SIPp 3.7.9 desde el codigo oficial en Rocky Linux 8 (o el mismo Issabel). SIPp no esta en los repositorios.
#   bash sipp/instalar_sipp.sh        (como root; deja /usr/local/bin/sipp)
# En Debian o Ubuntu: apt install build-essential cmake libncurses-dev libssl-dev libpcap-dev libgsl-dev y los mismos pasos de cmake.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "Ejecuta como root."; exit 1; }
VERSION=3.7.9
dnf -y --enablerepo=powertools install gcc-c++ cmake make ncurses-devel openssl-devel libpcap-devel gsl-devel wget tar
cd /usr/src
[ -f sipp-$VERSION.tar.gz ] || wget -q "https://github.com/SIPp/sipp/releases/download/v$VERSION/sipp-$VERSION.tar.gz"
tar xzf sipp-$VERSION.tar.gz
cd sipp-$VERSION
cmake . -DUSE_PCAP=1 -DUSE_SSL=1 -DUSE_GSL=1
make -j"$(nproc)"
install -m 755 sipp /usr/local/bin/sipp
sipp -v | head -3
