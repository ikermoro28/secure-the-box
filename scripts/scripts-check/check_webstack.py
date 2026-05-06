import urllib.request
import urllib.parse
import sys

def check_security():
    url = 'http://localhost/index.php'
    
    # TEST 1: Comprobar que la web funciona (Funcionalidad legítima)
    try:
        data_normal = urllib.parse.urlencode({'ip': '127.0.0.1'}).encode('utf-8')
        req_normal = urllib.request.Request(url, data=data_normal)
        res_normal = urllib.request.urlopen(req_normal)
        html_normal = res_normal.read().decode('utf-8')
        
        # Comprobamos que el comando ping normal sigue generando salida en el HTML
        if "127.0.0.1" not in html_normal or "ping" not in html_normal.lower():
            sys.exit(1)
            
    except Exception as e:
        sys.exit(1)

    # TEST 2: Comprobar la vulnerabilidad de Command Injection
    try:
        # CAMBIO CLAVE: Partimos la cadena en el payload. 
        # Si hay inyección real, Bash la concatenará y devolverá "STB_VULN_TEST_ACTIVA".
        # Si es un falso positivo por reflejo de error, devolverá literalmente lo introducido.
        payload = "127.0.0.1; echo 'STB_VULN_''TEST_ACTIVA'"
        data_vuln = urllib.parse.urlencode({'ip': payload}).encode('utf-8')
        req_vuln = urllib.request.Request(url, data=data_vuln)
        res_vuln = urllib.request.urlopen(req_vuln)
        html_vuln = res_vuln.read().decode('utf-8')
        
        # Si el texto aparece concatenado, significa que el comando 'echo' logró ejecutarse en Bash
        if "STB_VULN_TEST_ACTIVA" in html_vuln:
            sys.exit(1)
            
    except Exception as e:
        pass

    # Si pasamos el Test 1 y fallamos en inyectar en el Test 2, el reto está superado
    sys.exit(0)

if __name__ == "__main__":
    check_security()
