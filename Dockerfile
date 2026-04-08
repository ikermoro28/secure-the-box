# Usamos Ubuntu 24.04 como base
FROM ubuntu:24.04

# Evitamos que la instalación nos pida confirmaciones interactivas
ENV DEBIAN_FRONTEND=noninteractive

# Instalamos SQLite3 para que Docker pueda leer tu base de datos
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo donde montaremos tu proyecto
WORKDIR /app

# El ENTRYPOINT ejecuta la lógica al arrancar:
# 1. Busca el script aleatorio según la dificultad en sqlite-scripts.db
# 2. Le da permisos de ejecución
# 3. Lo ejecuta y luego te da acceso a la terminal (/bin/bash)
ENTRYPOINT ["/bin/bash", "-c", "\
    echo '[+] Buscando un escenario aleatorio para la dificultad $DIFICULTAD...'; \
    RUTA_ELEGIDA=$(sqlite3 sqlite-scripts.db \"SELECT ruta_script FROM scripts WHERE nivel_dificultad = $DIFICULTAD ORDER BY RANDOM() LIMIT 1;\"); \
    if [ -z \"$RUTA_ELEGIDA\" ]; then \
        echo '❌ Error: No se ha encontrado ningún script para la dificultad $DIFICULTAD en la base de datos.'; \
        exit 1; \
    fi; \
    echo '[+] Escenario seleccionado: $RUTA_ELEGIDA'; \
    chmod +x \"$RUTA_ELEGIDA\"; \
    \"$RUTA_ELEGIDA\"; \
    echo '[+] Máquina preparada. ¡Buena suerte!'; \
    /bin/bash \
"]
