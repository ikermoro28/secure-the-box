#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys

vulnerabilidades = 0

try:
    # Extraemos el "running-config" actual del router emulado en memoria
    frr_proc = subprocess.run(["vtysh", "-c", "show running-config"], capture_output=True, text=True)
    config = frr_proc.stdout
    
    # Comprobación 1: Contraseñas en texto claro ("cisco")
    # Si el alumno no ha puesto "no password cisco" y "no enable password cisco", falla.
    if "password cisco" in config or "enable password cisco" in config:
        vulnerabilidades += 1
        
    # Comprobación 2: ¿Se configuró un "enable secret"? (Contraseña fuerte)
    # Si el alumno no ha añadido una clave cifrada de enable, falla.
    if "enable secret" not in config:
        vulnerabilidades += 1
        
    # Comprobación 3: Ruta estática maliciosa a una IP desconocida (192.168.66.6)
    # Si el alumno no ha hecho "no ip route 0.0.0.0/0 192.168.66.6", falla.
    if "ip route 0.0.0.0/0 192.168.66.6" in config:
        vulnerabilidades += 1

except Exception:
    # Si hay un error al conectar con la CLI del router, se considera entorno vulnerable/roto
    vulnerabilidades += 1

# Decisión final que app.py leerá de forma interna mediante el código de salida
if vulnerabilidades > 0:
    sys.exit(1) # Indica a app.py que es vulnerable (mostrará sus propios logs de error)
else:
    sys.exit(0) # Indica a app.py que es seguro (mostrará sus propios logs de éxito)
