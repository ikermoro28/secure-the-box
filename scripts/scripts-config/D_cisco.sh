#!/bin/bash

# Capturamos el nombre de usuario
USER_NAME=${1:-admin}

# 1. Crear el usuario de Linux subyacente
useradd -m -s /bin/bash "$USER_NAME"
echo "$USER_NAME:stb2024" | chpasswd

# Agregamos al usuario al grupo 'frrvty' para que pueda ejecutar la CLI (vtysh) sin permisos de root
usermod -aG sudo,frrvty "$USER_NAME"
usermod -aG frrvty root

# Configurar sudo sin contraseña para el entorno
echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME
chmod 440 /etc/sudoers.d/$USER_NAME
echo "$USER_NAME" > /tmp/terminal_user.txt

# ==========================================
# 2. CONFIGURACIÓN DEL ENTORNO CISCO (FRR)
# ==========================================

# Habilitamos el demonio principal de enrutamiento (Zebra)
sed -i 's/zebra=no/zebra=yes/' /etc/frr/daemons

# Inyectamos la configuración vulnerable inicial (Como si fuera el startup-config)
cat <<EOF > /etc/frr/frr.conf
frr version 8.4
frr defaults traditional
hostname IOS-Core-R1
!
! VULNERABILIDAD 1: Contraseñas débiles y en texto claro
password cisco
enable password cisco
!
! VULNERABILIDAD 2: Ruta estática maliciosa (Backdoor de enrutamiento)
ip route 0.0.0.0/0 192.168.66.6
!
line vty
!
EOF

# Ajustamos permisos requeridos por el servicio
chown frr:frr /etc/frr/frr.conf

# Iniciamos el servicio de simulación de router silenciosamente
/etc/init.d/frr start > /dev/null 2>&1

# ==========================================
# 3. LANZAMIENTO AUTOMÁTICO DE LA CLI CISCO
# ==========================================

# Hacemos que la terminal entre directamente a la CLI del router (vtysh) al abrirse.
# No incluimos textos de bienvenida, entrará directo al prompt IOS-Core-R1#
echo "vtysh" >> /home/$USER_NAME/.bashrc
echo "vtysh" >> /root/.bashrc
