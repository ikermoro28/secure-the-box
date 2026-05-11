#!/bin/bash

# Capturamos el nombre de usuario
USER_NAME=${1:-admin}

# 1. Crear el usuario y configurar sudo
useradd -m -s /bin/bash "$USER_NAME"
echo "$USER_NAME:stb2024" | chpasswd
usermod -aG sudo "$USER_NAME"

echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME
chmod 440 /etc/sudoers.d/$USER_NAME
touch "/home/$USER_NAME/.sudo_as_admin_successful"
chown "$USER_NAME:$USER_NAME" "/home/$USER_NAME/.sudo_as_admin_successful"
echo "$USER_NAME" > /tmp/terminal_user.txt

# =====================================================================
# 2. TRUCO DE INMERSIÓN: SIMULAR POWERSHELL EN BASH
# =====================================================================
cat << EOF >> "/home/$USER_NAME/.bashrc"

update_prompt() {
    local current_dir=\$(pwd)
    if [[ "\$current_dir" == /home/$USER_NAME* ]]; then
        local fake_path="C:\Users\\$USER_NAME\${current_dir#/home/$USER_NAME}"
    elif [[ "\$current_dir" == / ]]; then
        local fake_path="C:\\\\"
    else
        local fake_path="C:\${current_dir}"
    fi
    # Reemplazar barras normales por barras invertidas
    fake_path=\$(echo "\$fake_path" | sed 's|/|\\\\|g')
    export PS1="\[\e[36m\]PS \${fake_path}>\[\e[0m\] "
}
export PROMPT_COMMAND=update_prompt

# Alias para comandos de Windows
alias dir="ls -la"
alias cls="clear"
alias type="cat"
EOF

# =====================================================================
# 3. CREACIÓN DE EVIDENCIAS (Estructura Windows - Event Logs)
# =====================================================================
# Simulamos la ruta real de los logs de eventos de Windows
EVIDENCE_DIR="/Windows/System32/winevt/Logs/Triage_USB"
mkdir -p "$EVIDENCE_DIR/Recent_files"

cat << 'EOF' > "$EVIDENCE_DIR/setupapi.dev.log"
>>>  [Device Install (Hardware initiated) - USB\VID_0781&PID_5581\010111222333]
>>>  Section start 2023/10/25 14:00:00.000
      dvi: {Build Driver List}
      dvi:      Found Driver: disk.inf
<<<  Section end 2023/10/25 14:00:05.000
>>>  [Device Install - SWD\WPDBUSENUM\_??_USBSTOR#Disk&Ven_SanDisk&Prod_Cruzer...]
EOF

cat << 'EOF' > "$EVIDENCE_DIR/mounted_devices.txt"
\DosDevices\C: -> \Device\HarddiskVolume1
\DosDevices\E: -> \Device\HarddiskVolume2 (USBSTOR\Disk&Ven_SanDisk&Prod_Cruzer)
EOF

cat << 'EOF' > "$EVIDENCE_DIR/autorun.inf"
[autorun]
open=sysupdate.exe
icon=usb.ico
action=Open folder to view files
EOF

touch "$EVIDENCE_DIR/Recent_files/Factura_Octubre.pdf.lnk"
touch "$EVIDENCE_DIR/Recent_files/sysupdate.exe.lnk"

cat << 'EOF' > "$EVIDENCE_DIR/Windows_Defender.log"
2023-10-25 14:01:12 - SCAN_START
2023-10-25 14:01:15 - THREAT_DETECTED: Trojan:Win32/AutoRun.A
2023-10-25 14:01:15 - FILE: E:\sysupdate.exe
2023-10-25 14:01:16 - ACTION: QUARANTINE_FAILED (File in use by system)
EOF

# Damos permisos para que el jugador pueda leer la carpeta simulada de Windows
chown -R "$USER_NAME:$USER_NAME" /Windows

# =====================================================================
# 4. INFECCIÓN DEL SISTEMA (El reto práctico)
# =====================================================================
mkdir -p /ProgramData
echo '#!/bin/bash' > /ProgramData/sysupdate.exe
echo 'echo "Conectando al C2..." >> /tmp/malware_activity.log' >> /ProgramData/sysupdate.exe
chmod +x /ProgramData/sysupdate.exe

# Persistencia simulando Tareas Programadas de Windows
echo "* * * * * root /ProgramData/sysupdate.exe" > /etc/cron.d/Windows_Task_Scheduler
chmod 644 /etc/cron.d/Windows_Task_Scheduler

service cron start > /dev/null 2>&1
