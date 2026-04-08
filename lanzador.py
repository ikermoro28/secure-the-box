#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    print("=========================================")
    print("      Bienvenido a Secure The Box        ")
    print("=========================================")
    print("¿En qué dificultad quieres la máquina a securizar?")
    print("  1 - Fácil")
    print("  2 - Medio")
    print("  3 - Difícil")
    
    dificultad = input("\nElige una opción (1/2/3): ").strip()
    
    if dificultad not in ['1', '2', '3']:
        print("❌ Opción no válida. Debes introducir 1, 2 o 3.")
        sys.exit(1)
        
    print("\n[+] Comprobando/Construyendo la imagen base de Docker...")
    # Construye la imagen (si no hay cambios en el Dockerfile, será instantáneo por el caché)
    subprocess.run(["docker", "build", "-q", "-t", "secure-the-box", "."], check=True)
    
    print(f"[+] Levantando el entorno (Dificultad: {dificultad})...\n")
    
    # Obtenemos la ruta actual (la raíz de tu proyecto git)
    directorio_actual = os.getcwd()
    
    # Preparamos el comando de Docker. 
    # Pasamos la dificultad como variable de entorno (-e) y montamos todo el proyecto en /app (-v)
    comando_docker = [
        "docker", "run", "-it", "--rm",
        "-e", f"DIFICULTAD={dificultad}",
        "-v", f"{directorio_actual}:/app",
        "secure-the-box"
    ]
    
    # Ejecutamos Docker. El control de la terminal pasa al contenedor.
    subprocess.run(comando_docker)

if __name__ == "__main__":
    main()
