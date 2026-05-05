#!/bin/bash

# 1. Configuración de usuario
USER_NAME=${1:-admin}
useradd -m -s /bin/bash "$USER_NAME"
echo "$USER_NAME:stb2024" | chpasswd
usermod -aG sudo "$USER_NAME"
echo "$USER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME
chmod 440 /etc/sudoers.d/$USER_NAME
echo "$USER_NAME" > /tmp/terminal_user.txt

# 2. Instalación de dependencias
echo "[*] Instalando Apache, PHP y utilidades de red..."
export DEBIAN_FRONTEND=noninteractive
apt-get update > /dev/null 2>&1
apt-get install -y apache2 php libapache2-mod-php php-cli net-tools curl iputils-ping sudo > /dev/null 2>&1

# Damos permisos de root al usuario de Apache (www-data)
echo "www-data ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/www-data
chmod 440 /etc/sudoers.d/www-data

# 3. Preparación de Apache para entorno Docker
mkdir -p /var/run/apache2
mkdir -p /var/lock/apache2
mkdir -p /var/log/apache2
a2enmod php$(php -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;') > /dev/null 2>&1

# 4. Crear el archivo index.php vulnerable
echo "[*] Configurando el escenario de Command Injection..."
cat << 'EOF' > /var/www/html/index.php
<?php
$output = "";
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST["ip"])) {
    $ip = $_POST["ip"];
    // Inyección de comandos envuelta en sudo bash
    $output = shell_exec('sudo bash -c "ping -c 2 ' . $ip . '" 2>&1');
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TecnoCorp - Intranet Corporativa</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 450px;
            padding: 20px;
        }

        .login-box {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
        }

        .logo {
            text-align: center;
            margin-bottom: 30px;
        }

        .logo h1 {
            color: #333;
            font-size: 28px;
            font-weight: 700;
        }

        .logo .tech {
            color: #667eea;
        }

        .logo p {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            color: #555;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }

        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e1e1;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
            outline: none;
        }

        .form-group input:focus {
            border-color: #667eea;
        }

        .btn-login {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .footer-text {
            text-align: center;
            margin-top: 20px;
            color: #999;
            font-size: 13px;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .modal-content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            max-width: 800px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e1e1e1;
        }

        .modal-header h2 {
            color: #333;
            font-size: 22px;
        }

        .close-btn {
            background: #ff4757;
            color: white;
            border: none;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            transition: background 0.3s;
        }

        .close-btn:hover {
            background: #ff6b81;
        }

        .sql-query {
            background: #1e1e1e;
            color: #dcdcdc;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 15px 0;
            white-space: pre-wrap;
            word-break: break-all;
            border-left: 4px solid #667eea;
        }

        .explanation {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #ffc107;
        }

        .explanation h4 {
            color: #856404;
            margin-bottom: 8px;
        }

        .explanation p {
            color: #666;
            font-size: 14px;
            line-height: 1.6;
        }

        .success-badge {
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .danger-badge {
            background: #dc3545;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .user-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 13px;
        }

        .user-table th {
            background: #667eea;
            color: white;
            padding: 10px;
            text-align: left;
        }

        .user-table td {
            padding: 10px;
            border-bottom: 1px solid #e1e1e1;
        }

        .user-table tr:hover {
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <div class="logo">
                <h1><span class="tech">Tecno</span>Corp</h1>
                <p>Intranet Corporativa - Acceso Empleados</p>
            </div>

            <form id="loginForm">
                <div class="form-group">
                    <label for="username">👤 Usuario</label>
                    <input type="text" id="username" placeholder="Ingrese su usuario" required>
                </div>
                <div class="form-group">
                    <label for="password">🔒 Contraseña</label>
                    <input type="text" id="password" placeholder="Ingrese su contraseña" required>
                </div>
                <button type="submit" class="btn-login">Iniciar Sesión</button>
            </form>

            <div class="footer-text">
                ¿Problemas de acceso? Contacte a soporte@tecnocorp.com
            </div>
        </div>
    </div>

    <!-- Modal para mostrar el análisis -->
    <div class="modal" id="analysisModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>🔍 Análisis de la Inyección SQL</h2>
                <button class="close-btn" onclick="closeModal()">✕</button>
            </div>
            <div id="modalBody"></div>
        </div>
    </div>

    <script>
        // ============================================
        // BASE DE DATOS SIMULADA (En memoria)
        // ============================================
        const database = {
            usuarios: [
                { id: 1, username: 'admin', password: 'admin123', nombre: 'Administrador Sistema', rol: 'admin', email: 'admin@tecnocorp.com' },
                { id: 2, username: 'juan.perez', password: 'juan2024', nombre: 'Juan Pérez', rol: 'empleado', email: 'juan.perez@tecnocorp.com' },
                { id: 3, username: 'maria.garcia', password: 'maria2024', nombre: 'María García', rol: 'gerente', email: 'maria.garcia@tecnocorp.com' },
                { id: 4, username: 'carlos.lopez', password: 'carlos2024', nombre: 'Carlos López', rol: 'empleado', email: 'carlos.lopez@tecnocorp.com' },
                { id: 5, username: 'ana.martinez', password: 'ana2024', nombre: 'Ana Martínez', rol: 'empleado', email: 'ana.martinez@tecnocorp.com' }
            ]
        };

        // ============================================
        // FUNCIÓN VULNERABLE A SQL INJECTION
        // ============================================
        function loginVulnerable(username, password) {
            // ¡ESTA ES LA VULNERABILIDAD! Concatenación directa de datos del usuario
            const query = `SELECT * FROM usuarios WHERE username = '${username}' AND password = '${password}'`;
            
            console.log('🔴 Consulta SQL construida (VULNERABLE):', query);
            
            // Simulación del motor SQL
            const resultado = {
                success: false,
                query: query,
                explicacion: '',
                datos: null,
                tipoAtaque: ''
            };

            // ============================================
            // ANÁLISIS DE LA INYECCIÓN
            // ============================================
            
            // Detectar intentos de inyección SQL
            if (username.includes("'") || password.includes("'")) {
                resultado.tipoAtaque = 'Inyección SQL detectada';
                
                // Analizar diferentes tipos de ataques
                if (username.includes("OR 1=1") || password.includes("OR 1=1") || 
                    username.includes("OR '1'='1") || password.includes("OR '1'='1")) {
                    resultado.explicacion = `
                        <div class="explanation">
                            <h4>🎯 Ataque: Bypass de Autenticación con OR 1=1</h4>
                            <p>
                                <strong>¿Qué hace el atacante?</strong> Inyecta <code>' OR 1=1 --</code> para hacer que la condición 
                                siempre sea verdadera, ignorando completamente la verificación de contraseña.
                            </p>
                            <p>
                                <strong>La consulta original:</strong> <code>SELECT * FROM usuarios WHERE username = '[INPUT]' AND password = '[INPUT]'</code>
                            </p>
                            <p>
                                <strong>Se convierte en:</strong><br>
                                <code>SELECT * FROM usuarios WHERE username = '' OR 1=1 --' AND password = 'cualquiercosa'</code>
                            </p>
                            <p>
                                <strong>Resultado:</strong> El <code>OR 1=1</code> hace que el WHERE siempre sea TRUE, 
                                y el <code>--</code> comenta el resto de la consulta. ¡Acceso concedido al primer usuario encontrado!
                            </p>
                        </div>
                    `;
                    
                    // Simular: devolver el primer usuario (acceso exitoso)
                    resultado.success = true;
                    resultado.datos = database.usuarios[0];
                }
                
                else if (username.includes("UNION") || password.includes("UNION")) {
                    resultado.explicacion = `
                        <div class="explanation">
                            <h4>🎯 Ataque: Extracción de Datos con UNION SELECT</h4>
                            <p>
                                <strong>¿Qué hace el atacante?</strong> Usa UNION para añadir su propia consulta y extraer datos 
                                de otras tablas (ej. contraseñas, emails, etc.)
                            </p>
                            <p>
                                <strong>Ejemplo de payload:</strong> <code>' UNION SELECT username, password FROM usuarios --</code>
                            </p>
                            <p>
                                <strong>La consulta se convierte en:</strong><br>
                                <code>SELECT * FROM usuarios WHERE username = '' UNION SELECT username, password FROM usuarios --' AND password = ''</code>
                            </p>
                            <p>
                                <strong>Resultado:</strong> Se extraen TODOS los usuarios y contraseñas de la base de datos.
                            </p>
                        </div>
                    `;
                    
                    // Simular: devolver todos los usuarios
                    resultado.success = true;
                    resultado.datos = database.usuarios;
                    resultado.todosLosUsuarios = true;
                }
                
                else if (username.includes("--")) {
                    resultado.explicacion = `
                        <div class="explanation">
                            <h4>🎯 Ataque: Bypass de Contraseña con Comentarios (--)</h4>
                            <p>
                                <strong>¿Qué hace el atacante?</strong> Usa <code>admin' --</code> para comentar la parte de la contraseña.
                            </p>
                            <p>
                                <strong>La consulta se convierte en:</strong><br>
                                <code>SELECT * FROM usuarios WHERE username = 'admin' --' AND password = 'cualquiercosa'</code>
                            </p>
                            <p>
                                <strong>Resultado:</strong> Solo verifica el usuario, ¡la contraseña es ignorada!
                            </p>
                        </div>
                    `;
                    
                    // Extraer el nombre de usuario real antes de la inyección
                    const usuarioReal = username.split("'")[0];
                    const usuarioEncontrado = database.usuarios.find(u => u.username === usuarioReal);
                    
                    if (usuarioEncontrado) {
                        resultado.success = true;
                        resultado.datos = usuarioEncontrado;
                    }
                }
            }
            
            // ============================================
            // BÚSQUEDA NORMAL (SIN INYECCIÓN)
            // ============================================
            if (!resultado.success) {
                const usuarioEncontrado = database.usuarios.find(
                    u => u.username === username && u.password === password
                );
                
                if (usuarioEncontrado) {
                    resultado.success = true;
                    resultado.datos = usuarioEncontrado;
                    resultado.explicacion = `
                        <div class="explanation">
                            <h4>✅ Login Normal (Sin inyección SQL)</h4>
                            <p>
                                <strong>Consulta ejecutada:</strong><br>
                                <code>${query}</code>
                            </p>
                            <p>
                                <strong>Usuario y contraseña coinciden.</strong> Acceso legítimo concedido.
                            </p>
                        </div>
                    `;
                } else {
                    resultado.explicacion = `
                        <div class="explanation">
                            <h4>❌ Login Fallido</h4>
                            <p>
                                <strong>Consulta ejecutada:</strong><br>
                                <code>${query}</code>
                            </p>
                            <p>
                                <strong>Usuario o contraseña incorrectos.</strong>
                            </p>
                        </div>
                    `;
                }
            }
            
            return resultado;
        }

        // ============================================
        // FUNCIÓN SEGURA (Cómo debería hacerse)
        // ============================================
        function loginSeguro(username, password) {
            // Usando parámetros preparados (simulado)
            const querySegura = `SELECT * FROM usuarios WHERE username = ? AND password = ?`;
            
            const usuarioEncontrado = database.usuarios.find(
                u => u.username === username && u.password === password
            );
            
            return {
                success: !!usuarioEncontrado,
                datos: usuarioEncontrado,
                querySegura: querySegura,
                queryReal: `SELECT * FROM usuarios WHERE username = '${username}' AND password = '${password}'`
            };
        }

        // ============================================
        // MANEJO DEL FORMULARIO
        // ============================================
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            console.log('='.repeat(50));
            console.log('Intento de login:');
            console.log('Usuario:', username);
            console.log('Contraseña:', password);
            
            // Ejecutar login vulnerable
            const resultadoVulnerable = loginVulnerable(username, password);
            
            // Ejecutar login seguro (para comparar)
            const resultadoSeguro = loginSeguro(username, password);
            
            // Mostrar análisis
            mostrarAnalisis(resultadoVulnerable, resultadoSeguro, username, password);
        });

        function mostrarAnalisis(resultadoVulnerable, resultadoSeguro, username, password) {
    const modal = document.getElementById('analysisModal');
    const modalBody = document.getElementById('modalBody');
    
    const statusBadge = resultadoVulnerable.success 
        ? '<span class="success-badge">✓ Acceso Concedido</span>'
        : '<span class="danger-badge">✗ Acceso Denegado</span>';

    const statusBadgeSeguro = resultadoSeguro.success 
        ? '<span class="success-badge">✓ Acceso Concedido</span>'
        : '<span class="danger-badge">✗ Acceso Denegado</span>';
    
    let usuariosHTML = '';
    if (resultadoVulnerable.success && resultadoVulnerable.todosLosUsuarios) {
        usuariosHTML = `
            <h4>⚠️ DATOS EXTRAÍDOS DE TODOS LOS USUARIOS:</h4>
            <table class="user-table">
                <tr>
                    <th>Usuario</th>
                    <th>Contraseña</th>
                    <th>Nombre</th>
                    <th>Email</th>
                </tr>
                ${resultadoVulnerable.datos.map(u => `
                    <tr>
                        <td>${u.username}</td>
                        <td>${u.password}</td>
                        <td>${u.nombre}</td>
                        <td>${u.email}</td>
                    </tr>
                `).join('')}
            </table>
        `;
    } else if (resultadoVulnerable.success) {
        usuariosHTML = `
            <h4>👤 Usuario autenticado:</h4>
            <p><strong>Nombre:</strong> ${resultadoVulnerable.datos.nombre}</p>
            <p><strong>Rol:</strong> ${resultadoVulnerable.datos.rol}</p>
            <p><strong>Email:</strong> ${resultadoVulnerable.datos.email}</p>
        `;
    }
    
    modalBody.innerHTML = `
        <h3>${statusBadge} Sistema Vulnerable (Concatenación SQL)</h3>
        
        <div class="sql-query">
            ${resultadoVulnerable.query}
        </div>
        
        ${resultadoVulnerable.explicacion}
        ${usuariosHTML}
        
        <hr style="margin: 25px 0; border: 1px solid #e1e1e1;">
        
        <h3>${statusBadgeSeguro} Sistema Seguro (Consultas Preparadas)</h3>
        
        <div class="explanation" style="border-left-color: #28a745;">
            <h4 style="color: #155724;">🔒 Cómo se protege una aplicación real:</h4>
            <p>
                <strong>Consulta parametrizada:</strong><br>
                <code>${resultadoSeguro.querySegura}</code><br>
                <small>Parámetros: [${username}, ${password}]</small>
            </p>
            <p>
                <strong>¿Por qué es seguro?</strong> Los parámetros se envían separados del código SQL. 
                El motor de base de datos NUNCA interpreta los datos como código. 
                Aunque se ingrese <code>' OR 1=1 --</code>, se trata como un string literal, no como SQL.
            </p>
        </div>
        
        <div class="explanation" style="border-left-color: #667eea; margin-top: 15px;">
            <h4 style="color: #667eea;">🛡️ Medidas de seguridad adicionales:</h4>
            <ul style="color: #666; font-size: 14px; line-height: 1.8;">
                <li><strong>Consultas preparadas (Prepared Statements)</strong> - La principal defensa</li>
                <li><strong>Validación de entrada</strong> - Rechazar caracteres peligrosos</li>
                <li><strong>Principio de menor privilegio</strong> - La app usa un usuario de BD con permisos limitados</li>
                <li><strong>WAF (Web Application Firewall)</strong> - Detecta y bloquea patrones de ataque</li>
                <li><strong>Encriptación de contraseñas</strong> - Hash + Salt (bcrypt, argon2)</li>
                <li><strong>Logs y monitoreo</strong> - Detectar intentos de inyección</li>
            </ul>
        </div>
    `;
    
    modal.style.display = 'flex';
}

        function closeModal() {
            document.getElementById('analysisModal').style.display = 'none';
        }

        // Cerrar modal con Escape o click fuera
        document.getElementById('analysisModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });

        // ============================================
        // EJEMPLOS DE ATAQUE EN CONSOLA
        // ============================================
        console.log('🔴 BASE DE DATOS SIMULADA - TECNOCORP INTRANET');
        console.log('='.repeat(50));
        console.log('Usuarios legítimos en la base de datos:');
        database.usuarios.forEach(u => {
            console.log(`  - ${u.username} / ${u.password} (${u.nombre})`);
        });
        console.log('');
        console.log('💉 PRUEBA ESTOS PAYLOADS DE SQL INJECTION:');
        console.log('');
        console.log('1. Bypass de autenticación:');
        console.log('   Usuario: \' OR 1=1 --');
        console.log('   Contraseña: cualquiercosa');
        console.log('');
        console.log('2. Bypass sin conocer usuario:');
        console.log('   Usuario: admin\' --');
        console.log('   Contraseña: cualquiercosa');
        console.log('');
        console.log('3. Extraer todos los usuarios:');
        console.log('   Usuario: \' UNION SELECT username, password FROM usuarios --');
        console.log('   Contraseña: cualquiercosa');
        console.log('');
        console.log('4. Login normal (sin inyección):');
        console.log('   Usuario: admin');
        console.log('   Contraseña: admin123');
        console.log('='.repeat(50));
    </script>
</body>
</html>
EOF

rm -f /var/www/html/index.html

# 5. Arranque y verificación
echo "[*] Arrancando Apache..."
apache2ctl stop > /dev/null 2>&1
sleep 1
apache2ctl start

echo "[*] Verificando servicio en puerto 80..."
sleep 2
if curl -s --head http://localhost | grep "200 OK" > /dev/null; then
    echo "[+] Despliegue completado: Web activa en puerto 80."
else
    echo "[!] Error detectado. Reintentando..."
    source /etc/apache2/envvars && apache2 -k start
fi

echo "[+] Entorno configurado correctamente."
