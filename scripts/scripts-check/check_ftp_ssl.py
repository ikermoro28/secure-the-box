#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket
import subprocess
import os

vulnerabilidades_encontradas = 0

# Comprobación 1: ¿Se activó SSL en la configuración?
try:
    with open("/etc/vsftpd.conf", "r") as f:
        config = f.read().lower()
        lines = [line.strip() for line in config.split('\n') if not line.startswith('#')]
        
        if "ssl_enable=yes" not in lines:
            vulnerabilidades_encontradas += 1
except Exception:
    vulnerabilidades_encontradas += 1

# Comprobación 2: ¿El servidor admite conexiones cifradas?
sock_21 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_21.settimeout(2)
try:
    if sock_21.connect_ex(('127.0.0.1', 21)) == 0:
        banner = sock_21.recv(1024).decode()
        # Intentamos iniciar una negociación TLS (Comando FTP AUTH TLS)
        sock_21.send(b"AUTH TLS\r\n")
        response = sock_21.recv(1024).decode()
        
        # El código 234 significa "Proceed with negotiation" (SSL activado correctamente)
        if "234" not in response:
            vulnerabilidades_encontradas += 1
    else:
        vulnerabilidades_encontradas += 1
except Exception:
    vulnerabilidades_encontradas += 1
finally:
    sock_21.close()

# Comprobación 3: Reinicio del servicio (como en tu script SSH)
try:
    pgrep_proc = subprocess.run(["pgrep", "-x", "vsftpd"], capture_output=True, text=True)
    pids = pgrep_proc.stdout.strip().split('\n')
    vsftpd_pid = pids[0] if pids[0] else None

    if not vsftpd_pid:
        vulnerabilidades_encontradas += 1
    else:
        # Comparamos si el proceso es más nuevo que el archivo de configuración modificado
        config_time = os.path.getmtime('/etc/vsftpd.conf')
        process_time = os.path.getmtime(f'/proc/{vsftpd_pid}')
        
        if config_time > process_time:
            vulnerabilidades_encontradas += 1
except Exception:
    vulnerabilidades_encontradas += 1

# Evaluación final
if vulnerabilidades_encontradas > 0:
    sys.exit(1)
else:
    sys.exit(0)
