#!/bin/bash

# Capturamos el nombre de usuario que nos envía Python (o usamos 'admin' por defecto)
USER_NAME=${1:-admin}

# 1. Crear el usuario dinámico y darle sudo
useradd -m -s /bin/bash "$USER_NAME"
echo "$USER_NAME:stb2024" | chpasswd
usermod -aG sudo "$USER_NAME"

# Quitar aviso de sudo y dejar pista para la App
touch "/home/$USER_NAME/.sudo_as_admin_successful"
chown "$USER_NAME:$USER_NAME" "/home/$USER_NAME/.sudo_as_admin_successful"
echo "$USER_NAME" > /tmp/terminal_user.txt

# 2. Instalación y configuración de SSH (igual que antes)
apt-get update &>/dev/null
apt-get install -y openssh-server &>/dev/null
mkdir -p /run/sshd
passwd -d root &>/dev/null

echo "Port 222" >> /etc/ssh/sshd_config
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
echo "PermitEmptyPasswords yes" >> /etc/ssh/sshd_config
echo "UsePAM no" >> /etc/ssh/sshd_config

/usr/sbin/sshd
