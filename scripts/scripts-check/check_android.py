#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re

vulnerabilidades_encontradas = 0

# =========================================================
# COMPROBACIÓN 1
# ¿ADB sigue habilitado?
# =========================================================

settings_file = "/opt/case/filesystem/settings_global.xml"

try:
    with open(settings_file, "r") as f:
        contenido = f.read().lower()

    if 'name="adb_enabled" value="1"' in contenido:
        vulnerabilidades_encontradas += 1

    if 'name="adb_wifi_enabled" value="1"' in contenido:
        vulnerabilidades_encontradas += 1

except Exception:
    vulnerabilidades_encontradas += 1

# =========================================================
# COMPROBACIÓN 2
# ¿Sigue existiendo el malware?
# =========================================================

malware_path = "/opt/case/filesystem/data/app/com.system.update"

if os.path.exists(malware_path):
    vulnerabilidades_encontradas += 1

# =========================================================
# COMPROBACIÓN 3
# IOC REPORT
# =========================================================

usuarios_home = [
    d for d in os.listdir("/home")
    if os.path.isdir(os.path.join("/home", d))
]

ioc_ok = False

for usuario in usuarios_home:

    report_path = f"/home/{usuario}/ioc-report.txt"

    if not os.path.exists(report_path):
        continue

    try:
        with open(report_path, "r") as f:
            contenido = f.read().lower()

        ip_ok = "185.220.101.44" in contenido
        dominio_ok = "api.sync-cloud.com" in contenido
        paquete_ok = "com.system.update" in contenido

        if ip_ok and dominio_ok and paquete_ok:
            ioc_ok = True
            break

    except Exception:
        pass

if not ioc_ok:
    vulnerabilidades_encontradas += 1

# =========================================================
# RESULTADO FINAL
# =========================================================

if vulnerabilidades_encontradas > 0:
    sys.exit(1)
else:
    sys.exit(0)
