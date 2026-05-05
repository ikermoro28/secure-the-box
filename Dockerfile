# Usamos Debian 13 (Trixie) como base
FROM debian:trixie

# Evitamos prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Actualizamos e instalamos sudo y nano
RUN apt-get update && \
    apt-get install -y sudo && \
    apt-get install -y nano && \
    rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo (Home de root)
WORKDIR /root

# Mantenemos el contenedor vivo con bash
CMD ["/bin/bash"]
