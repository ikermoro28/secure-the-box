#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import sys

vulnerabilidades_encontradas = 0

# Comprobación 1: ¿La contraseña de root está vacía?
try:
    passwd_proc = subprocess.run(["passwd", "-S", "root"], capture_output=True, text=True)
    if passwd_proc.stdout:
        # El formato de salida es algo como "root NP 10/12/2023 0 99999 7 -1"
        partes = passwd_proc.stdout.strip().split()
        if len(partes) > 1 and partes[1] == "NP":
            vulnerabilidades_encontradas += 1
except Exception:
    pass

# Extraemos la configuración de sshd en memoria para las comprobaciones 2 y 3
sshd_config_out = ""
try:
    sshd_proc = subprocess.run(["/usr/sbin/sshd", "-T"], capture_output=True, text=True)
    sshd_config_out = sshd_proc.stdout.lower()
except Exception:
    pass

# Comprobación 2: ¿SSH permite el login de root directo?
if "permitrootlogin yes" in sshd_config_out:
    vulnerabilidades_encontradas += 1

# Comprobación 3: ¿SSH permite contraseñas vacías?
if "permitemptypasswords yes" in sshd_config_out:
    vulnerabilidades_encontradas += 1

# Comprobación 4 y 5: Estado del servicio y reinicio
try:
    # Buscamos el PID de sshd
    pgrep_proc = subprocess.run(["pgrep", "-x", "sshd"], capture_output=True, text=True)
    pids = pgrep_proc.stdout.strip().split('\n')
    sshd_pid = pids[0] if pids[0] else None

    if not sshd_pid:
        # El servicio no está corriendo
        vulnerabilidades_encontradas += 1
    else:
        # Comparamos la marca de tiempo (archivo vs proceso en memoria)
        # os.path.getmtime es el equivalente directo a stat -c %Y
        config_time = os.path.getmtime('/etc/ssh/sshd_config')
        process_time = os.path.getmtime(f'/proc/{sshd_pid}')
        
        if config_time > process_time:
            # El archivo fue modificado pero el servicio no se ha reiniciado
            vulnerabilidades_encontradas += 1
except Exception:
    # Si pgrep falla o no hay permisos para leer /proc, lo marcamos como vulnerable
    vulnerabilidades_encontradas += 1

# Evaluación final
print("\n🔒 RESULTADO DE AUDITORÍA DE SEGURIDAD")

if vulnerabilidades_encontradas > 0:
    print("\n❌ SISTEMA VULNERABLE\n")
    print("Se han detectado brechas de seguridad activas\n")
    sys.exit(1)
else:
    print("\n✅ SISTEMA SEGURO\n")
    print("No se han detectado vulnerabilidades activas\n")
    sys.exit(0)
