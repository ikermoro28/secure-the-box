#!/bin/bash

# Inicializamos las variables asumiendo que está seguro
ROOT_PASS_EMPTY=0
SSH_ROOT_LOGIN=0
SSH_EMPTY_PASS=0

# Comprobación 1: ¿La contraseña de root está vacía ('NP' = No Password)?
ESTADO_PASS=$(passwd -S root 2>/dev/null | awk '{print $2}')
if [ "$ESTADO_PASS" == "NP" ]; then
    ROOT_PASS_EMPTY=1
fi

# Comprobación 2: ¿SSH permite el login de root directo?
# USAMOS LA RUTA COMPLETA: /usr/sbin/sshd
if /usr/sbin/sshd -T 2>/dev/null | grep -qi "permitrootlogin yes"; then
    SSH_ROOT_LOGIN=1
fi

# Comprobación 3: ¿SSH permite contraseñas vacías?
# USAMOS LA RUTA COMPLETA: /usr/sbin/sshd
if /usr/sbin/sshd -T 2>/dev/null | grep -qi "permitemptypasswords yes"; then
    SSH_EMPTY_PASS=1
fi

# Evaluación final: Si los tres fallos coexisten, la puerta sigue abierta
if [ $ROOT_PASS_EMPTY -eq 1 ] || [ $SSH_ROOT_LOGIN -eq 1 ] || [ $SSH_EMPTY_PASS -eq 1 ]; then
    echo "❌ ERROR: El sistema sigue vulnerable. ¡Se puede acceder como 'root' sin contraseña por SSH!"
    exit 1
else
    # Si el jugador ha puesto contraseña a root, o ha modificado el sshd_config...
    echo "✅ ¡Vulnerabilidad parcheada con éxito!"
    echo "Has asegurado el acceso de superusuario. Has ganado X puntos"
    exit 0
fi
