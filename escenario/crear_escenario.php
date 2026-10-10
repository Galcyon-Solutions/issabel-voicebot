<?php
// Crea, con las funciones propias de IssabelPBX (las mismas que usa la web), el escenario completo de estos manuales:
//
//   llamada -> Misc Application (ext 7800) -> IVR "Demo Voicebot" -> tecla 1 -> Custom Destination -> voicebot galcymedia (7500)
//                                                               -> tecla 2 -> Custom Destination -> agente puro (7501)
//
// Uso (lo lanza escenario/01_crear_escenario.sh):  php crear_escenario.php 7800 7500 7501
// Reglas del framework: incluir /etc/issabelpbx.conf (no bootstrap.php) y hacer chdir a /var/www/html.
// Idempotente: usa su PROPIO IVR llamado "Demo Voicebot" y lo reemplaza si ya existe. Nunca toca otro IVR de tu central.

$ext_menu = $argv[1] ?? '7800';
$ext_galcymedia = $argv[2] ?? '7500';
$ext_puro = $argv[3] ?? '7501';

chdir('/var/www/html');
include '/etc/issabelpbx.conf';
global $db;

function hecho($m) { echo $m . "\n"; }

// 1. Destinos personalizados (Admin > Custom Destinations): "contexto,extension,prioridad"
$destinos = array(
    "from-internal-custom,$ext_galcymedia,1" => 'Voicebot galcymedia',
    "from-internal-custom,$ext_puro,1"       => 'Agente de voz puro',
);
$existentes = array();
foreach (customappsreg_customdests_list() as $d) { $existentes[$d['custom_dest']] = true; }
foreach ($destinos as $dest => $descripcion) {
    if (isset($existentes[$dest])) { hecho("destino ya existe: $dest"); continue; }
    ob_start(); $ok = customappsreg_customdests_add($dest, $descripcion, 'Creado por escenario/01_crear_escenario.sh'); ob_end_clean();
    hecho(($ok ? 'destino creado: ' : 'NO se pudo crear: ') . $dest);
}

// 2. El IVR (Applications > IVR). Si ya hay uno llamado "Demo Voicebot" (el nuestro), se reutiliza su id
$id_ivr = '';
foreach ($db->getAll('SELECT id FROM ivr_details WHERE name = "Demo Voicebot"') as $fila) { $id_ivr = $fila[0]; }
$vals = array(
    'extdisplay' => $id_ivr, 'name' => 'Demo Voicebot', 'description' => 'Menu de bienvenida: 1 galcymedia, 2 puro',
    'announcement' => 0, 'directdial' => '', 'invalid_loops' => 3, 'invalid_retry_recording' => 'default',
    'invalid_destination' => 'app-blackhole,hangup,1', 'invalid_recording' => 'default', 'retvm' => '',
    'timeout_time' => 10, 'timeout_recording' => 'default', 'timeout_retry_recording' => 'default',
    'timeout_destination' => 'app-blackhole,hangup,1', 'timeout_loops' => 3,
    'timeout_append_announce' => '0', 'invalid_append_announce' => '0', 'timeout_ivr_ret' => '0', 'invalid_ivr_ret' => '0',
);
$id_ivr = ivr_save_details($vals);
ivr_save_entries($id_ivr, array(
    'ext'  => array('1', '2'),
    'goto' => array("from-internal-custom,$ext_galcymedia,1", "from-internal-custom,$ext_puro,1"),
    'ivr_ret' => array(0, 0),       // 0 = no volver al IVR despues de ese destino
));
hecho("IVR 'Demo Voicebot' guardado con id $id_ivr (tecla 1: $ext_galcymedia, tecla 2: $ext_puro)");

// 3. Una extension de menu para probar sin troncal (Applications > Misc Applications)
$existe = false;
foreach (miscapps_list(true) as $m) { if (($m['ext'] ?? '') == $ext_menu) { $existe = true; } }
if ($existe) {
    hecho("Misc Application $ext_menu ya existe");
} else {
    miscapps_add('Menu de bienvenida', $ext_menu, "ivr-$id_ivr,s,1");
    hecho("Misc Application creada: marcar $ext_menu entra al IVR $id_ivr");
}

needreload();
hecho('listo; falta aplicar (retrieve_conf y dialplan reload)');
