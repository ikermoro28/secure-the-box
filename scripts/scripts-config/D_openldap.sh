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

# --- 2. NOTIFICACIÓN DEL RETO OPENLDAP ---
# El servicio slapd ya lo está arrancando el ENTRYPOINT nativo de la imagen.
echo "[*] Esperando a que el servicio OpenLDAP inicie internamente..."
sleep 5

# Por defecto, esta imagen permite el "Anonymous Bind" (lectura anónima).
echo "[+] Entorno OpenLDAP vulnerable desplegado y escuchando en el puerto 389."
