%global debug_package %{nil}
%define _without_misdn 1
%define astapi 20
#%define docdir /usr/share/doc/asterisk
%define logdir /var/log
%undefine __brp_mangle_shebangs
Summary: Asterisk, The Open Source PBX
Name: asterisk20
Version: 20.18.0
Release: 1%{?rcver:.rc%{rcver}}%{?betaver:.beta%{betaver}}%{?debugthreads:.debugthreads}%{?dist}
License: GPL
Group: Utilities/System
Source: asterisk-%{version}.tar.gz
Source2: asterisk-logrotate
Source3: asterisk8.odbc.ini
Source4: cdr_adaptive_odbc.conf
Source5: cdr.conf
Source6: cdr_sqlite3_custom.conf 
Source7: asterisk.service
Source8: res_speech_vosk.c.multiserver_grammar

Patch0: disable.inhibit.tcptls.patch
#Patch1: disable-broken-pjsip-verify.patch
#Patch2: asterisk-13.22.disable-tty-console.patch
#Patch6: lazymembers.patch
#Patch8: ASTERISK-rb3984.patch
Patch9: websocket.diff
BuildRoot: %{_tmppath}/asterisk-%{version}-root
URL: http://www.asterisk.org
Vendor: Digium, Inc.
Packager: Issabel Dev Team <devs@issabel.org>
##Provides and Obsoletes
Provides: asterisk
Provides: asterisk18
Conflicts: asterisk11
Conflicts: asterisk13
Conflicts: asterisk16
Conflicts: asterisk = 2009020507:11.25.0-0.el7.centos
##
BuildRequires: subversion
Requires: lua
BuildRequires: lua-devel
Requires: iksemel
BuildRequires: iksemel-devel
Requires: portaudio
BuildRequires: portaudio-devel
Requires: neon
BuildRequires: neon-devel
Requires: libxml2
BuildRequires: libxml2-devel
Requires: spandsp
BuildRequires: spandsp-devel
Requires: libical
BuildRequires: libical-devel
Requires: libsrtp
BuildRequires: libsrtp-devel
Requires: freeradius
#Requires: radiusclient-ng
#BuildRequires: radiusclient-ng-devel
Requires: jack-audio-connection-kit
BuildRequires: jack-audio-connection-kit-devel
Requires: libresample
BuildRequires: libresample-devel
Requires: openldap
BuildRequires: openldap-devel
Requires: sqlite
BuildRequires: sqlite-devel
Requires: unixODBC
BuildRequires: unixODBC-devel
Requires: libtool-ltdl
BuildRequires: libtool-ltdl-devel
BuildRequires: xmlstarlet
BuildRequires: bash
BuildRequires: gmime-devel
%{?_without_optimizations:Requires: %{name}-debuginfo = %{version}-%{release}}
Requires: %{name}-core = %{version}-%{release}
%{!?_without_dahdi:Requires: %{name}-dahdi = %{version}-%{release}}
Requires: %{name}-doc = %{version}-%{release}
Requires: %{name}-voicemail = %{version}-%{release}
Requires: %{name}-addons = %{version}-%{release}
Requires: %{name}-configs = %{version}-%{release}
Requires: %{name}-resample = %{version}-%{release}
Requires: %{name}-odbc = %{version}-%{release}
Requires: asterisk-sounds-en-gsm
BuildRequires: ncurses-devel
BuildRequires: libxml2-devel
BuildRequires: libuuid-devel
BuildRequires: jansson-devel
%{!?_without_newt:BuildRequires: newt-devel}
BuildConflicts: rh-postgresql-devel

%description
Asterisk is an open source PBX and telephony development platform.  Asterisk
can both replace a conventional PBX and act as a platform for the
development of custom telephony applications for the delivery of dynamic
content over a telephone; similar to how one can deliver dynamic content
through a web browser using CGI and a web server.

Asterisk supports a variety of telephony hardware including BRI, PRI, POTS,
and IP telephony clients using the Inter-Asterisk eXchange (IAX) protocol (e.g.
gnophone or miniphone).  For more information and a current list of supported
hardware, see http://www.asterisk.org

#
#  core subpackage
#
%package core
Summary: Asterisk core package without any "extras".
Group: Utilities/System
#Provides: asterisk-core
#Provides: asterisk%{astapi}-core
		
	
Requires: libxml2
Requires: %{name} = %{version}-%{release}

%description core
This package contains a base install of Asterisk without any "extras".

#
#  Alsa subpackage
#
%{?_without_alsa:%if 0}
%{!?_without_alsa:%if 1}
%package alsa
Summary: Alsa channel driver for Asterisk
Group: Utilities/System
#Provides: asterisk-alsa		
#Provides: asterisk%{astapi}-alsa

%if "%{distname}" == "suse" || "%{distname}" == "sles"
BuildRequires: alsa-devel
Requires: alsa
%else
BuildRequires: alsa-lib-devel
Requires: alsa-lib
%endif
Requires: %{name}-core = %{version}-%{release}

%description alsa
Alsa channel driver for Asterisk
%endif




#
# prometheus
#
%package prometheus
Summary: prometheus  resource module for Asterisk
Group: Utilities/System		

%description prometheus
prometheus resource module for Asterisk

%files prometheus 
%defattr(-, root, root)
%{_libdir}/asterisk/modules/res_prometheus.so
%{_includedir}/asterisk/res_prometheus.h





#
# audiosocket
#
%package audiosocket
Summary: audiosocket channel driver and resource module for Asterisk
Group: Utilities/System
Requires: %{name}-core = %{version}-%{release}

%description audiosocket
audiosocket channel driver and resource module for Asterisk

%files audiosocket 
%defattr(-, root, root)
%{_libdir}/asterisk/modules/app_audiosocket.so
%{_libdir}/asterisk/modules/chan_audiosocket.so
%{_libdir}/asterisk/modules/res_audiosocket.so
%{_includedir}/asterisk/res_audiosocket.h


#
#  snmp subpackage
#
%{?_without_snmp:%if 0}
%{!?_without_snmp:%if 1}
%package snmp
Summary: snmp resource module for Asterisk
Group: Utilities/System		
#Provides: asterisk-snmp
#Provides: asterisk%{astapi}-snmp
%if "%{distname}" == "suse" || "%{distname}" == "sles"
BuildRequires: sensors
BuildRequires: tcpd-devel
%else
BuildRequires: lm_sensors-devel
%endif
BuildRequires: net-snmp-devel
Requires: net-snmp
Requires: %{name}-core = %{version}-%{release}

%description snmp
snmp resource module for Asterisk
%endif

#
#  pgsql subpackage
#
%{?_without_pgsql:%if 0}
%{!?_without_pgsql:%if 1}
%package pgsql
Summary: Postgresql modules for Asterisk
Group: Utilities/System
#Provides: asterisk-pgsql		
#Provides: asterisk%{astapi}-pgsql
BuildRequires: postgresql-devel
Requires: postgresql
Requires: %{name}-core = %{version}-%{release}

%description pgsql
Postgresql modules for Asterisk
%endif

#
#  tds subpackage
#
%{?_without_tds:%if 0}
%{!?_without_tds:%if 1}
%package tds
Summary: tds modules for Asterisk
Group: Utilities/System
#Provides: asterisk-tds	
#Provides: asterisk%{astapi}-tds
BuildRequires: freetds-devel
Requires: freetds
Requires: %{name}-core = %{version}-%{release}

%description tds
tds modules for Asterisk
%endif

#
#  dahdi subpackage
#
%{?_without_dahdi:%if 0}
%{!?_without_dahdi:%if 1}
%package dahdi
Summary: DAHDI channel driver for Asterisk
Group: Utilities/System
#Provides: asterisk-dahdi
#Provides: asterisk%{astapi}-dahdi
Requires: %{name}-core = %{version}-%{release}
BuildRequires: libopenr2-devel
BuildRequires: libpri-devel
BuildRequires: libss7-devel
BuildRequires: libtonezone-devel
BuildRequires: dahdi-devel
Requires: libopenr2
Requires: libpri
Requires: libss7
Requires: libtonezone
Requires: dahdi-linux
AutoReqProv: no	

%description dahdi
DAHDI channel driver for Asterisk
%endif

#
#  mISDN subpackage
#
%{?_without_misdn:%if 0}
%{!?_without_misdn:%if 1}
%package misdn
Summary: mISDN channel driver for Asterisk
Group: Utilities/System
#Provides: asterisk%{astapi}-misdn
Requires: %{name}-core = %{version}-%{release}
BuildRequires: mISDNuser-devel
BuildRequires: mISDN-devel
Requires: mISDNuser
Requires: mISDN
Requires: mISDN-kmod
AutoReqProv: no

%description misdn
mISDN channel driver for Asterisk
%endif

#
#  Configs subpackage
#
%package configs
Summary: Basic configuration files for Asterisk
Group: Utilities/System
#Provides: asterisk%{astapi}-configs
Requires: %{name}-core = %{version}-%{release}

%description configs
The sample configuration files for Asterisk

#
#  cURL subpackage
#
%{?_without_curl:%if 0}
%{!?_without_curl:%if 1}
%package curl
Summary: cURL application module for Asterisk
Group: Utilities/System	
#Provides: asterisk%{astapi}-curl
BuildRequires: curl-devel
Requires: curl
Requires: %{name}-core = %{version}-%{release}

%description curl
cURL application module for Asterisk
%endif

#
#  Development subpackage
#
%package devel
Summary: Static libraries and header files for Asterisk development
Group: Development/Libraries
#Provides: asterisk%{astapi}-devel
Requires: %{name}-core = %{version}-%{release}

%description devel
The static libraries and header files needed for building additional Asterisk
plugins/modules

#
#  Documentation subpackage
#
%package doc
Summary: Documentation files for Asterisk
Group: Development/Libraries
#Provides: asterisk%{astapi}-doc
Requires: %{name}-core = %{version}-%{release}

%description doc
The Documentation files for Asterisk

#
#  Ogg-Vorbis subpackage
#
%{?_without_ogg:%if 0}
%{!?_without_ogg:%if 1}
%package ogg
Summary: Ogg-Vorbis codec module for Asterisk
Group: Utilities/System	
#Provides: asterisk%{astapi}-ogg
BuildRequires: libvorbis-devel libogg-devel
Requires: libvorbis libogg
Requires: %{name}-core = %{version}-%{release}

%description ogg
Asterisk format plugin for the Ogg-Vorbis codec
%endif

#
#  Speex subpackage
#
%{?_without_speex:%if 0}
%{!?_without_speex:%if 1}
%package speex
Summary: Speex codec module for Asterisk
Group: Utilities/System		
#Provides: asterisk%{astapi}-speex
BuildRequires: speex-devel
BuildRequires: speexdsp speexdsp-devel
Requires: speex
Requires: %{name}-core = %{version}-%{release}

%description speex
Asterisk format plugin for the Speex codec
%endif

#
#  resample subpackage
#
%{?_without_resample:%if 0}
%{!?_without_resample:%if 1}
%package resample
Summary: resampling codec module for Asterisk
Group: Utilities/System		
#Provides: asterisk%{astapi}-resample
BuildRequires: libresample-devel
Requires: libresample
Requires: %{name}-core = %{version}-%{release}

%description resample
Asterisk plugin for the resample codec
%endif

#
#  unixODBC subpackage
#
%{?_without_odbc:%if 0}
%{!?_without_odbc:%if 1}
%package odbc
Summary: Open Database Connectivity (ODBC) drivers for Asterisk
Group: Utilities/System
#Provides: asterisk%{astapi}-odbc
BuildRequires: unixODBC-devel
Requires: unixODBC
Requires: mariadb-connector-odbc >= 3.1.12
Requires: %{name}-core = %{version}-%{release}

%description odbc
ODBC drivers for Asterisk
%endif

#
#  sqlite3 subpackage
#
%{?_without_sqlite3:%if 0}
%{!?_without_sqlite3:%if 1}
%package sqlite3
Summary: sqlite3 drivers for Asterisk
Group: Utilities/System	
#Provides: asterisk%{astapi}-sqlite3
BuildRequires: sqlite-devel
Requires: sqlite
Requires: %{name}-core = %{version}-%{release}

%description sqlite3
sqlite3 drivers for Asterisk
%endif

#
#  voicemail file storage subpackage
#
%package voicemail
Summary: Voicemail with file storage module for Asterisk
Group: Utilities/System
#Provides: asterisk-voicemail = %{version}-%{release}
#Provides: asterisk%{astapi}-voicemail
#Provides: asterisk-voicemail-filestorage = %{version}-%{release}
#Provides: asterisk%{astapi}-voicemail-filestorage


Requires: %{name}-core = %{version}-%{release}
#Provides: %{name}-voicemail-filestorage = %{version}-%{release}
Conflicts: %{name}-voicemail-odbcstorage
Conflicts: %{name}-voicemail-imapstorage

%description voicemail
Voicemail with file storage module for Asterisk

#
#  voicemail ODBC storage subpackage
#
%{?_without_voicemail_odbcstorage:%if 0}
%{!?_without_voicemail_odbcstorage:%if 1}
%package voicemail-odbcstorage
Summary: Voicemail with ODBC storage module for Asterisk
Group: Utilities/System
#Provides: asterisk-voicemail-odbcstorage = %{version}-%{release}
#Provides: asterisk%{astapi}-voicemail-odbcstorage
BuildRequires: unixODBC-devel
Requires: unixODBC
Requires: %{name}-core = %{version}-%{release}
#Provides: %{name}-voicemail = %{version}-%{release}
Conflicts: %{name}-voicemail-filestorage
Conflicts: %{name}-voicemail-imapstorage

%description voicemail-odbcstorage
Voicemail with ODBC storage module for Asterisk
%endif

#
#  voicemail IMAP storage subpackage
#
%{?_without_voicemail_imapstorage:%if 0}
%{!?_without_voicemail_imapstorage:%if 1}
%package voicemail-imapstorage
Summary: Voicemail with IMAP storage module for Asterisk
Group: Utilities/System
	

%if "%{distname}" == "suse" || "%{distname}" == "sles"
BuildRequires: imap-devel
Requires: imap-lib
%else
BuildRequires: libc-client-devel
Requires: libc-client
%endif
Requires: %{name}-core = %{version}-%{release}
#Provides: %{name}-voicemail = %{version}-%{release}




Conflicts: %{name}-voicemail-filestorage
Conflicts: %{name}-voicemail-odbcstorage

%description voicemail-imapstorage
Voicemail with IMAP storage module for Asterisk
%endif

#
#  addons subpackage
#
%package addons
Summary: Asterisk-addons package.
Group: Utilities/System
Requires: asterisk%{astapi}-addons-core = %{version}-%{release}
#Provides: asterisk-addons
#Provides: asterisk%{astapi}-addons

Requires: %{name}-addons-core = %{version}-%{release}
Requires: %{name}-core = %{version}-%{release}	

%{?_without_mysql:%if 0}
%{!?_without_mysql:%if 1}
Requires: %{name}-addons-mysql = %{version}-%{release}
Requires: mariadb
%endif

%{?_without_bluetooth:%if 0}
%{!?_without_bluetooth:%if 1}
Requires: %{name}-addons-bluetooth = %{version}-%{release}
Requires: bluez-libs
Requires: %{name}-core = %{version}-%{release}		
%endif

%{?_without_ooh323:%if 0}
%{!?_without_ooh323:%if 1}
Requires: %{name}-addons-ooh323 = %{version}-%{release}
Requires: %{name}-core = %{version}-%{release}	
%endif

%description addons
This package contains a base install of Asterisk-addons without any "extras".

#
#  addons-core subpackage
#
%package addons-core
Summary: Asterisk-addons core package.
Group: Utilities/System
#Provides: asterisk-gplonly
Requires: asterisk%{astapi}-core = %{version}-%{release}
#Provides: asterisk-addons-core
#Provides: asterisk%{astapi}-addons-core
Requires: %{name}-core = %{version}-%{release}		

%description addons-core
This package contains a base install of Asterisk-addons without any "extras".

#
#  addons-mysql subpackage
#
%{?_without_mysql:%if 0}
%{!?_without_mysql:%if 1}
%package addons-mysql
Summary: mysql modules for Asterisk
Group: Utilities/System
BuildRequires: mariadb-devel
Requires: mariadb
Requires: %{name}-addons-core = %{version}-%{release}
#Provides: asterisk-addons-mysql
#Provides: asterisk%{astapi}-addons-mysql
Requires: %{name}-core = %{version}-%{release}		

%description addons-mysql
mysql modules for Asterisk
%endif

#
#  bluetooth subpackage
#
%{?_without_bluetooth:%if 0}
%{!?_without_bluetooth:%if 1}
%package addons-bluetooth
Summary: bluetooth modules for Asterisk
Group: Utilities/System
BuildRequires: bluez-libs-devel
Requires: bluez-libs
Requires: %{name}-core = %{version}-%{release}
#Provides: asterisk-addons-bluetooth
#Provides: asterisk%{astapi}-addons-bluetooth

%description addons-bluetooth
bluetooth modules for Asterisk
%endif

#
#  ooh323 subpackage
#
%{?_without_ooh323:%if 0}
%{!?_without_ooh323:%if 1}
%package addons-ooh323
Summary: chan_ooh323 module for Asterisk
Group: Utilities/System
Requires: %{name}-core = %{version}-%{release}
#Provides: asterisk-addons-ooh323
#Provides: asterisk%{astapi}-addons-ooh323

%description addons-ooh323
chan_ooh323 module for Asterisk
%endif


###################################################################
#
#  The Prep Section
#  If stuff needs to be done before building, this is the section
#  Use shell scripts to do stuff like uncompress and cd into source dir
#  %setup macro - cleans old build trees, uncompress and extracts original source
#
###################################################################
%prep
%setup -n asterisk-%{version}
cp %{SOURCE8} res/res_speech_vosk.c

#cp %{SOURCE12} res/
#cp %{SOURCE13} res/
#cp %{SOURCE9} apps/
#cp %{SOURCE10} channels/
#cp %{SOURCE11} include/asterisk/

%patch0 -p0
%patch9 -p0

#%patch8 -p0		
#%patch2 -p1

###################################################################
#
#  The Build Section
#  Use shell scripts and do stuff that makes the build happen, i.e. make
#
###################################################################
%build
%ifarch x86_64
%define makeflags OPT=-fPIC
%else
%define makeflags OPT=
%endif
echo %{version}%{?_without_optimizations:-debug} > .version

./configure --libdir=%{_libdir} --with-pjproject-bundled --with-jansson-bundled
make menuselect.makeopts
#menuselect/menuselect --list-options to get the options passed below
#menuselect/menuselect --disable-category MENUSELECT_CORE_SOUNDS --disable-category MENUSELECT_EXTRA_SOUNDS --disable-category MENUSELECT_MOH --enable-category MENUSELECT_ADDONS --enable res_pktccops --enable chan_sip --enable res_monitor --enable chan_skinny --enable chan_mgcp --enable chan_motif --enable app_macro --enable app_meetme --enable app_page --enable res_snmp --enable res_srtp --enable DONT_OPTIMIZE --disable BUILD_NATIVE --enable res_statsd --enable res_chan_stats --enable res_endpoint_stats --enable codec_opus --enable codec_silk --enable codec_siren7 --enable codec_siren14 --enable res_fax_spandsp --enable HAVE_SYSTEMD menuselect.makeopts
menuselect/menuselect --disable-category MENUSELECT_CORE_SOUNDS --disable-category MENUSELECT_EXTRA_SOUNDS --disable-category MENUSELECT_MOH --enable-category MENUSELECT_ADDONS --enable res_pktccops --enable chan_sip --enable res_monitor --enable chan_skinny --enable chan_alsa --enable chan_mgcp --enable chan_motif --enable app_macro --enable app_meetme --enable app_page --enable res_snmp --enable res_srtp --enable DONT_OPTIMIZE --disable BUILD_NATIVE --enable res_statsd --enable res_chan_stats --enable res_endpoint_stats --enable codec_opus --enable codec_silk --enable codec_siren7 --enable codec_siren14 --enable res_fax_spandsp menuselect.makeopts

contrib/scripts/get_mp3_source.sh

make -j$(nproc) %{makeflags}


###################################################################
#
#  The Install Section
#  Use shell scripts and perform the install, like 'make install',
#  but can also be shell commands, i.e. cp, mv, install, etc..
#
###################################################################
%install
echo DEBUG
pwd

mkdir -p $RPM_BUILD_ROOT/home/asterisk/	  		
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/system/
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/
echo "AST_USER=asterisk" > $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/asterisk
echo "AST_GROUP=asterisk" >> $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/asterisk
echo "AST_GROUP=asterisk" >> $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/asterisk
echo "COREDUMP=yes" >> $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/asterisk
echo "COLOR=yes" >> $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/asterisk

make DESTDIR=$RPM_BUILD_ROOT install
make DESTDIR=$RPM_BUILD_ROOT samples
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
make DESTDIR=$RPM_BUILD_ROOT config
rm -rf $RPM_BUILD_ROOT/etc/rc.d
make DESTDIR=$RPM_BUILD_ROOT install-headers

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/
cp %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/asterisk
echo -e "#This comment is to fix rpm file replacing\n#Config file built on $(date)" >> $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/asterisk	
##ODBC config template
cp %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/asterisk8.odbc.ini
#Replace default cdr_odbc.conf and cdr.conf files
rm $RPM_BUILD_ROOT%{_sysconfdir}/asterisk/cdr_adaptive_odbc.conf
cp %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/asterisk/cdr_adaptive_odbc.conf
rm $RPM_BUILD_ROOT%{_sysconfdir}/asterisk/cdr.conf
cp %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/asterisk/cdr.conf
#GV 16.5.1
rm $RPM_BUILD_ROOT%{_sysconfdir}/asterisk/cdr_sqlite3_custom.conf
cp %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/asterisk/cdr_sqlite3_custom.conf

#NG 16.16
#cp %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/asterisk/res-speech-vosk.conf

cp %{SOURCE7} $RPM_BUILD_ROOT/usr/lib/systemd/system/asterisk.service 

mkdir -p $RPM_BUILD_ROOT/var/lib/asterisk/licenses/
mkdir -p $RPM_BUILD_ROOT/var/lib/digium/licenses/

	
#Added by JP rename the new config files to prevent them to be overwritten
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/enum.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/enum.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/extensions.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/extensions.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/features.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/features.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/http.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/http.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/iax.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/iax.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/indications.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/indications.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/logger.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/logger.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/manager.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/manager.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/meetme.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/meetme.confnew
#mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/modules.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/modules.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/motif.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/motif.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/phone.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/phone.confnew || true
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/res_fax.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/res_fax.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/res_odbc.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/res_odbc.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/sip.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/sip.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/sip_notify.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/sip_notify.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/udptl.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/udptl.confnew
mv $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/xmpp.conf $RPM_BUILD_ROOT/%{_sysconfdir}/asterisk/xmpp.confnew
#Added by JP move opus config file from third-party to documentation
mv $RPM_BUILD_ROOT/var/lib/asterisk/documentation/thirdparty/codec_opus_config-en_US.xml $RPM_BUILD_ROOT/var/lib/asterisk/documentation/codec_opus_config-en_US.xml
###################################################################
#
#  Install and Uninstall
#  This section can have scripts that are run either before/after
#  an install process, or before/after an uninstall process
#  %pre - executes prior to the installation of a package
#  %post - executes after the package is installed
#  %preun - executes prior to the uninstallation of a package
#  %postun - executes after the uninstallation of a package
#
###################################################################
%pre core
# Some distros may already ship with an existing asterisk group. Create it here
# if the group does not yet exist (with the -f flag).
/usr/sbin/groupadd -f -r asterisk

# At this point the asterisk group must already exist
if ! grep -q asterisk: /etc/passwd ; then
    echo -e "Adding new user asterisk..."
    /usr/sbin/useradd -r -g asterisk -c "Asterisk PBX" -s /bin/bash -d /var/lib/asterisk asterisk
fi

%post core
#/sbin/chkconfig --add asterisk
systemctl enable asterisk

# to avoid backup failures 
mkdir -p /var/spool/asterisk/monitor
chown asterisk.asterisk /var/spool/asterisk/monitor

if [ ! -d %{logdir}/asterisk ]; then
mkdir %{logdir}/asterisk
chown asterisk.asterisk %{logdir}/asterisk
fi

if [ ! -d %{logdir}/asterisk/cdr-csv ]; then
mkdir %{logdir}/asterisk/cdr-csv
chown asterisk.asterisk %{logdir}/asterisk/cdr-csv
fi

if [ ! -d %{logdir}/asterisk/cdr-custom ]; then
mkdir %{logdir}/asterisk/cdr-custom
chown asterisk.asterisk %{logdir}/asterisk/cdr-custom
fi

%post configs
if ! grep 'noload => cdr_mysql.so' /etc/asterisk/modules_custom.conf ; then
#Remove cdr_mysql as default to use ODBC
echo "noload => cdr_mysql.so" >> /etc/asterisk/modules_custom.conf
chown asterisk:asterisk /etc/asterisk/modules_custom.conf
fi

%postun configs
sed -i '/^noload => cdr_mysql.so/d' /etc/asterisk/modules_custom.conf

%post
#Mod by Asternic - Use trigger to prevent the configuration files to be deleted after asterisk is uninstalled		
#/sbin/chkconfig --add asterisk
systemctl enable asterisk

for A in /etc/asterisk/*.rpmsave; do
[ -e "$A" ] || continue
B=${A%.rpmsave}
echo $B >>/tmp/rpm2.log
if [ ! -f $B ]; then
mv -f $A $B
fi
done
#Remove cdr_mysql as default to use ODBC
echo "noload => cdr_mysql.so" > /etc/asterisk/modules_additional.conf
chown asterisk:asterisk /etc/asterisk/modules_additional.conf
rm -f /tmp/rpm2.log
#Rename voicemail.conf files to keep them after reinstall or version switch
if [  -f /etc/asterisk/voicemail.conf.rpmsave ]; then
mv -f /etc/asterisk/voicemail.conf.rpmsave /etc/asterisk/voicemail.conf
chown asterisk.asterisk /etc/asterisk/voicemail.conf
fi
# Start asterisk
if [ ! -f /tmp/issabelinstall ]; then
echo "Restarting asterisk for changes...";
/sbin/service asterisk start
fi

#Mod by Asternic - Use postun script to prevent some of the configuration files to be replaced after uninstalling this package. This is needed for Asterisk version switch
%postun
for A in /etc/asterisk/*.rpmsave; do
[ -e "$A" ] || continue
B=${A%.rpmsave}
if [ ! -f $B  ]; then
mv -f $A $B
chown asterisk.asterisk $B
fi
done

#################################################################o#
#
#  Verify
#
###################################################################
%verifyscript

###################################################################
#
#  Clean
#
###################################################################
	

%clean
cd $RPM_BUILD_DIR
%{__rm} -rf asterisk-%{version}
%{__rm} -rf /var/log/%{name}-sources-%{version}-%{release}.make.err
%{__rm} -rf $RPM_BUILD_ROOT


###################################################################
#
#  File List
#
###################################################################
%files
%defattr(-, root, root)

%files core
#new modules in 20.16-20.18 (not in the 20.12 spec)
%{_libdir}/asterisk/modules/codec_codec2.so
%{_libdir}/asterisk/modules/res_resolver_unbound.so
%{_libdir}/asterisk/modules/app_broadcast.so
%{_libdir}/asterisk/modules/app_if.so
%{_libdir}/asterisk/modules/app_signal.so
%{_libdir}/asterisk/modules/chan_websocket.so
%{_libdir}/asterisk/modules/func_export.so
%{_libdir}/asterisk/modules/func_uuid.so
%{_libdir}/asterisk/modules/res_geolocation.so
%{_libdir}/asterisk/modules/res_pjsip_aoc.so
%{_libdir}/asterisk/modules/res_pjsip_geolocation.so
%{_libdir}/asterisk/modules/res_pjsip_rfc3329.so
%{_libdir}/asterisk/modules/res_websocket_client.so
%defattr(-, root, root)
/usr/lib/systemd/system/asterisk.service
%config %{_sysconfdir}/sysconfig/asterisk
%attr(0775,asterisk,asterisk) %dir %{_sysconfdir}/asterisk
%attr(0755,asterisk,asterisk) %dir /home/asterisk
%{_libdir}/asterisk/modules/app_adsiprog.so		
%{_libdir}/asterisk/modules/app_alarmreceiver.so
%{_libdir}/asterisk/modules/app_amd.so
#GV 16.5.1
%{_libdir}/asterisk/modules/app_attended_transfer.so
%{_libdir}/asterisk/modules/app_authenticate.so
#GV 16.5.1

#NG 16.16
#libjwt>=1.15.3 not available on EL8, not built: %{_libdir}/asterisk/modules/res_pjsip_stir_shaken.so
#libjwt>=1.15.3 not available on EL8, not built: %{_libdir}/asterisk/modules/res_stir_shaken.so
%{_libdir}/asterisk/modules/res_speech_vosk.so

#NG 16.20
%{_libdir}/asterisk/modules/app_dtmfstore.so
%{_libdir}/asterisk/modules/app_reload.so
%{_libdir}/asterisk/modules/app_waitforcond.so
#NG 16.20

#GV 18.12
%{_libdir}/asterisk/modules/app_mf.so
%{_libdir}/asterisk/modules/app_sf.so
%{_libdir}/asterisk/modules/func_evalexten.so
%{_libdir}/asterisk/modules/func_frame_drop.so
%{_libdir}/asterisk/modules/func_json.so
%{_libdir}/asterisk/modules/func_sayfiles.so
%{_libdir}/asterisk/modules/func_scramble.so
%{_libdir}/asterisk/modules/res_aeap.so
%{_libdir}/asterisk/modules/res_speech_aeap.so
%{_libdir}/asterisk/modules/res_tonedetect.so
#GV 18.12

%{_libdir}/asterisk/modules/app_blind_transfer.so
%{_libdir}/asterisk/modules/app_bridgeaddchan.so	
%{_libdir}/asterisk/modules/app_cdr.so
%{_libdir}/asterisk/modules/app_celgenuserevent.so
%{_libdir}/asterisk/modules/app_chanisavail.so
%{_libdir}/asterisk/modules/app_channelredirect.so
%{_libdir}/asterisk/modules/app_chanspy.so
%{_libdir}/asterisk/modules/app_confbridge.so
%{_libdir}/asterisk/modules/app_controlplayback.so
%{_libdir}/asterisk/modules/app_db.so
%{_libdir}/asterisk/modules/app_dial.so
%{_libdir}/asterisk/modules/app_dictate.so
%{_libdir}/asterisk/modules/app_directed_pickup.so
%{_libdir}/asterisk/modules/app_directory.so
%{_libdir}/asterisk/modules/app_disa.so
%{_libdir}/asterisk/modules/app_dumpchan.so
%{_libdir}/asterisk/modules/app_echo.so
%{_libdir}/asterisk/modules/app_exec.so
%{_libdir}/asterisk/modules/app_externalivr.so
%{_libdir}/asterisk/modules/app_festival.so
%{_libdir}/asterisk/modules/app_forkcdr.so
%{_libdir}/asterisk/modules/app_followme.so
%{_libdir}/asterisk/modules/app_getcpeid.so
#removed upstream 20.x %{_libdir}/asterisk/modules/app_ices.so
#removed upstream 20.x %{_libdir}/asterisk/modules/app_image.so
%{_libdir}/asterisk/modules/app_macro.so
%{_libdir}/asterisk/modules/app_milliwatt.so
%{_libdir}/asterisk/modules/app_minivm.so
%{_libdir}/asterisk/modules/app_mixmonitor.so
%{_libdir}/asterisk/modules/app_morsecode.so
%{_libdir}/asterisk/modules/app_mp3.so
#removed upstream 20.x %{_libdir}/asterisk/modules/app_nbscat.so
%{_libdir}/asterisk/modules/app_originate.so
%{_libdir}/asterisk/modules/app_playback.so
%{_libdir}/asterisk/modules/app_playtones.so
%{_libdir}/asterisk/modules/app_privacy.so
%{_libdir}/asterisk/modules/app_queue.so
%{_libdir}/asterisk/modules/app_readexten.so
%{_libdir}/asterisk/modules/app_read.so
%{_libdir}/asterisk/modules/app_record.so
%{_libdir}/asterisk/modules/app_sayunixtime.so
%{_libdir}/asterisk/modules/app_senddtmf.so
%{_libdir}/asterisk/modules/app_sendtext.so
%{_libdir}/asterisk/modules/app_sms.so
%{_libdir}/asterisk/modules/app_softhangup.so
%{_libdir}/asterisk/modules/app_speech_utils.so
%{_libdir}/asterisk/modules/app_stack.so
%{_libdir}/asterisk/modules/app_stream_echo.so
%{_libdir}/asterisk/modules/app_system.so
%{_libdir}/asterisk/modules/app_talkdetect.so
%{_libdir}/asterisk/modules/app_test.so
%{_libdir}/asterisk/modules/app_transfer.so
#removed upstream 20.x %{_libdir}/asterisk/modules/app_url.so
%{_libdir}/asterisk/modules/app_userevent.so
%{_libdir}/asterisk/modules/app_verbose.so
%{_libdir}/asterisk/modules/app_waitforring.so
%{_libdir}/asterisk/modules/app_waitforsilence.so
%{_libdir}/asterisk/modules/app_waituntil.so
%{_libdir}/asterisk/modules/app_while.so
%{_libdir}/asterisk/modules/app_zapateller.so
%{_libdir}/asterisk/modules/bridge_builtin_features.so
%{_libdir}/asterisk/modules/bridge_simple.so
%{_libdir}/asterisk/modules/bridge_softmix.so
%{_libdir}/asterisk/modules/cdr_csv.so
%{_libdir}/asterisk/modules/cdr_custom.so
%{_libdir}/asterisk/modules/cdr_manager.so
%{_libdir}/asterisk/modules/cel_custom.so
%{_libdir}/asterisk/modules/cel_manager.so
%{_libdir}/asterisk/modules/chan_iax2.so
%{_libdir}/asterisk/modules/chan_mgcp.so
%{_libdir}/asterisk/modules/chan_rtp.so
#removed upstream 20.x %{_libdir}/asterisk/modules/chan_oss.so
%{_libdir}/asterisk/modules/chan_skinny.so
%{_libdir}/asterisk/modules/chan_sip.so
%{_libdir}/asterisk/modules/chan_unistim.so
%{_libdir}/asterisk/modules/codec_adpcm.so
%{_libdir}/asterisk/modules/codec_alaw.so
%{_libdir}/asterisk/modules/codec_a_mu.so
%{_libdir}/asterisk/modules/codec_g722.so
%{_libdir}/asterisk/modules/codec_g726.so
%{_libdir}/asterisk/modules/codec_gsm.so
%{_libdir}/asterisk/modules/codec_lpc10.so
%{_libdir}/asterisk/modules/codec_ulaw.so
%{_libdir}/asterisk/modules/format_g719.so
%{_libdir}/asterisk/modules/format_g723.so
%{_libdir}/asterisk/modules/format_g726.so
%{_libdir}/asterisk/modules/format_g729.so
%{_libdir}/asterisk/modules/format_gsm.so
%{_libdir}/asterisk/modules/format_h263.so
%{_libdir}/asterisk/modules/format_h264.so
%{_libdir}/asterisk/modules/format_ilbc.so
%{_libdir}/asterisk/modules/format_ogg_speex.so
%{_libdir}/asterisk/modules/format_pcm.so
%{_libdir}/asterisk/modules/format_siren7.so
%{_libdir}/asterisk/modules/format_siren14.so
%{_libdir}/asterisk/modules/format_sln.so
%{_libdir}/asterisk/modules/format_vox.so
%{_libdir}/asterisk/modules/format_wav_gsm.so
%{_libdir}/asterisk/modules/format_wav.so
%{_libdir}/asterisk/modules/func_aes.so
#%{_libdir}/asterisk/modules/func_audiohookinherit.so
%{_libdir}/asterisk/modules/func_base64.so
%{_libdir}/asterisk/modules/func_blacklist.so
%{_libdir}/asterisk/modules/func_callcompletion.so
%{_libdir}/asterisk/modules/func_callerid.so
%{_libdir}/asterisk/modules/func_cdr.so
%{_libdir}/asterisk/modules/func_channel.so
%{_libdir}/asterisk/modules/func_config.so
%{_libdir}/asterisk/modules/func_cut.so
%{_libdir}/asterisk/modules/func_db.so
%{_libdir}/asterisk/modules/func_devstate.so
%{_libdir}/asterisk/modules/func_dialgroup.so
%{_libdir}/asterisk/modules/func_dialplan.so
%{_libdir}/asterisk/modules/func_enum.so
%{_libdir}/asterisk/modules/func_env.so
%{_libdir}/asterisk/modules/func_extstate.so
%{_libdir}/asterisk/modules/func_frame_trace.so
%{_libdir}/asterisk/modules/func_global.so
%{_libdir}/asterisk/modules/func_groupcount.so	
%{_libdir}/asterisk/modules/func_iconv.so
%{_libdir}/asterisk/modules/func_lock.so
%{_libdir}/asterisk/modules/func_logic.so
%{_libdir}/asterisk/modules/func_math.so
%{_libdir}/asterisk/modules/func_md5.so
%{_libdir}/asterisk/modules/func_module.so
%{_libdir}/asterisk/modules/func_pitchshift.so
%{_libdir}/asterisk/modules/func_rand.so
%{_libdir}/asterisk/modules/func_realtime.so
%{_libdir}/asterisk/modules/func_sha1.so
%{_libdir}/asterisk/modules/func_shell.so
%{_libdir}/asterisk/modules/func_sprintf.so
%{_libdir}/asterisk/modules/func_srv.so
%{_libdir}/asterisk/modules/func_strings.so
%{_libdir}/asterisk/modules/func_sysinfo.so	
%{_libdir}/asterisk/modules/func_timeout.so
%{_libdir}/asterisk/modules/func_uri.so
%{_libdir}/asterisk/modules/func_version.so
%{_libdir}/asterisk/modules/func_vmcount.so
%{_libdir}/asterisk/modules/func_volume.so
%{_libdir}/asterisk/modules/pbx_ael.so
%{_libdir}/asterisk/modules/pbx_config.so
%{_libdir}/asterisk/modules/pbx_dundi.so
%{_libdir}/asterisk/modules/pbx_loopback.so
%{_libdir}/asterisk/modules/pbx_lua.so
%{_libdir}/asterisk/modules/pbx_realtime.so
%{_libdir}/asterisk/modules/pbx_spool.so
%{_libdir}/asterisk/modules/res_adsi.so
%{_libdir}/asterisk/modules/res_ael_share.so
%{_libdir}/asterisk/modules/res_agi.so
%{_libdir}/asterisk/modules/res_clialiases.so
%{_libdir}/asterisk/modules/res_clioriginate.so
%{_libdir}/asterisk/modules/res_convert.so
%{_libdir}/asterisk/modules/res_crypto.so
%{_libdir}/asterisk/modules/res_fax.so
%{_libdir}/asterisk/modules/res_http_post.so
%{_libdir}/asterisk/modules/res_limit.so
%{_libdir}/asterisk/modules/res_monitor.so
%{_libdir}/asterisk/modules/res_musiconhold.so
%{_libdir}/asterisk/modules/res_mutestream.so
#GV 16.5.1
%{_libdir}/asterisk/modules/res_mwi_devstate.so
%{_libdir}/asterisk/modules/res_phoneprov.so
%{_libdir}/asterisk/modules/res_realtime.so
%{_libdir}/asterisk/modules/res_rtp_asterisk.so
%{_libdir}/asterisk/modules/res_rtp_multicast.so
%{_libdir}/asterisk/modules/res_security_log.so
%{_libdir}/asterisk/modules/res_smdi.so
%{_libdir}/asterisk/modules/res_speech.so
%{_libdir}/asterisk/modules/res_stun_monitor.so
%{_libdir}/asterisk/modules/res_timing_pthread.so
%{_libdir}/asterisk/modules/chan_motif.so
%{_libdir}/asterisk/modules/func_speex.so
%{_libdir}/asterisk/modules/res_pktccops.so
%{_libdir}/asterisk/modules/res_config_ldap.so
%{_libdir}/asterisk/modules/res_fax_spandsp.so
%{_libdir}/asterisk/modules/codec_ilbc.so
%{_libdir}/asterisk/modules/func_jitterbuffer.so
%{_libdir}/asterisk/modules/res_format_attr_celt.so
%{_libdir}/asterisk/modules/res_format_attr_ilbc.so
%{_libdir}/asterisk/modules/res_format_attr_silk.so
%{_libdir}/asterisk/modules/func_presencestate.so
%{_libdir}/asterisk/modules/func_hangupcause.so
%{_libdir}/asterisk/modules/res_config_sqlite3.so
%{_libdir}/asterisk/modules/res_format_attr_h263.so
%{_libdir}/asterisk/modules/res_format_attr_h264.so
%{_libdir}/asterisk/modules/res_format_attr_g729.so
%{_libdir}/asterisk/modules/res_http_media_cache.so
%{_libdir}/asterisk/modules/res_http_websocket.so
%{_libdir}/asterisk/modules/res_xmpp.so
#%{_libdir}/asterisk/modules/res_mwi_devstate.so
%{_libdir}/asterisk/modules/res_srtp.so
%{_libdir}/asterisk/modules/app_agent_pool.so
%{_libdir}/asterisk/modules/app_bridgewait.so
%{_libdir}/asterisk/modules/app_stasis.so
%{_libdir}/asterisk/modules/bridge_builtin_interval_features.so
%{_libdir}/asterisk/modules/bridge_holding.so
%{_libdir}/asterisk/modules/bridge_native_rtp.so
%{_libdir}/asterisk/modules/chan_bridge_media.so
%{_libdir}/asterisk/modules/chan_pjsip.so
%{_libdir}/asterisk/modules/func_pjsip_endpoint.so
%{_libdir}/asterisk/modules/res_ari.so
%{_libdir}/asterisk/modules/res_ari_applications.so
%{_libdir}/asterisk/modules/res_ari_asterisk.so
%{_libdir}/asterisk/modules/res_ari_bridges.so
%{_libdir}/asterisk/modules/res_ari_channels.so
%{_libdir}/asterisk/modules/res_ari_device_states.so
%{_libdir}/asterisk/modules/res_ari_endpoints.so
%{_libdir}/asterisk/modules/res_ari_events.so
%{_libdir}/asterisk/modules/res_ari_model.so
%{_libdir}/asterisk/modules/res_ari_playbacks.so
%{_libdir}/asterisk/modules/res_ari_recordings.so
%{_libdir}/asterisk/modules/res_ari_sounds.so
%{_libdir}/asterisk/modules/res_format_attr_opus.so
%{_libdir}/asterisk/modules/res_parking.so
%{_libdir}/asterisk/modules/res_pjsip.so
%{_libdir}/asterisk/modules/res_pjsip_acl.so
%{_libdir}/asterisk/modules/res_pjsip_authenticator_digest.so
%{_libdir}/asterisk/modules/res_pjsip_caller_id.so
%{_libdir}/asterisk/modules/res_pjsip_diversion.so
%{_libdir}/asterisk/modules/res_pjsip_dtmf_info.so
%{_libdir}/asterisk/modules/res_pjsip_endpoint_identifier_anonymous.so
%{_libdir}/asterisk/modules/res_pjsip_endpoint_identifier_ip.so
%{_libdir}/asterisk/modules/res_pjsip_endpoint_identifier_user.so
%{_libdir}/asterisk/modules/res_pjsip_exten_state.so
%{_libdir}/asterisk/modules/res_pjsip_header_funcs.so
%{_libdir}/asterisk/modules/res_pjsip_logger.so
%{_libdir}/asterisk/modules/res_pjsip_messaging.so
%{_libdir}/asterisk/modules/res_pjsip_mwi.so	
%{_libdir}/asterisk/modules/res_pjsip_nat.so
%{_libdir}/asterisk/modules/res_pjsip_notify.so
%{_libdir}/asterisk/modules/res_pjsip_one_touch_record_info.so
%{_libdir}/asterisk/modules/res_pjsip_outbound_authenticator_digest.so	
%{_libdir}/asterisk/modules/res_pjsip_outbound_registration.so
#REM by JP, file not being generated
#%{_libdir}/asterisk/modules/res_pjsip_pidf.so
%{_libdir}/asterisk/modules/res_pjsip_pubsub.so		
%{_libdir}/asterisk/modules/res_pjsip_refer.so		
%{_libdir}/asterisk/modules/res_pjsip_registrar.so
#%{_libdir}/asterisk/modules/res_pjsip_registrar_expire.so
%{_libdir}/asterisk/modules/res_pjsip_rfc3326.so
%{_libdir}/asterisk/modules/res_pjsip_sdp_rtp.so	
%{_libdir}/asterisk/modules/res_pjsip_session.so
%{_libdir}/asterisk/modules/res_pjsip_t38.so
%{_libdir}/asterisk/modules/res_pjsip_transport_websocket.so
%{_libdir}/asterisk/modules/res_sorcery_astdb.so
%{_libdir}/asterisk/modules/res_sorcery_memory_cache.so
%{_libdir}/asterisk/modules/res_sorcery_config.so
%{_libdir}/asterisk/modules/res_sorcery_memory.so
%{_libdir}/asterisk/modules/res_sorcery_realtime.so
%{_libdir}/asterisk/modules/res_stasis.so
%{_libdir}/asterisk/modules/res_stasis_answer.so
%{_libdir}/asterisk/modules/res_stasis_device_state.so
%{_libdir}/asterisk/modules/res_stasis_playback.so
%{_libdir}/asterisk/modules/res_stasis_recording.so
%{_libdir}/asterisk/modules/res_stasis_snoop.so	
%{_libdir}/asterisk/modules/res_statsd.so
%{_libdir}/asterisk/modules/res_chan_stats.so
%{_libdir}/asterisk/modules/res_endpoint_stats.so
%{_libdir}/asterisk/modules/res_pjsip_mwi_body_generator.so
%{_libdir}/asterisk/modules/res_pjsip_pidf_body_generator.so
%{_libdir}/asterisk/modules/res_pjsip_pidf_eyebeam_body_supplement.so
%{_libdir}/asterisk/modules/res_pjsip_xpidf_body_generator.so
%{_libdir}/asterisk/modules/func_sorcery.so
%{_libdir}/asterisk/modules/res_pjsip_pidf_digium_body_supplement.so
%{_libdir}/asterisk/modules/res_pjsip_send_to_voicemail.so
%{_libdir}/asterisk/modules/func_talkdetect.so
%{_libdir}/asterisk/modules/res_pjsip_dialog_info_body_generator.so
%{_libdir}/asterisk/modules/res_pjsip_phoneprov_provider.so
%{_libdir}/asterisk/modules/func_pjsip_aor.so
%{_libdir}/asterisk/modules/func_pjsip_contact.so
%{_libdir}/asterisk/modules/res_pjsip_config_wizard.so
#REM by JP file not being generated
#%{_libdir}/asterisk/modules/res_pjsip_keepalive.so
#%{_libdir}/asterisk/modules/res_pjsip_transport_management.so
%{_libdir}/asterisk/modules/res_pjsip_sips_contact.so
%{_libdir}/asterisk/modules/func_holdintercept.so
%{_libdir}/asterisk/modules/res_format_attr_vp8.so
%{_libdir}/asterisk/modules/res_odbc_transaction.so
%{_libdir}/asterisk/modules/res_pjproject.so
%{_libdir}/asterisk/modules/res_pjsip_history.so
%{_libdir}/asterisk/modules/res_pjsip_empty_info.so
%{_libdir}/libasteriskpj.so
%{_libdir}/libasteriskpj.so.2
%{_libdir}/asterisk/modules/res_format_attr_siren14.so
%{_libdir}/asterisk/modules/res_format_attr_siren7.so
#Add by JP, added the new codecs files
%{_libdir}/asterisk/modules/codec_opus.manifest.xml
%{_libdir}/asterisk/modules/codec_opus.so
%{_libdir}/asterisk/modules/codec_silk.manifest.xml
%{_libdir}/asterisk/modules/codec_silk.so
%{_libdir}/asterisk/modules/codec_siren14.manifest.xml
%{_libdir}/asterisk/modules/codec_siren14.so
%{_libdir}/asterisk/modules/codec_siren7.manifest.xml
%{_libdir}/asterisk/modules/codec_siren7.so
%{_libdir}/asterisk/modules/format_ogg_opus.so
%{_sbindir}/asterisk
%{_sbindir}/rasterisk
%{_sbindir}/safe_asterisk
%{_sbindir}/astcanary
%{_sbindir}/astgenkey
%{_sbindir}/astdb2bdb
%{_sbindir}/astdb2sqlite3
%{_sbindir}/astversion
%{?_without_newt:%if 0}
%{!?_without_newt:%if 1}
#%{_sbindir}/astman
%endif
%{_sbindir}/autosupport
%{_libdir}/asterisk/modules/app_jack.so
%{_libdir}/asterisk/modules/cdr_radius.so
%{_libdir}/asterisk/modules/cel_radius.so
%{_libdir}/asterisk/modules/chan_console.so
%{_libdir}/asterisk/modules/res_calendar.so
%{_libdir}/asterisk/modules/res_calendar_caldav.so
%{_libdir}/asterisk/modules/res_calendar_ews.so
%{_libdir}/asterisk/modules/res_calendar_exchange.so
%{_libdir}/asterisk/modules/res_calendar_icalendar.so
%{_libdir}/asterisk/modules/res_timing_timerfd.so
%{_libdir}/libasteriskssl.so.1
%{_libdir}/libasteriskssl.so
#REM by JP file not being generated
#%{_libdir}/asterisk/modules/res_ari_mailboxes.so
#%{_libdir}/asterisk/modules/res_pjsip_multihomed.so
%{_libdir}/asterisk/modules/res_pjsip_path.so
%{_libdir}/asterisk/modules/func_periodic_hook.so
%{_libdir}/asterisk/modules/res_hep.so
%{_libdir}/asterisk/modules/res_hep_pjsip.so
%{_libdir}/asterisk/modules/res_hep_rtcp.so
%{_libdir}/asterisk/modules/res_manager_devicestate.so
%{_libdir}/asterisk/modules/res_manager_presencestate.so
%{_libdir}/asterisk/modules/res_pjsip_outbound_publish.so
%{_libdir}/asterisk/modules/res_pjsip_publish_asterisk.so
%{_libdir}/asterisk/modules/res_pjsip_dlg_options.so
#Mod by JP, to avoid conflicts with the older CDR files
%exclude %dir %{logdir}/asterisk
%exclude %dir %{logdir}/asterisk/cdr-csv
%exclude %dir %{logdir}/asterisk/cdr-custom
#%attr(0775,asterisk,asterisk) %dir %{logdir}/asterisk
#%attr(0775,asterisk,asterisk) %dir %{logdir}/asterisk/cdr-csv
#%attr(0775,asterisk,asterisk) %dir %{logdir}/asterisk/cdr-custom
%config %{_sysconfdir}/logrotate.d/asterisk
%attr(0775,asterisk,asterisk) %dir /var/run/asterisk
%attr(0755,asterisk,asterisk) %dir /var/lib/asterisk
%attr(0755,asterisk,asterisk) %dir /var/lib/asterisk/agi-bin
%attr(0755,asterisk,asterisk) %dir /var/lib/asterisk/documentation
%attr(0644,asterisk,asterisk)      /var/lib/asterisk/documentation/*
%attr(0755,asterisk,asterisk) %dir /var/lib/asterisk/images
%attr(0644,asterisk,asterisk)      /var/lib/asterisk/images/*
%attr(0755,asterisk,asterisk) %dir /var/lib/asterisk/keys
%attr(0755,asterisk,asterisk) %dir /var/lib/asterisk/licenses
%attr(0755,asterisk,asterisk) %dir /var/lib/asterisk/phoneprov
%attr(0644,asterisk,asterisk)      /var/lib/asterisk/phoneprov/*
%attr(0755,asterisk,asterisk) %dir /var/lib/asterisk/static-http
%attr(0644,asterisk,asterisk)      /var/lib/asterisk/static-http/*
%attr(0755,asterisk,asterisk) %dir /var/lib/digium
%attr(0755,asterisk,asterisk) %dir /var/lib/digium/licenses
%attr(0755,asterisk,asterisk) %dir /var/lib/asterisk/rest-api
%attr(0644,asterisk,asterisk)      /var/lib/asterisk/rest-api/*
/var/lib/asterisk/scripts/*
%attr(0775,asterisk,asterisk) %dir /var/spool/asterisk
%attr(0775,asterisk,asterisk) %dir /var/spool/asterisk/meetme
%attr(0775,asterisk,asterisk) %dir /var/spool/asterisk/system
%attr(0775,asterisk,asterisk) %dir /var/spool/asterisk/tmp
%attr(0775,asterisk,asterisk) %dir /var/spool/asterisk/voicemail
#
#  Alsa Subpackage
#
%{?_without_alsa:%if 0}
%{!?_without_alsa:%if 1}
%files alsa
%defattr(-, root, root)
%{_libdir}/asterisk/modules/chan_alsa.so
%endif

#
#  snmp Subpackage
#
%{?_without_snmp:%if 0}
%{!?_without_snmp:%if 1}
%files snmp
%defattr(-, root, root)
%{_libdir}/asterisk/modules/res_snmp.so
%endif

#
#  pgsql Subpackage
#
%{?_without_pgsql:%if 0}
%{!?_without_pgsql:%if 1}
%files pgsql
%defattr(-, root, root)
%{_libdir}/asterisk/modules/res_config_pgsql.so
%{_libdir}/asterisk/modules/cdr_pgsql.so
%{_libdir}/asterisk/modules/cel_pgsql.so
%endif

#
#  tds Subpackage
#
%{?_without_tds:%if 0}
%{!?_without_tds:%if 1}
%files tds
%defattr(-, root, root)
%{_libdir}/asterisk/modules/cdr_tds.so
%{_libdir}/asterisk/modules/cel_tds.so
%endif

#
#  mISDN Subpackage
#
%{?_without_misdn:%if 0}
%{!?_without_misdn:%if 1}
%files misdn
%defattr(-, root, root)
%{_libdir}/asterisk/modules/chan_misdn.so
%endif

#
#  dahdi Subpackage
#
%{?_without_dahdi:%if 0}
%{!?_without_dahdi:%if 1}
%files dahdi
%defattr(-, root, root)
#removed upstream 20.x %{_libdir}/asterisk/modules/app_dahdiras.so
%{_libdir}/asterisk/modules/app_flash.so
%{_libdir}/asterisk/modules/app_meetme.so
%{_libdir}/asterisk/modules/app_page.so
%{_libdir}/asterisk/modules/chan_dahdi.so
%{_libdir}/asterisk/modules/codec_dahdi.so
%{_libdir}/asterisk/modules/res_timing_dahdi.so
%{_datadir}/dahdi/span_config.d/40-asterisk
%endif

#
#  Configs Subpackage
#
%files configs
%defattr(-, asterisk, asterisk)
%attr(0664,asterisk,asterisk) %config(noreplace) %{_sysconfdir}/asterisk/*
#Renamed the config files to keep the ones created by IssabelPBX
#%config(noreplace) %{_sysconfdir}/asterisk/enum.conf
#%config(noreplace) %{_sysconfdir}/asterisk/extensions.conf
#%config(noreplace) %{_sysconfdir}/asterisk/features.conf
#%config(noreplace) %{_sysconfdir}/asterisk/http.conf
#%config(noreplace) %{_sysconfdir}/asterisk/iax.conf
#%config(noreplace) %{_sysconfdir}/asterisk/indications.conf
#%config(noreplace) %{_sysconfdir}/asterisk/logger.conf
#%config(noreplace) %{_sysconfdir}/asterisk/manager.conf
#%config(noreplace) %{_sysconfdir}/asterisk/meetme.conf
#%config(noreplace) %{_sysconfdir}/asterisk/modules.conf
#%config(noreplace) %{_sysconfdir}/asterisk/motif.conf
#%config(noreplace) %{_sysconfdir}/asterisk/phone.conf
#%config(noreplace) %{_sysconfdir}/asterisk/res_fax.conf
#%config(noreplace) %{_sysconfdir}/asterisk/res_odbc.conf
#%config(noreplace) %{_sysconfdir}/asterisk/rtp.conf
#%config(noreplace) %{_sysconfdir}/asterisk/sip.conf
#%config(noreplace) %{_sysconfdir}/asterisk/sip_notify.conf
#%config(noreplace) %{_sysconfdir}/asterisk/udptl.conf
#%config(noreplace) %{_sysconfdir}/asterisk/xmpp.conf
#%config(noreplace) %{_sysconfdir}/asterisk/iax.conf

#
#  cURL Subpackage
#
%{?_without_curl:%if 0}
%{!?_without_curl:%if 1}
%files curl
%defattr(-, root, root)
%{_libdir}/asterisk/modules/func_curl.so
%{_libdir}/asterisk/modules/res_config_curl.so
%{_libdir}/asterisk/modules/res_curl.so
%endif

#
#  Development Subpackage
#
%files devel
#new headers in 20.16-20.18
%{_includedir}/asterisk/refer.h
%{_includedir}/asterisk/res_geolocation.h
%{_includedir}/asterisk/res_pjsip_redirect.h
%{_includedir}/asterisk/serializer_shutdown_group.h
%{_includedir}/asterisk/taskpool.h
%{_includedir}/asterisk/websocket_client.h
%defattr(-, root, root)
%{_includedir}/asterisk.h
%{_includedir}/asterisk/spinlock.h
%{_includedir}/asterisk/_private.h
%{_includedir}/asterisk/abstract_jb.h
%{_includedir}/asterisk/acl.h
%{_includedir}/asterisk/adsi.h
%{_includedir}/asterisk/ael_structs.h
%{_includedir}/asterisk/agi.h
%{_includedir}/asterisk/alaw.h

#NG 16.16.0
%{_includedir}/asterisk/dns_txt.h
%{_includedir}/asterisk/logger_category.h
%{_includedir}/asterisk/res_stir_shaken.h
%{_includedir}/asterisk/utf8.h

#NG 18.4.0
%{_includedir}/asterisk/stasis_state.h
%{_includedir}/asterisk/res_pjsip_session_caps.h

#GV 18.12
%{_includedir}/asterisk/res_aeap.h
%{_includedir}/asterisk/res_aeap_message.h

#Added by JP for .17 compat
%{_includedir}/asterisk/aoc.h
%{_includedir}/asterisk/alertpipe.h
%{_includedir}/asterisk/autochan.h
%{_includedir}/asterisk/autoconfig.h
%{_includedir}/asterisk/app.h	
#GV 16.5.1
%{_includedir}//asterisk/mwi.h
%{_includedir}/asterisk/astdb.h
%{_includedir}/asterisk/ast_expr.h
%{_includedir}/asterisk/ast_version.h
%{_includedir}/asterisk/astmm.h
#%{_includedir}/asterisk/astobj.h
%{_includedir}/asterisk/astobj2.h
#%{_includedir}/asterisk/astosp.h
%{_includedir}/asterisk/audiohook.h
%{_includedir}/asterisk/build.h
%{_includedir}/asterisk/buildinfo.h
%{_includedir}/asterisk/buildopts.h
%{_includedir}/asterisk/calendar.h
%{_includedir}/asterisk/callerid.h
%{_includedir}/asterisk/causes.h
%{_includedir}/asterisk/ccss.h
%{_includedir}/asterisk/cdr.h
%{_includedir}/asterisk/cel.h
%{_includedir}/asterisk/channel.h
%{_includedir}/asterisk/channelstate.h
%{_includedir}/asterisk/chanvars.h
%{_includedir}/asterisk/cli.h
%{_includedir}/asterisk/compat.h
%{_includedir}/asterisk/compiler.h
%{_includedir}/asterisk/config.h
%{_includedir}/asterisk/conversions.h
%{_includedir}/asterisk/crypto.h
#%{_includedir}/asterisk/data.h
%{_includedir}/asterisk/data_buffer.h
%{_includedir}/asterisk/datastore.h
%{_includedir}/asterisk/devicestate.h
%{_includedir}/asterisk/dial.h
%{_includedir}/asterisk/dlinkedlists.h
%{_includedir}/asterisk/dns.h
%{_includedir}/asterisk/dns_core.h
%{_includedir}/asterisk/dns_internal.h
%{_includedir}/asterisk/dns_naptr.h
%{_includedir}/asterisk/dns_query_set.h
%{_includedir}/asterisk/dns_recurring.h
%{_includedir}/asterisk/dns_resolver.h
%{_includedir}/asterisk/dns_srv.h
%{_includedir}/asterisk/dns_test.h
%{_includedir}/asterisk/dns_tlsa.h
%{_includedir}/asterisk/dnsmgr.h
%{_includedir}/asterisk/doxyref.h
%{_includedir}/asterisk/dsp.h
%{_includedir}/asterisk/dundi.h
%{_includedir}/asterisk/endian.h
%{_includedir}/asterisk/enum.h
%{_includedir}/asterisk/event.h
%{_includedir}/asterisk/event_defs.h
%{_includedir}/asterisk/extconf.h
%{_includedir}/asterisk/features.h
%{_includedir}/asterisk/file.h
%{_includedir}/asterisk/frame.h
%{_includedir}/asterisk/framehook.h
%{_includedir}/asterisk/fskmodem.h
%{_includedir}/asterisk/fskmodem_float.h
%{_includedir}/asterisk/fskmodem_int.h
%{_includedir}/asterisk/hashtab.h
%{_includedir}/asterisk/heap.h
%{_includedir}/asterisk/http.h
%{_includedir}/asterisk/ilbc.h
%{_includedir}/asterisk/image.h
%{_includedir}/asterisk/iostream.h
%{_includedir}/asterisk/indications.h
%{_includedir}/asterisk/inline_api.h
%{_includedir}/asterisk/io.h
%{_includedir}/asterisk/global_datastores.h
%{_includedir}/asterisk/linkedlists.h
%{_includedir}/asterisk/localtime.h
%{_includedir}/asterisk/lock.h
%{_includedir}/asterisk/logger.h
%{_includedir}/asterisk/manager.h
%{_includedir}/asterisk/md5.h
%{_includedir}/asterisk/media_cache.h
%{_includedir}/asterisk/mod_format.h
%{_includedir}/asterisk/module.h
%{_includedir}/asterisk/monitor.h
%{_includedir}/asterisk/musiconhold.h
#%{_includedir}/asterisk/netsock.h
%{_includedir}/asterisk/netsock2.h
%{_includedir}/asterisk/network.h
%{_includedir}/asterisk/optional_api.h
%{_includedir}/asterisk/options.h
%{_includedir}/asterisk/paths.h
%{_includedir}/asterisk/pbx.h		
%{_includedir}/asterisk/pktccops.h
%{_includedir}/asterisk/plc.h
%{_includedir}/asterisk/poll-compat.h
%{_includedir}/asterisk/privacy.h
%{_includedir}/asterisk/pval.h	
%{_includedir}/asterisk/res_odbc.h
%{_includedir}/asterisk/res_fax.h
%{_includedir}/asterisk/res_srtp.h
%{_includedir}/asterisk/rtp_engine.h
%{_includedir}/asterisk/say.h
%{_includedir}/asterisk/sched.h		
%{_includedir}/asterisk/security_events.h
%{_includedir}/asterisk/security_events_defs.h
%{_includedir}/asterisk/select.h
%{_includedir}/asterisk/serializer.h
%{_includedir}/asterisk/sha1.h
%{_includedir}/asterisk/slin.h
%{_includedir}/asterisk/slinfactory.h
%{_includedir}/asterisk/smdi.h
%{_includedir}/asterisk/speech.h
%{_includedir}/asterisk/srv.h
%{_includedir}/asterisk/stringfields.h
%{_includedir}/asterisk/strings.h
%{_includedir}/asterisk/stun.h
%{_includedir}/asterisk/syslog.h
%{_includedir}/asterisk/taskprocessor.h
%{_includedir}/asterisk/tcptls.h
%{_includedir}/asterisk/tdd.h
%{_includedir}/asterisk/term.h
%{_includedir}/asterisk/test.h
%{_includedir}/asterisk/threadstorage.h
%{_includedir}/asterisk/time.h
%{_includedir}/asterisk/timing.h
%{_includedir}/asterisk/transcap.h
%{_includedir}/asterisk/translate.h
%{_includedir}/asterisk/udptl.h
%{_includedir}/asterisk/ulaw.h
%{_includedir}/asterisk/unaligned.h
%{_includedir}/asterisk/utils.h
%{_includedir}/asterisk/vector.h
%{_includedir}/asterisk/version.h
%{_includedir}/asterisk/xml.h
%{_includedir}/asterisk/xmldoc.h
%{_includedir}/asterisk/doxygen/architecture.h
#%{_includedir}/asterisk/doxygen/asterisk-git-howto.h
#%{_includedir}/asterisk/doxygen/commits.h
%{_includedir}/asterisk/doxygen/licensing.h
#%{_includedir}/asterisk/doxygen/releases.h
#%{_includedir}/asterisk/doxygen/reviewboard.h
%{_includedir}/asterisk/celt.h
%{_includedir}/asterisk/format.h
%{_includedir}/asterisk/format_cap.h
%{_includedir}/asterisk/message.h
%{_includedir}/asterisk/silk.h
%{_includedir}/asterisk/presencestate.h
%{_includedir}/asterisk/channel_internal.h
%{_includedir}/asterisk//config_options.h
%{_includedir}/asterisk/http_websocket.h
%{_includedir}/asterisk/sip_api.h
%{_includedir}/asterisk/xmpp.h
%{_includedir}/asterisk/ari.h
%{_includedir}/asterisk/backtrace.h
%{_includedir}/asterisk/bridge.h
%{_includedir}/asterisk/bridge_after.h
%{_includedir}/asterisk/bridge_basic.h
%{_includedir}/asterisk/bridge_channel.h
%{_includedir}/asterisk/bridge_channel_internal.h
%{_includedir}/asterisk/bridge_features.h
%{_includedir}/asterisk/bridge_internal.h
%{_includedir}/asterisk/bridge_roles.h
%{_includedir}/asterisk/bridge_technology.h
%{_includedir}/asterisk/bucket.h
%{_includedir}/asterisk/core_local.h
%{_includedir}/asterisk/core_unreal.h
%{_includedir}/asterisk/endpoints.h
%{_includedir}/asterisk/features_config.h
%{_includedir}/asterisk/json.h
%{_includedir}/asterisk/media_index.h
%{_includedir}/asterisk/mixmonitor.h
%{_includedir}/asterisk/opus.h
%{_includedir}/asterisk/parking.h
%{_includedir}/asterisk/pickup.h
%{_includedir}/asterisk/res_pjsip.h
%{_includedir}/asterisk/res_pjsip_cli.h
#%{_includedir}/asterisk/res_pjsip_exten_state.h
%{_includedir}/asterisk/res_pjsip_pubsub.h
%{_includedir}/asterisk/res_pjsip_session.h
%{_includedir}/asterisk/sdp_srtp.h
%{_includedir}/asterisk/sem.h
%{_includedir}/asterisk/sorcery.h
%{_includedir}/asterisk/sounds_index.h
%{_includedir}/asterisk/stasis.h
%{_includedir}/asterisk/stasis_app.h
%{_includedir}/asterisk/stasis_app_device_state.h
%{_includedir}/asterisk/stasis_app_impl.h
%{_includedir}/asterisk/stasis_app_playback.h
%{_includedir}/asterisk/stasis_app_recording.h
%{_includedir}/asterisk/stasis_app_snoop.h
%{_includedir}/asterisk/stasis_bridges.h
%{_includedir}/asterisk/stasis_cache_pattern.h
%{_includedir}/asterisk/stasis_channels.h
%{_includedir}/asterisk/stasis_endpoints.h
%{_includedir}/asterisk/stasis_internal.h
%{_includedir}/asterisk/stasis_message_router.h
%{_includedir}/asterisk/stasis_system.h
%{_includedir}/asterisk/stasis_test.h
%{_includedir}/asterisk/statsd.h
%{_includedir}/asterisk/stream.h
%{_includedir}/asterisk/threadpool.h
%{_includedir}/asterisk/uuid.h
%{_includedir}/asterisk/res_mwi_external.h
%{_includedir}/asterisk/stasis_app_mailbox.h
%{_includedir}/asterisk/res_pjsip_body_generator_types.h
%{_includedir}/asterisk/res_pjsip_presence_xml.h
%{_includedir}/asterisk/res_hep.h
%{_includedir}/asterisk/beep.h
%{_includedir}/asterisk/codec.h
%{_includedir}/asterisk/format_cache.h
%{_includedir}/asterisk/format_compatibility.h
%{_includedir}/asterisk/res_pjsip_outbound_publish.h
%{_includedir}/asterisk/smoother.h
%{_includedir}/asterisk/uri.h
%{_includedir}/asterisk/phoneprov.h
%{_includedir}/asterisk/max_forwards.h
%{_includedir}/asterisk/res_odbc_transaction.h
%{_includedir}/asterisk/res_pjproject.h
%{_includedir}/asterisk/named_locks.h
%{_includedir}/asterisk/multicast_rtp.h

#
#  Documentation Subpackage
#
%files doc
%defattr(-, root, root)

#
#  Manual Pages
#
%{_mandir}/man8/asterisk.8.gz
%{_mandir}/man8/astgenkey.8.gz
%{_mandir}/man8/autosupport.8.gz
%{_mandir}/man8/safe_asterisk.8.gz
%{_mandir}/man8/astdb2bdb.8.gz
%{_mandir}/man8/astdb2sqlite3.8.gz

#  Ogg-Vorbis Subpackage
#
%{?_without_ogg:%if 0}
%{!?_without_ogg:%if 1}
%files ogg
%defattr(-, root, root)
%{_libdir}/asterisk/modules/format_ogg_vorbis.so
%endif

#
#  Speex Subpackage
#
%{?_without_speex:%if 0}
%{!?_without_speex:%if 1}
%files speex
%defattr(-, root, root)
%{_libdir}/asterisk/modules/codec_speex.so
%endif

#
#  resample Subpackage
#
%{?_without_resample:%if 0}
%{!?_without_resample:%if 1}
%files resample
%defattr(-, root, root)
%{_libdir}/asterisk/modules/codec_resample.so
%endif

#
#  unixODBC Subpackage
#
%{?_without_odbc:%if 0}
%{!?_without_odbc:%if 1}
%files odbc
%defattr(-, root, root)
%{_libdir}/asterisk/modules/cdr_adaptive_odbc.so
%{_libdir}/asterisk/modules/cdr_odbc.so
%{_libdir}/asterisk/modules/cel_odbc.so
%{_libdir}/asterisk/modules/func_odbc.so
%{_libdir}/asterisk/modules/res_config_odbc.so
%{_libdir}/asterisk/modules/res_odbc.so
%{_sysconfdir}/asterisk8.odbc.ini
%post odbc
mv -f %{_sysconfdir}/asterisk8.odbc.ini %{_sysconfdir}/odbc.ini
%endif

#
#  sqlite3 Subpackage
#
%{?_without_sqlite3:%if 0}
%{!?_without_sqlite3:%if 1}
%files sqlite3
%defattr(-, root, root)
%{_libdir}/asterisk/modules/cdr_sqlite3_custom.so
%{_libdir}/asterisk/modules/cel_sqlite3_custom.so

%endif

#
#  voicemail file storage Subpackage
#
%files voicemail
%defattr(-, root, root)
%{_libdir}/asterisk/modules/app_voicemail.so

#
#  voicemail ODBC storage Subpackage
#
%{?_without_voicemail_odbcstorage:%if 0}
%{!?_without_voicemail_odbcstorage:%if 1}
%files voicemail-odbcstorage
%defattr(-, root, root)
#%{_libdir}/asterisk/modules/app_voicemail_odbcstorage.so
%endif

#
#  voicemail IMAP storage Subpackage
#
%{?_without_voicemail_imapstorage:%if 0}
%{!?_without_voicemail_imapstorage:%if 1}
%files voicemail-imapstorage
%defattr(-, root, root)
#%{_libdir}/asterisk/modules/app_voicemail_imapstorage.so
%endif

%files addons
%defattr(-, root, root)

%files addons-core
%defattr(-, root, root)
%{_libdir}/asterisk/modules/format_mp3.so

%{?_without_mysql:%if 0}
%{!?_without_mysql:%if 1}
%files addons-mysql
#not in 20.18: %{_libdir}/asterisk/modules/app_mysql.so
#not in 20.18: %{_libdir}/asterisk/modules/cdr_mysql.so
%{_libdir}/asterisk/modules/res_config_mysql.so
%endif

%{?_without_bluetooth:%if 0}
%{!?_without_bluetooth:%if 1}
%files addons-bluetooth
%{_libdir}/asterisk/modules/chan_mobile.so
%endif

%{?_without_ooh323:%if 0}
%{!?_without_ooh323:%if 1}
%files addons-ooh323
%{_libdir}/asterisk/modules/chan_ooh323.so
%endif

%changelog
* Fri Oct 09 2026 Galcyon lab <lab@localhost> 20.18.0-1
- Rebase on Asterisk 20.18.0 (chan_websocket available since 20.16.0). Spec derived from asterisk18 18.12.0 of Issabel; same patches (tcptls inhibit, websocket ping).

* Sat May 14 2022 German Venturino <german@issabel.com> 18.12.0-1
- Fix log rotate
- Version bump

* Tue Nov 09 2021 Nicolás Gudiño <nicolas@issabel.com> 18.6.0-2
- Vosk with multi server and grammar support

* Thu Dec 05 2019 German Venturino <german@issabel.com> 16.6.2-0
- COLOR=yes setting

* Thu Feb 21 2019 Juan Bustos <juan@issabel.com> 16.2.0-0
- Version bump

* Wed Dec 12 2018 Juan Bustos <juan@issabel.com> 16.1.0-0
- Initial package
