#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket

vulnerabilidades_encontradas = 0

print("[*] Iniciando comprobación de seguridad...")

# Comprobación: Banner de ProFTPD y Explotación
sock_21 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_21.settimeout(2)
try:
    if sock_21.connect_ex(('127.0.0.1', 21)) == 0:
        print("✅ Puerto 21 abierto. Leyendo banner...")
        banner = sock_21.recv(1024).decode()
        print(f"[*] Banner detectado: {banner.strip()}")
        
        # ¿Sigue el banner de la versión 1.3.5 vulnerable?
        if "ProFTPD 1.3.5" in banner:
            print("❌ ERROR: El servicio sigue siendo la versión vulnerable (ProFTPD 1.3.5).")
            vulnerabilidades_encontradas += 1
            
            # Intentamos explotar la vulnerabilidad de copia
            sock_21.send(b"SITE CPFR /etc/passwd\r\n")
            resp1 = sock_21.recv(1024).decode()
            sock_21.send(b"SITE CPTO /var/www/html/shell.php\r\n")
            resp2 = sock_21.recv(1024).decode()
            
            if "250 Copy successful" in resp2:
                print("❌ ERROR: La vulnerabilidad RCE de copia (mod_copy) es explotable.")
                vulnerabilidades_encontradas += 1
        else:
            print("✅ El servicio FTP actual está actualizado y no es la versión vulnerable.")
    else:
        print("❌ ERROR: El puerto 21 está cerrado. Debes instalar y arrancar el servidor ProFTPD legítimo.")
        vulnerabilidades_encontradas += 1
except Exception as e:
    print(f"❌ ERROR CRÍTICO AL CONECTAR AL FTP: {e}")
    vulnerabilidades_encontradas += 1
finally:
    sock_21.close()

# Evaluación final
if vulnerabilidades_encontradas > 0:
    print("\n[!] Check fallido. Se encontraron vulnerabilidades.")
    sys.exit(1)
else:
    print("\n[+] Check completado. Sistema seguro.")
    sys.exit(0)
