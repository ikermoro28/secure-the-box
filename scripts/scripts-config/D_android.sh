#!/bin/bash

# Usuario de la app
USER_NAME=${1:-admin}

# Config inicial
useradd -m -s /bin/bash "$USER_NAME"
echo "$USER_NAME:stb2024" | chpasswd
usermod -aG sudo "$USER_NAME"

echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME
chmod 440 /etc/sudoers.d/$USER_NAME

touch "/home/$USER_NAME/.sudo_as_admin_successful"
chown "$USER_NAME:$USER_NAME" "/home/$USER_NAME/.sudo_as_admin_successful"

echo "$USER_NAME" > /tmp/terminal_user.txt

# Montamos al estructura del móvil simulado
mkdir -p /opt/case/logs
mkdir -p /opt/case/filesystem/data/app/com.system.update
mkdir -p /opt/case/filesystem/data/app/com.whatsapp
mkdir -p /opt/case/filesystem/data/app/com.spotify.music
mkdir -p /opt/case/filesystem/data/app/com.android.chrome
mkdir -p /opt/case/filesystem/data/app/com.google.android.youtube
mkdir -p /opt/case/filesystem/data/app/com.google.update.service
mkdir -p /opt/case/network
cat > /opt/case/filesystem/packages.xml << EOF
<packages>
    <package name="com.whatsapp" />
    <package name="com.spotify.music" />
    <package name="com.android.chrome" />
    <package name="com.google.android.youtube" />
    <package name="com.google.update.service" />
    <package name="com.system.update" />
</packages>
EOF

# Fichero de logs de adb
cat > /opt/case/logs/adb.log << EOF
[2026-04-11 08:12:01] adbd started
[2026-04-11 08:12:05] usb device connected
[2026-04-11 08:12:06] shell opened
[2026-04-11 08:12:15] pm list packages
[2026-04-11 08:14:21] usb disconnected

[2026-04-11 09:01:33] adbd listening on port 5555
[2026-04-11 09:01:35] local connection from 127.0.0.1
[2026-04-11 09:01:37] shell opened
[2026-04-11 09:05:11] package install com.spotify.music
[2026-04-11 09:06:42] shell closed

[2026-04-11 10:17:52] usb device connected
[2026-04-11 10:18:01] shell opened
[2026-04-11 10:18:22] settings get global adb_enabled
[2026-04-11 10:18:23] settings get global adb_wifi_enabled
[2026-04-11 10:19:44] usb disconnected

[2026-04-11 11:33:08] usb device connected
[2026-04-11 11:33:11] shell opened
[2026-04-11 11:34:02] logcat -d
[2026-04-11 11:35:17] shell closed

[2026-04-11 12:11:44] usb device connected
[2026-04-11 12:11:46] shell opened
[2026-04-11 12:12:03] pm path com.android.chrome
[2026-04-11 12:12:40] shell closed

[2026-04-11 15:02:18] usb device connected
[2026-04-11 15:02:20] shell opened
[2026-04-11 15:03:01] dumpsys package
[2026-04-11 15:04:12] shell closed

[2026-04-12 03:11:02] adbd listening on port 5555
[2026-04-12 03:14:22] connection from 185.220.101.44
[2026-04-12 03:14:25] shell opened
[2026-04-12 03:14:33] pm list packages
[2026-04-12 03:15:01] package install com.system.update
[2026-04-12 03:15:12] chmod 755 /data/local/tmp
[2026-04-12 03:16:02] monkey -p com.system.update
[2026-04-12 03:17:42] adb shell settings put global adb_enabled 1
[2026-04-12 03:17:45] adb shell settings put global adb_wifi_enabled 1
[2026-04-12 03:18:11] shell closed

[2026-04-12 08:02:14] usb device connected
[2026-04-12 08:02:20] shell opened
[2026-04-12 08:02:33] logcat -d
[2026-04-12 08:03:02] shell closed
EOF

# Config insegura de adb
cat > /opt/case/filesystem/settings_global.xml << EOF
<settings>
    <setting name="adb_enabled" value="1" />
    <setting name="adb_wifi_enabled" value="1" />
</settings>
EOF

# Malware simulado
cat > /opt/case/filesystem/data/app/com.system.update/base.apk << EOF
FAKE_ANDROID_APK
C2_DOMAIN=api.sync-cloud.com
MALWARE_FAMILY=SpyAgent
EOF

# Logs de red
cat > /opt/case/network/netstat.txt << EOF
tcp 10.0.0.15:38422 -> 142.250.184.78:443
tcp 10.0.0.15:42133 -> 91.219.236.77:443
tcp 10.0.0.15:40211 -> 31.13.71.36:443
tcp 10.0.0.15:53321 -> 35.186.224.47:443
EOF
cat > /opt/case/network/dns.log << EOF
google.com
clients3.google.com
play.googleapis.com
spotify.com
api.spotify.com
web.whatsapp.com
graph.facebook.com
cdn.sync-cloud.com
api.sync-cloud.com
youtubei.googleapis.com
android.clients.google.com
EOF

# Readme con pistas
cat > /home/$USER_NAME/README.txt << EOF
Reto forense en Android

Un dispositivo Android corporativo ha sido comprometido tras
exponer ADB por red de forma insegura.

Se han detectado actividades sospechosas relacionadas con:
- accesos remotos no autorizados
- instalación de aplicaciones maliciosas
- posibles conexiones hacia infraestructura externa

Tu misión como analista Blue Team es:

1. Investigar el incidente
2. Identificar la actividad del atacante
3. Encontrar los artefactos maliciosos
4. Asegurar la configuración del dispositivo
5. Eliminar el malware
6. Generar un informe IOC

Requisitos del IOC report:

- Nombre del fichero: ioc-report.txt
- Ubicación: tu directorio HOME

El informe debe contener:
- IP atacante
- Dominio malicioso
- Nombre del paquete malicioso

Directorios útiles:

/opt/case/logs/
/opt/case/filesystem/
/opt/case/network/

EOF
chown -R "$USER_NAME:$USER_NAME" "/home/$USER_NAME"
