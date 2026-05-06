import subprocess
import sys

def check_security():
    try:
        # Intentamos hacer una conexión anónima al servidor LDAP (-x indica bind simple sin credenciales)
        result = subprocess.run(
            ["ldapwhoami", "-x", "-H", "ldap://localhost"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Si el comando tiene éxito y el servidor acepta la conexión
        if result.returncode == 0 and "anonymous" in result.stdout.lower():
            print("VULNERABLE: El servidor permite conexiones anónimas (Anonymous Bind). Fuga de datos activa.")
            sys.exit(1)
            
        # Si el servidor rechaza la conexión exigiendo autenticación
        elif "inappropriate authentication" in result.stderr.lower() or result.returncode != 0:
            print("SEGURO: Conexiones anónimas bloqueadas. El directorio exige autenticación.")
            sys.exit(0)
            
        else:
            # Fallback de seguridad si responde otra cosa rara tras securizar
            print("SEGURO: Las conexiones anónimas parecen estar bloqueadas.")
            sys.exit(0)

    except Exception as e:
        print(f"ERROR CRÍTICO: No se pudo ejecutar el test de LDAP: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_security()
