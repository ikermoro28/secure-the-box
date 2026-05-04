#!/bin/bash

# Capturamos el nombre de usuario que nos envía Python (o usamos 'admin' por defecto)
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

# 2. Preparar el entorno para el servicio malicioso
apt-get update > /dev/null 2>&1
apt-get install -y python3 socat > /dev/null 2>&1
apt-get install -y iproute2 > /dev/null 2>&1
apt-get install -y netcat-traditional > /dev/null 2>&1

# 3. Crear el emulador de ProFTPD Vulnerable
cat << 'EOF' > /usr/local/bin/proftpd_rogue.py
import socket, subprocess, threading

def handle_client(c):
    c.send(b"220 ProFTPD 1.3.5 Server (ProFTPD Default Installation) [0.0.0.0]\r\n")
    try:
        c.settimeout(5)
        while True:
            data = c.recv(1024).decode().strip()
            if not data: break
            if data.startswith("SITE CPFR "):
                c.send(b"350 File or directory exists, ready for destination name\r\n")
            elif data.startswith("SITE CPTO "):
                c.send(b"250 Copy successful\r\n")
                # Simulamos la RCE abriendo una terminal en el puerto 6200
                subprocess.Popen(["socat", "TCP-LISTEN:6200,reuseaddr,fork", "EXEC:/bin/bash,pty,stderr,setsid,sigint,sane"])
            elif data.startswith("USER ") or data.startswith("PASS "):
                c.send(b"331 Password required\r\n")
            else:
                c.send(b"500 Invalid command\r\n")
    except:
        pass
    c.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 21))
s.listen(5)
while True:
    c, addr = s.accept()
    threading.Thread(target=handle_client, args=(c,)).start()
EOF

# 4. Lanzar el proceso oculto bajo el nombre "proftpd"
bash -c 'exec -a proftpd python3 /usr/local/bin/proftpd_rogue.py &'
