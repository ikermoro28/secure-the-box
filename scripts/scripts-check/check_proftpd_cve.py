#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket

vulnerabilidades_encontradas = 0

# Comprobación: Banner de ProFTPD y Explotación
sock_21 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_21.settimeout(2)
try:
    if sock_21.connect_ex(('127.0.0.1', 21)) == 0:
        banner = sock_21.recv(1024).decode()
        
        # ¿Sigue el banner de la versión 1.3.5 vulnerable?
        if "ProFTPD 1.3.5" in banner:
            vulnerabilidades_encontradas += 1
            
            # Intentamos explotar la vulnerabilidad de copia
            sock_21.send(b"SITE CPFR /etc/passwd\r\n")
            resp1 = sock_21.recv(1024).decode()
            sock_21.send(b"SITE CPTO /var/www/html/shell.php\r\n")
            resp2 = sock_21.recv(1024).decode()
            
            if "250 Copy successful" in resp2:
                vulnerabilidades_encontradas += 1
    else:
        vulnerabilidades_encontradas += 1
except Exception:
    vulnerabilidades_encontradas += 1
finally:
    sock_21.close()

# Evaluación final
if vulnerabilidades_encontradas > 0:
    sys.exit(1)
else:
    sys.exit(0)
