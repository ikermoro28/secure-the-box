#!/bin/bash

# Inicializamos las variables
VULNERABILIDADES_ENCONTRADAS=0

# Comprobación 1: ¿La contraseña de root está vacía?
ESTADO_PASS=$(passwd -S root 2>/dev/null | awk '{print $2}')
if [ "$ESTADO_PASS" == "NP" ]; then
    VULNERABILIDADES_ENCONTRADAS=$((VULNERABILIDADES_ENCONTRADAS + 1))
fi

# Comprobación 2: ¿SSH permite el login de root directo?
if /usr/sbin/sshd -T 2>/dev/null | grep -qi "permitrootlogin yes"; then
    VULNERABILIDADES_ENCONTRADAS=$((VULNERABILIDADES_ENCONTRADAS + 1))
fi

# Comprobación 3: ¿SSH permite contraseñas vacías?
if /usr/sbin/sshd -T 2>/dev/null | grep -qi "permitemptypasswords yes"; then
    VULNERABILIDADES_ENCONTRADAS=$((VULNERABILIDADES_ENCONTRADAS + 1))
fi

# Comprobación 4 y 5: Estado del servicio y reinicio
SSHD_PID=$(pgrep -x sshd | head -n 1)

if [ -z "$SSHD_PID" ]; then
    # El servicio no está corriendo
    VULNERABILIDADES_ENCONTRADAS=$((VULNERABILIDADES_ENCONTRADAS + 1))
else
    # Comparamos la marca de tiempo (archivo vs proceso en memoria)
    CONFIG_TIME=$(stat -c %Y /etc/ssh/sshd_config 2>/dev/null)
    PROCESS_TIME=$(stat -c %Y /proc/$SSHD_PID 2>/dev/null)
    
    if [ "$CONFIG_TIME" -gt "$PROCESS_TIME" ]; then
        # El archivo fue modificado pero el servicio no se ha reiniciado
        VULNERABILIDADES_ENCONTRADAS=$((VULNERABILIDADES_ENCONTRADAS + 1))
    fi
fi

# Evaluación final con tu diseño original
echo ""
echo "🔒 RESULTADO DE AUDITORÍA DE SEGURIDAD"

if [ $VULNERABILIDADES_ENCONTRADAS -gt 0 ]; then
    echo ""
    echo "❌ SISTEMA VULNERABLE"
    echo ""
    echo "Se han detectado brechas de seguridad activas"
    echo ""
    exit 1
else
    echo ""
    echo "✅ SISTEMA SEGURO"
    echo ""
    echo "No se han detectado vulnerabilidades activas"
    echo ""
    exit 0
fi
