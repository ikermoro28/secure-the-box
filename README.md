# 🛡️ Secure The Box - Defensive CTF Trainer

**Secure The Box** es una plataforma de entrenamiento en ciberseguridad defensiva diseñada para practicar la fortificación de entornos Linux en tiempo real. Mediante el uso de contenedores Docker, la aplicación despliega escenarios vulnerables que el usuario debe asegurar para obtener puntos.

Este proyecto ha sido desarrollado como **Trabajo de Fin de Máster (TFM)** por **Iker Moro** y **Guillermo Jaume**.

## 📋 Información General

- **Estado:** Prototipo funcional para TFM.
- **Sistemas Soportados:** Debian y Ubuntu (basado en paquetes `.deb`).
- **Tecnologías:** Python 3, CustomTkinter, Docker, SQLite3.

## 🛠️ Instalación

Para configurar el entorno, las dependencias de Python (venv) y los permisos de Docker, descarga el proyecto y ejecuta el script de instalación:

```bash
sudo bash setup.sh
´´´
🚀 Cómo ejecutar la aplicación
Una vez finalizada la instalación, puedes iniciar la plataforma de dos maneras:

1. Desde el lanzador de aplicaciones
Busca el icono de Secure The Box en el menú de aplicaciones de tu escritorio (Gnome, KDE, etc.) e inícialo normalmente.

2. Desde la terminal (Modo manual)
Si deseas ver la salida de la consola para depuración, ejecuta:

Bash
cd secure-the-box
source venv/bin/activate
python3 app.py
📂 Estructura del Proyecto
app.py: Binario principal con la interfaz gráfica.

sqlite-scripts.db: Base de datos que gestiona los retos y los Dockerfiles.

dockerfiles/: Contiene las imágenes base (Debian 13 Trixie, Ubuntu 24.04, etc.).

retos/: Directorio con los scripts de vulneración (setup.sh) y auditoría (check.py).

✍️ Autores
Iker Moro

Guillermo Jaume

Este software ha sido desarrollado con fines educativos como parte de un Trabajo de Fin de Máster.
