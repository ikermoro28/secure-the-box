import customtkinter as ctk
import os
import subprocess
import threading
import sqlite3
import json
import time

# Configuración de apariencia global
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CustomConfirmDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, callback):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.callback = callback
        self.transient(parent)
        self.grab_set()
        self.label = ctk.CTkLabel(self, text=message, wraplength=350, font=ctk.CTkFont(size=14))
        self.label.pack(pady=30)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.btn_yes = ctk.CTkButton(self.btn_frame, text="Sí, salir", fg_color="#a51f1f", 
                                    hover_color="#701414", width=120, command=self.confirm)
        self.btn_yes.grid(row=0, column=0, padx=15)

        self.btn_no = ctk.CTkButton(self.btn_frame, text="Cancelar", width=120, command=self.destroy)
        self.btn_no.grid(row=0, column=1, padx=15)

    def confirm(self):
        self.callback()
        self.destroy()

class SecureTheBoxApp(ctk.CTk):
    def __init__(self):
        super().__init__(className="Secure The Box") 
        self.puntuacion_base_actual = 0  # <--- Añade esta línea
        self.start_time = 0             # También inicializamos el tiempo
        self.title("Secure The Box - Defensive CTF Trainer")
        self.geometry("750x550") 
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variables de estado
        self.dificultad_var = ctk.StringVar(value="1")
        self.container_running = False
        self.nombre_contenedor = "maquina_reto"
        self.ruta_check_actual = None
        self.usuario_terminal_actual = "root"

        self.setup_ui()

    def setup_ui(self):
        # --- Cabecera ---
        self.label_title = ctk.CTkLabel(self, text="🛡️ SECURE THE BOX", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=20)

        # --- Selección Dificultad ---
        self.frame_diff = ctk.CTkFrame(self)
        self.frame_diff.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.frame_diff, text="Selecciona la dificultad del reto:").pack(pady=5)
        
        self.radio_frame = ctk.CTkFrame(self.frame_diff, fg_color="transparent")
        self.radio_frame.pack(pady=10)
        
        ctk.CTkRadioButton(self.radio_frame, text="Fácil (Nivel 1)", variable=self.dificultad_var, value="1").grid(row=0, column=0, padx=20)
        ctk.CTkRadioButton(self.radio_frame, text="Medio (Nivel 2)", variable=self.dificultad_var, value="2").grid(row=0, column=1, padx=20)
        ctk.CTkRadioButton(self.radio_frame, text="Difícil (Nivel 3)", variable=self.dificultad_var, value="3").grid(row=0, column=2, padx=20)

        # --- Consola ---
        self.textbox_log = ctk.CTkTextbox(self, height=200, width=650, font=("Consolas", 12))
        self.textbox_log.pack(pady=10, padx=20)
        self.log("Sistema iniciado. Esperando selección de reto...")

        # --- Botonera Principal Dinámica ---
        self.frame_buttons = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_buttons.pack(pady=20)

        # Botones Normales
        self.btn_launch = ctk.CTkButton(self.frame_buttons, text="🚀 DESPLEGAR ESCENARIO", width=220, 
                                        command=self.start_launch_thread, font=ctk.CTkFont(weight="bold"))
        self.btn_launch.grid(row=0, column=0, padx=10)

        self.btn_stop = ctk.CTkButton(self.frame_buttons, text="⏹ DETENER RETO", width=220, 
                                      command=self.show_inline_confirmation, fg_color="#a51f1f", 
                                      hover_color="#701414", font=ctk.CTkFont(weight="bold"), state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=10)

        # Botón de Comprobación (Oculto al inicio)
        self.btn_check = ctk.CTkButton(self.frame_buttons, text="✅ COMPROBAR SEGURIDAD", width=220, 
                                      command=self.start_check_thread, fg_color="#28a745", 
                                      hover_color="#218838", text_color="white", font=ctk.CTkFont(weight="bold"))
        
        # Botones de Confirmación (Ocultos por defecto)
        self.btn_confirm_yes = ctk.CTkButton(self.frame_buttons, text="⚠️ SÍ, DESTRUIR", command=self.execute_stop, 
                                             fg_color="#a51f1f", hover_color="#701414", font=ctk.CTkFont(weight="bold"))
        self.btn_confirm_no = ctk.CTkButton(self.frame_buttons, text="Cancelar", command=self.hide_inline_confirmation, font=ctk.CTkFont(weight="bold"))
        
#    def log(self, message):
#        """Añade un mensaje con timestamp a la consola"""
#        timestamp = time.strftime("%H:%M:%S")
#        self.textbox_log.insert("end", f"[{timestamp}] {message}\n")
#        self.textbox_log.see("end")
#        self.update()  # Forzar actualización de la UI
    def log(self, message):
        """Añade un mensaje a la consola con estilo prompt minimalista"""
        # Si el mensaje está vacío o es una línea separadora (====), lo imprimimos tal cual
        if message.strip() == "" or message.startswith("="):
            self.textbox_log.insert("end", f"{message}\n")
        else:
            self.textbox_log.insert("end", f" >> {message}\n")
            self.textbox_log.see("end")
            self.update()
    # --- LÓGICA DE INTERFAZ DINÁMICA ---
    def show_inline_confirmation(self):
        self.btn_launch.grid_remove()
        self.btn_stop.grid_remove()
        self.btn_check.grid_remove()
        
        self.btn_confirm_yes.grid(row=0, column=0, padx=10)
        self.btn_confirm_no.grid(row=0, column=1, padx=10)
        self.log("¿Estás seguro de que quieres detener el reto? El progreso no guardado se perderá.")

    def hide_inline_confirmation(self):
        self.btn_confirm_yes.grid_remove()
        self.btn_confirm_no.grid_remove()
        
        self.btn_launch.grid()
        self.btn_stop.grid()
        if self.container_running:
            self.btn_check.grid(row=0, column=2, padx=10)
        self.log("Cancelado. El reto sigue activo.")

    def execute_stop(self):
        self.hide_inline_confirmation()
        self.start_stop_thread()

    # --- LÓGICA DE DOCKER Y SUBPROCESOS ---
    def start_launch_thread(self):
        thread = threading.Thread(target=self.launch_challenge, daemon=True)
        thread.start()

    def start_stop_thread(self):
        thread = threading.Thread(target=self.stop_challenge, daemon=True)
        thread.start()

    def start_check_thread(self):
        if not self.ruta_check_actual:
            self.log("ERROR: No hay script de validación asignado a este reto.")
            return
        thread = threading.Thread(target=self.check_challenge, daemon=True)
        thread.start()

    def launch_challenge(self):
        dificultad = self.dificultad_var.get()
        self.log("")
        self.log("=" * 50)
        self.log("INICIANDO PROCESO DE DESPLIEGUE...")
        # self.log("")
        
        try:
            with open("challenge_data.json", "r", encoding='utf-8') as f:
                datos = json.load(f)
                usuario_objetivo = datos.get("username", "admin")
        except FileNotFoundError:
            self.log("ADVERTENCIA: No se encontró challenge_data.json. Usando 'admin' por defecto.")
            usuario_objetivo = "admin"
        except json.JSONDecodeError:
            self.log("ADVERTENCIA: Error al leer challenge_data.json. Usando 'admin' por defecto.")
            usuario_objetivo = "admin"
        except Exception as e:
            self.log(f"ADVERTENCIA: Error inesperado al leer JSON: {e}. Usando 'admin' por defecto.")
            usuario_objetivo = "admin"

        self.btn_launch.configure(state="disabled", text="🔨 CONSTRUYENDO...")
        
        try:
            conexion = sqlite3.connect('sqlite-scripts.db')
            cursor = conexion.cursor()
            cursor.execute("SELECT ruta_script, ruta_check, puntos_base FROM scripts WHERE nivel_dificultad = ? ORDER BY RANDOM() LIMIT 1", (dificultad,))
            res = cursor.fetchone()
            conexion.close()
            
            if not res:
                self.log("ERROR: No hay retos en la DB para esta dificultad.")
                self.reset_ui()
                return
            
            ruta_script, self.ruta_check_actual, self.puntuacion_base_actual = res
            self.log("Construyendo y configurando el entorno...")
            self.log("Esto puede tardar unos segundos...")
            resultado_build = subprocess.run(["docker", "build", "-q", "-t", "secure-the-box", "."], 
                                           capture_output=True, text=True)
            if resultado_build.returncode != 0:
                self.log(f"Error en build: {resultado_build.stderr}")
                raise Exception("Error en docker build")
            
            subprocess.run(["docker", "rm", "-f", self.nombre_contenedor], capture_output=True)
            
            subprocess.run(["docker", "run", "-d", "-it", "--name", self.nombre_contenedor, 
                                          "--hostname", "securethebox", "secure-the-box", "/bin/bash"], 
                                         capture_output=True, text=True, check=True)
            
            subprocess.run(["docker", "cp", ruta_script, f"{self.nombre_contenedor}:/tmp/setup.sh"], check=True, capture_output=True)
            
            resultado_setup = subprocess.run(
                ["docker", "exec", self.nombre_contenedor, "/bin/bash", "-c", 
                 f"bash /tmp/setup.sh {usuario_objetivo} && rm -f /tmp/setup.sh"],
                capture_output=True, text=True
            )
            
            if resultado_setup.returncode != 0:
                self.log(f"Setup completado con warnings: {resultado_setup.stderr[:100]}...")

            time.sleep(2)

            result_user = subprocess.run(
                ["docker", "exec", self.nombre_contenedor, "cat", "/tmp/terminal_user.txt"], 
                capture_output=True, text=True
            )
            self.usuario_terminal_actual = result_user.stdout.strip() if result_user.returncode == 0 else usuario_objetivo
            
            result_ssh = subprocess.run(
                ["docker", "exec", self.nombre_contenedor, "pgrep", "sshd"],
                capture_output=True
            )
            if result_ssh.returncode != 0:
                self.log("ADVERTENCIA: El servicio SSH podría no estar ejecutándose.")
            
            # FINALIZACIÓN
            
            self.container_running = True
            self.log("")
            self.log("=" * 50)
            self.log("¡ESCENARIO DESPLEGADO CON ÉXITO!")
            self.log(f"Terminal abierta como usuario: {self.usuario_terminal_actual}")
            self.log(f"Contraseña del usuario: stb2024")
            self.log("Usa el botón 'COMPROBAR SEGURIDAD' para probar la seguridad")
            self.start_time = time.time() # Guardamos la hora de inicio
            self.log("Cronómetro iniciado. ¡Buena suerte!")
            self.log("")
            self.btn_launch.configure(text="✅ RETO ACTIVO")
            self.btn_stop.configure(state="normal")
            self.btn_check.grid(row=0, column=2, padx=10)
            
            subprocess.Popen(["gnome-terminal", "--", "docker", "exec", "-it", "-u", self.usuario_terminal_actual, 
                            self.nombre_contenedor, "/bin/bash"])
	
        except Exception as e:
            self.log("=" * 50)
            self.log(f"ERROR CRÍTICO: {str(e)}")
            self.log("Revirtiendo cambios...")
            self.reset_ui()

    def check_challenge(self):
        if not self.container_running or not self.ruta_check_actual:
            return

        self.log("=" * 50)
        self.log("INICIANDO AUDITORÍA DE SEGURIDAD...")
    
        try:
            # 1. Copiamos el script de check al contenedor (silencioso)
            subprocess.run(["docker", "cp", self.ruta_check_actual, f"{self.nombre_contenedor}:/tmp/check.py"], 
                           check=True, capture_output=True)

            # 2. Ejecutamos el check
            # El script de la máquina solo debe imprimir si es vulnerable o no y salir con 0 o 1
            resultado = subprocess.run(
                ["docker", "exec", self.nombre_contenedor, "python3", "/tmp/check.py"],
                capture_output=True, text=True
            )

            # 3. Calculamos tiempo transcurrido
            elapsed_seconds = int(time.time() - self.start_time)
            minutos = elapsed_seconds // 60
            segundos = elapsed_seconds % 60
            tiempo_texto = f"{minutos}m {segundos}s"

            # 4. Si el código de salida es 0, el reto está superado
            if resultado.returncode == 0:
                # Lógica de puntuación basada en tus tramos
                if elapsed_seconds <= 240:          # 1-4 min
                    puntos_ganados = self.puntuacion_base_actual
                elif elapsed_seconds <= 600:        # 5-10 min
                    puntos_ganados = int(self.puntuacion_base_actual * 0.75)
                else:                               # 10+ min
                    puntos_ganados = int(self.puntuacion_base_actual * 0.50)

                self.log("✅ RESULTADO: SISTEMA SEGURO")
                self.log(f" > Tiempo empleado: {tiempo_texto}")
                self.log(f" > Puntuación: {puntos_ganados} / {self.puntuacion_base_actual} pts")
                self.log("=" * 50)
            
               # Aquí podrías añadir una llamada a la DB para guardar el récord del usuario
            else:
                self.log("❌ RESULTADO: SISTEMA VULNERABLE")
                self.log("Revisa la configuración y vuelve a intentarlo.")
            # Opcional: mostrar el error que devuelve el script de la máquina
            # self.log(f"Detalle: {resultado.stdout}")

        except Exception as e:
            self.log(f"ERROR CRÍTICO DURANTE EL CHECK: {e}")

    def stop_challenge(self):
        self.log("=" * 50)
        self.log("DETENIENDO RETO Y LIMPIANDO ENTORNO...")
        self.btn_stop.configure(state="disabled", text="⏹ DETENIENDO...")
        
        try:
            subprocess.run(["docker", "rm", "-f", self.nombre_contenedor], capture_output=True)
            self.container_running = False
            
            self.log("=" * 50)
            self.log("Entorno limpio. Puedes seleccionar otro reto.")
            self.log("=" * 50)
            
        except Exception as e:
            self.log(f"Error al detener: {e}")
        
        self.reset_ui()

    def reset_ui(self):
        self.btn_launch.configure(state="normal", text="🚀 DESPLEGAR ESCENARIO")
        self.btn_stop.configure(state="disabled", text="⏹ DETENER RETO")
        self.btn_check.grid_remove()
        self.container_running = False
        self.ruta_check_actual = None
        self.usuario_terminal_actual = "root"
        self.puntuacion_base_actual = 0
        self.start_time = 0
        
    def on_closing(self):
        if self.container_running:
            CustomConfirmDialog(self, "Salir de la app", "Hay un reto en ejecución. ¿Destruir el contenedor y salir?", self.destroy_and_quit)
        else:
            self.destroy()

    def destroy_and_quit(self):
        self.log("Cerrando aplicación...")
        subprocess.run(["docker", "rm", "-f", self.nombre_contenedor], capture_output=True)
        self.destroy()

if __name__ == "__main__":
    app = SecureTheBoxApp()
    app.mainloop()
