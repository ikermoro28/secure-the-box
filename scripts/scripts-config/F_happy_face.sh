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

# Crea el archivo prueba2 en /home pidiendo permisos de administrador
touch prueba2

