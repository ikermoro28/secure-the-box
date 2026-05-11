#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

vulnerabilidades_encontradas = 0


# Comprobación 1: ¿Sigue existiendo el archivo malicioso base?
ruta_malware = "/ProgramData/sysupdate.exe"

if os.path.exists(ruta_malware):
    vulnerabilidades_encontradas += 1
else:

# Comprobación 2: ¿Sigue existiendo la persistencia?
ruta_persistencia = "/etc/cron.d/Windows_Task_Scheduler"

if os.path.exists(ruta_persistencia):
    vulnerabilidades_encontradas += 1

# Evaluar resultado final
if vulnerabilidades_encontradas > 0:
    sys.exit(1) # Indica a app.py que ha fallado
else:
    sys.exit(0) # Indica a app.py que es seguro
