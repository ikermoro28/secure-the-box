#!/bin/bash

# Capturamos el nombre de usuario que nos envía Python (o usamos 'admin' por defecto)
USER_NAME=${1:-admin}

# 1. Crear el usuario dinámico (ya somos root, no necesitamos sudo)
useradd -m -s /bin/bash "$USER_NAME"
echo "$USER_NAME:stb2024" | chpasswd
usermod -aG sudo "$USER_NAME"

# Configurar sudo sin contraseña para el usuario
echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME
chmod 440 /etc/sudoers.d/$USER_NAME

# Quitar aviso de sudo y dejar pista para la App
touch "/home/$USER_NAME/.sudo_as_admin_successful"
chown "$USER_NAME:$USER_NAME" "/home/$USER_NAME/.sudo_as_admin_successful"
echo "$USER_NAME" > /tmp/terminal_user.txt

# 2. Instalación y configuración de SSH (como root)
apt-get update > /dev/null 2>&1
apt-get install -y openssh-server > /dev/null 2>&1
mkdir -p /run/sshd
passwd -d root > /dev/null 2>&1
# Configuración SSH insegura (como root)
cat >> /etc/ssh/sshd_config << EOF
Port 222
PermitRootLogin yes
PermitEmptyPasswords yes
UsePAM no
EOF

# Iniciamos SSH
/usr/sbin/sshd
