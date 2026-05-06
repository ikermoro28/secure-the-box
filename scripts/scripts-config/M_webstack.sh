#!/bin/bash

# 1. Configuración de usuario
USER_NAME=${1:-admin}
useradd -m -s /bin/bash "$USER_NAME"
echo "$USER_NAME:stb2024" | chpasswd
usermod -aG sudo "$USER_NAME"
echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME
chmod 440 /etc/sudoers.d/$USER_NAME
touch "/home/$USER_NAME/.sudo_as_admin_successful"
chown "$USER_NAME:$USER_NAME" "/home/$USER_NAME/.sudo_as_admin_successful"
echo "$USER_NAME" > /tmp/terminal_user.txt

# 2. Instalación de dependencias
echo "[*] Instalando Apache, PHP y utilidades de red..."
export DEBIAN_FRONTEND=noninteractive
apt-get update > /dev/null 2>&1
apt-get install -y apache2 php libapache2-mod-php php-cli net-tools curl iputils-ping sudo python3 > /dev/null 2>&1

# Damos permisos de root al usuario de Apache (www-data) sin pedir contraseña
echo "www-data ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/www-data
chmod 440 /etc/sudoers.d/www-data

# 3. Preparación de Apache para entorno Docker
mkdir -p /var/run/apache2
mkdir -p /var/lock/apache2
mkdir -p /var/log/apache2
a2enmod php$(php -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;') > /dev/null 2>&1

# 4. Crear el archivo index.php vulnerable
echo "[*] Configurando el escenario de Command Injection..."
cat << 'EOF' > /var/www/html/index.php
<?php
$output = "";
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST["ip"])) {
    $ip = $_POST["ip"];
    // ¡LA MAGIA OCURRE AQUÍ! Envolvemos todo en sudo bash
    $output = shell_exec('sudo bash -c "ping -c 2 ' . $ip . '" 2>&1');
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>DNS Health Check</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: sans-serif; background: #1a1a2e; color: white; display: flex; justify-content: center; padding-top: 50px; margin: 0; }
        .card { background: #16213e; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 100%; max-width: 500px; }
        h2 { margin-top: 0; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 5px; border: none; font-size: 16px; }
        button { width: 100%; padding: 12px; margin: 10px 0; background: #e94560; border: none; color: white; font-weight: bold; font-size: 16px; cursor: pointer; border-radius: 5px; transition: background 0.3s; }
        button:hover { background: #d13d56; }
        .res { background: #0f3460; padding: 15px; margin-top: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; color: #00ff41; width: 100%; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🛡️ DNS Connectivity Check</h2>
        <p>Verifica si tu servidor DNS es alcanzable.</p>
        <form method="POST">
            <input type="text" name="ip" placeholder="IP del Servidor (ej: 8.8.8.8)" required>
            <button type="submit">Ejecutar Ping</button>
        </form>
        <?php if($output): ?>
            <div class="res"><?php echo htmlspecialchars($output); ?></div>
        <?php endif; ?>
    </div>
</body>
</html>
EOF

rm -f /var/www/html/index.html

# 5. Arranque y verificación
echo "[*] Arrancando Apache..."
apache2ctl stop > /dev/null 2>&1
sleep 1
apache2ctl start

echo "[*] Verificando servicio en puerto 80..."
sleep 2
if curl -s --head http://localhost | grep "200 OK" > /dev/null; then
    echo "[+] Despliegue completado: Web activa en puerto 80."
else
    echo "[!] Error detectado. Reintentando con modo debug..."
    source /etc/apache2/envvars && apache2 -k start
fi

echo "[+] Entorno configurado correctamente."
