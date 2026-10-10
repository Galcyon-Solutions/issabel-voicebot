<?php
// Quita lo que crea crear_escenario.php: la Misc Application "Menu de bienvenida", el IVR "Demo Voicebot" y los dos
// destinos personalizados. Uso: php quitar_escenario.php 7500 7501   (extensiones de los voicebots)
$ext_galcymedia = $argv[1] ?? '7500';
$ext_puro = $argv[2] ?? '7501';

chdir('/var/www/html');
include '/etc/issabelpbx.conf';
global $db;

foreach (miscapps_list(false) as $m) {
    if ($m['description'] === 'Menu de bienvenida') { miscapps_delete($m['miscapps_id']); echo "Misc Application quitada\n"; }
}
foreach ($db->getAll('SELECT id FROM ivr_details WHERE name = "Demo Voicebot"') as $fila) {
    ivr_delete($fila[0]); echo "IVR {$fila[0]} quitado\n";
}
foreach (array("from-internal-custom,$ext_galcymedia,1", "from-internal-custom,$ext_puro,1") as $dest) {
    customappsreg_customdests_delete($dest); echo "destino quitado: $dest\n";
}
needreload();
