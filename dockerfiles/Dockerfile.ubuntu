# Usamos Ubuntu 24.04 como base
FROM ubuntu:24.04

# Evitamos prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Solo instalamos sudo (ya no necesitamos sqlite3)
RUN apt-get update && \
    apt-get install -y sudo && \
    apt-get install -y nano && \
#    apt-get install -y openssh-server && \
    rm -rf /var/lib/apt/lists/*

# Dejamos al usuario en root al entrar
WORKDIR ~

# Simplemente mantenemos el contenedor vivo
CMD ["/bin/bash"]
