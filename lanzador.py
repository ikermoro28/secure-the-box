#!/usr/bin/env python3
import os
import subprocess
import sys
import sqlite3

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
        print("Opción no válida. Debes introducir 1, 2 o 3.")
        sys.exit(1)
        
    # --- NUEVA LÓGICA: Python consulta la base de datos ---
    print("\n[+] Buscando un escenario aleatorio...")
    try:
        conexion = sqlite3.connect('sqlite-scripts.db')
        cursor = conexion.cursor()
        # Buscamos 1 script al azar según la dificultad
        cursor.execute("SELECT ruta_script FROM scripts WHERE nivel_dificultad = ? ORDER BY RANDOM() LIMIT 1", (dificultad,))
        resultado = cursor.fetchone()
        conexion.close()
        
        if not resultado:
            print(f"Error: No se ha encontrado ningún script para la dificultad {dificultad}.")
            sys.exit(1)
            
        ruta_script = resultado[0]
        
        if not os.path.exists(ruta_script):
            print(f"Error: El script {ruta_script} está en la base de datos pero el archivo no existe físicamente.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        sys.exit(1)

    # --- LÓGICA DE DOCKER ---
    print("[+] Comprobando/Construyendo la imagen base...")
    subprocess.run(["docker", "build", "-q", "-t", "secure-the-box", "."], check=True)
    
    nombre_contenedor = "maquina_reto"
    
    # 1. Levantamos el contenedor en segundo plano (-d) sin montarle ningún volumen
    print(f"[+] Levantando el entorno...")
    subprocess.run(["docker", "run", "-d", "-it", "--name", nombre_contenedor, "secure-the-box", "/bin/bash"], stdout=subprocess.DEVNULL)
    
    try:
        # 2. Copiamos SOLO el script elegido dentro del contenedor en una carpeta temporal
        subprocess.run(["docker", "cp", ruta_script, f"{nombre_contenedor}:/tmp/setup.sh"])
        
        # 3. Lo ejecutamos y lo BORRAMOS inmediatamente después
        print(f"[+] Preparando el escenario en absoluto secreto...")
        comando_setup = "bash /tmp/setup.sh && rm -f /tmp/setup.sh"
        subprocess.run(["docker", "exec", nombre_contenedor, "/bin/bash", "-c", comando_setup])
        
        # 4. Le damos el control interactivo al usuario
        print("[+] Máquina preparada. ¡Buena suerte!\n")
        subprocess.run(["docker", "exec", "-it", nombre_contenedor, "/bin/bash"])
        
    finally:
        # 5. Cuando el usuario escriba 'exit', destruimos el contenedor para no dejar basura
        print("\n[+] Destruyendo el contenedor y limpiando el entorno...")
        subprocess.run(["docker", "rm", "-f", nombre_contenedor], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
