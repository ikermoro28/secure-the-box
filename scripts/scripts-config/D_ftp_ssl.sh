#!/bin/bash

USER_NAME=${1:-admin}

# 1. Crear el usuario dinámico y configurar sudo
useradd -m -s /bin/bash "$USER_NAME"
echo "$USER_NAME:stb2024" | chpasswd
usermod -aG sudo "$USER_NAME"

echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME
chmod 440 /etc/sudoers.d/$USER_NAME

touch "/home/$USER_NAME/.sudo_as_admin_successful"
chown "$USER_NAME:$USER_NAME" "/home/$USER_NAME/.sudo_as_admin_successful"
echo "$USER_NAME" > /tmp/terminal_user.txt

# 2. Instalar el FTP real y OpenSSL
apt-get update > /dev/null 2>&1
apt-get install -y vsftpd openssl > /dev/null 2>&1
apt-get install -y iproute2 > /dev/null 2>&1
apt-get install -y netcat-traditional > /dev/null 2>&1

mkdir -p /var/run/vsftpd/empty

# 3. Configuración legítima pero insegura (Sin SSL)
cat << 'EOF' > /etc/vsftpd.conf
listen=YES
listen_ipv6=NO
anonymous_enable=NO
local_enable=YES
write_enable=YES
# Vulnerabilidad: SSL deshabilitado
ssl_enable=NO
EOF

# 4. Iniciar servicio
/usr/sbin/vsftpd &
