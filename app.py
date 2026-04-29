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

# Mapa de colores para las etiquetas de dificultad
DIFICULTAD_COLORS = {
    '1': '#28a745',  # Por si usas números: 1=fácil
    '2': '#fd7e14',  # 2=media
    '3': '#dc3545',  # 3=difícil
    'fácil': '#28a745',
    'media': '#fd7e14',
    'difícil': '#dc3545'
}

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
        self.puntuacion_base_actual = 0  
        self.start_time = 0             
        self.title("Secure The Box - Defensive CTF Trainer")
        self.geometry("850x800") 
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variables de estado
        self.reto_seleccionado_id = ctk.IntVar(value=-1)
        self.datos_retos = {} 
        self.tarjetas_retos = {} 
        
        self.container_running = False
        self.nombre_contenedor = "maquina_reto"
        self.ruta_check_actual = None
        self.usuario_terminal_actual = "root"

        self.setup_ui()

    def setup_ui(self):
        # --- Cabecera ---
        self.label_title = ctk.CTkLabel(self, text="🛡️ SECURE THE BOX", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=15)

        # --- Panel de Selección de Retos ---
        self.frame_lista_container = ctk.CTkFrame(self)
        self.frame_lista_container.pack(pady=5, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(self.frame_lista_container, text="MÁQUINAS DISPONIBLES:", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        # Panel con scroll para la lista de tarjetas de retos
        self.frame_lista = ctk.CTkScrollableFrame(self.frame_lista_container)
        self.frame_lista.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Forzar que ambas columnas midan exactamente lo mismo (50/50)
        self.frame_lista.grid_columnconfigure(0, weight=1, uniform="grupo1")
        self.frame_lista.grid_columnconfigure(1, weight=1, uniform="grupo1")

        self.cargar_lista_retos()

        # --- Consola ---
        # Aquí puedes cambiar el tamaño base modificando "height=150"
        self.textbox_log = ctk.CTkTextbox(self, height=150, font=("Consolas", 12))
        self.textbox_log.pack(pady=10, padx=20, fill="x")
        self.log("Sistema iniciado. Selecciona una máquina y despliega el escenario...")

        # --- Botonera Principal ---
        self.frame_buttons = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_buttons.pack(pady=15)

        self.btn_launch = ctk.CTkButton(self.frame_buttons, text="🚀 DESPLEGAR ESCENARIO", width=220, 
                                        command=self.start_launch_thread, font=ctk.CTkFont(weight="bold", size=14))
        self.btn_launch.grid(row=0, column=0, padx=10)

        self.btn_stop = ctk.CTkButton(self.frame_buttons, text="⏹ DETENER RETO", width=220, 
                                      command=self.show_inline_confirmation, fg_color="#a51f1f", 
                                      hover_color="#701414", font=ctk.CTkFont(weight="bold", size=14), state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=10)

        self.btn_check = ctk.CTkButton(self.frame_buttons, text="✅ COMPROBAR SEGURIDAD", width=220, 
                                      command=self.start_check_thread, fg_color="#28a745", 
                                      hover_color="#218838", text_color="white", font=ctk.CTkFont(weight="bold", size=14))
        
        self.btn_confirm_yes = ctk.CTkButton(self.frame_buttons, text="⚠️ SÍ, DESTRUIR", command=self.execute_stop, 
                                             fg_color="#a51f1f", hover_color="#701414", font=ctk.CTkFont(weight="bold", size=14))
        self.btn_confirm_no = ctk.CTkButton(self.frame_buttons, text="Cancelar", command=self.hide_inline_confirmation, font=ctk.CTkFont(weight="bold", size=14))

    def cargar_lista_retos(self):
        """Carga los retos como tarjetas visuales interactivas en cuadrícula 2x2"""
        try:
            conexion = sqlite3.connect('sqlite-scripts.db')
            cursor = conexion.cursor()
            cursor.execute("SELECT rowid, nombre_script, nivel_dificultad, descripcion, ruta_script, ruta_check, puntos_base FROM scripts")
            retos = cursor.fetchall()
            conexion.close()

            if not retos:
                ctk.CTkLabel(self.frame_lista, text="No se encontraron máquinas en la base de datos.").pack(pady=20)
                return

            for index, reto in enumerate(retos):
                r_id, nombre_s, dif, desc, r_script, r_check, puntos = reto
                self.datos_retos[r_id] = reto
                
                dif = str(dif)
                color_dif = DIFICULTAD_COLORS.get(dif.lower(), '#cccccc') 

                # --- CREACIÓN DE LA TARJETA ---
                card = ctk.CTkFrame(self.frame_lista, fg_color="#222222", corner_radius=10, border_width=2, border_color="#222222")
                
                fila = index // 2
                columna = index % 2
                
                card.grid(row=fila, column=columna, pady=10, padx=10, sticky="nsew")
                
                self.tarjetas_retos[r_id] = card 

                # --- ESTRUCTURA INTERNA DE LA TARJETA ---
                
                # 1. Cabecera (Dificultad y Plataforma)
                header_frame = ctk.CTkFrame(card, fg_color="transparent")
                header_frame.pack(fill="x", padx=15, pady=(15, 5))

                diff_label_frame = ctk.CTkFrame(header_frame, fg_color=color_dif, corner_radius=5)
                diff_label_frame.pack(side="left")
                ctk.CTkLabel(diff_label_frame, text=dif.upper(), text_color="white", 
                             font=ctk.CTkFont(size=11, weight="bold")).pack(padx=8, pady=3)

                ctk.CTkLabel(header_frame, text="💻 Linux", text_color="#aaaaaa", 
                             font=ctk.CTkFont(size=11)).pack(side="right")

                # 2. Título 
                title_label = ctk.CTkLabel(card, text=nombre_s, anchor="w", 
                                          font=ctk.CTkFont(size=18, weight="bold"))
                title_label.pack(fill="x", padx=15, pady=(10, 5))

                # 3. Descripción
                desc_label = ctk.CTkLabel(card, text=desc, anchor="nw", justify="left", 
                                         text_color="#cccccc", wraplength=350, 
                                         font=ctk.CTkFont(size=13))
                desc_label.pack(fill="both", expand=True, padx=15, pady=(0, 15))

                # 4. Línea Separadora
                ctk.CTkFrame(card, height=1, fg_color="#333333").pack(fill="x", padx=15, pady=(0, 10))

                # 5. Pie de página 
                footer_frame = ctk.CTkFrame(card, fg_color="transparent")
                footer_frame.pack(fill="x", padx=15, pady=(0, 15))

                ctk.CTkLabel(footer_frame, text=f"{puntos} PTS", text_color=color_dif, 
                             font=ctk.CTkFont(size=16, weight="bold")).pack(side="right")

                # --- INTERACTIVIDAD DE LA TARJETA ---
                self.bind_recursion(card, r_id)

        except sqlite3.OperationalError as e:
            self.log(f"Error de base de datos. Detalle: {e}")

    def bind_recursion(self, widget, r_id):
        widget.bind("<Button-1>", lambda event, rid=r_id: self.seleccionar_reto(rid))
        for child in widget.winfo_children():
            self.bind_recursion(child, r_id)

    def seleccionar_reto(self, r_id):
        self.reto_seleccionado_id.set(r_id)
        
        for card in self.tarjetas_retos.values():
            card.configure(fg_color="#222222", border_color="#222222")
            
        selected_card = self.tarjetas_retos[r_id]
        reto_info = self.datos_retos[r_id]
        dif = str(reto_info[2]) 
        color_dif = DIFICULTAD_COLORS.get(dif.lower(), '#337ab7') 
        
        selected_card.configure(fg_color="#282828", border_color=color_dif)
        
        reto_nombre = reto_info[1] 
        self.log(f"Máquina seleccionada: {reto_nombre}")

    def log(self, message):
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
        self.log("¿Seguro que quieres detener el reto?")

    def hide_inline_confirmation(self):
        self.btn_confirm_yes.grid_remove()
        self.btn_confirm_no.grid_remove()
        self.btn_launch.grid()
        self.btn_stop.grid()
        if self.container_running:
            self.btn_check.grid(row=0, column=2, padx=10)

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
        r_id = self.reto_seleccionado_id.get()
        if r_id == -1:
            self.log("ERROR: Selecciona una máquina de la lista antes de desplegar.")
            return
            
        reto = self.datos_retos.get(r_id)
        if not reto:
            self.log("ERROR: La máquina seleccionada no se encontró en memoria.")
            return
            
        _, nombre_s, dificultad, _, ruta_script, self.ruta_check_actual, self.puntuacion_base_actual = reto

        self.log("")
        self.log("=" * 50)
        self.log(f"INICIANDO DESPLIEGUE: {nombre_s.upper()}")
        
        try:
            with open("challenge_data.json", "r", encoding='utf-8') as f:
                datos = json.load(f)
                usuario_objetivo = datos.get("username", "admin")
        except:
            usuario_objetivo = "admin"

        self.btn_launch.configure(state="disabled", text="CONSTRUYENDO...")
        
        try:
            self.log("Construyendo y configurando el entorno...")
            resultado_build = subprocess.run(["docker", "build", "-q", "-t", "secure-the-box", "."], capture_output=True, text=True)
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
            
            # --- EXPANDIR LA TERMINAL CUANDO SE OCULTA LA LISTA ---
            self.frame_lista_container.pack_forget()
            self.textbox_log.pack_configure(expand=True, fill="both")
            
            self.container_running = True
            self.log("")
            self.log("=" * 50)
            self.log("¡ESCENARIO DESPLEGADO CON ÉXITO!")
            self.log(f"Terminal abierta como usuario: {self.usuario_terminal_actual}")
            self.log("Contraseña del usuario: stb2024")
            self.start_time = time.time() 
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
            subprocess.run(["docker", "cp", self.ruta_check_actual, f"{self.nombre_contenedor}:/tmp/check.py"], 
                           check=True, capture_output=True)

            resultado = subprocess.run(
                ["docker", "exec", self.nombre_contenedor, "python3", "/tmp/check.py"],
                capture_output=True, text=True
            )

            elapsed_seconds = int(time.time() - self.start_time)
            minutos = elapsed_seconds // 60
            segundos = elapsed_seconds % 60
            tiempo_texto = f"{minutos}m {segundos}s"

            if resultado.returncode == 0:
                if elapsed_seconds <= 240:          
                    puntos_ganados = self.puntuacion_base_actual
                elif elapsed_seconds <= 600:        
                    puntos_ganados = int(self.puntuacion_base_actual * 0.75)
                else:                               
                    puntos_ganados = int(self.puntuacion_base_actual * 0.50)

                self.log("✅ RESULTADO: SISTEMA SEGURO")
                self.log(f" > Tiempo empleado: {tiempo_texto}")
                self.log(f" > Puntuación: {puntos_ganados} / {self.puntuacion_base_actual} pts")
                self.log("=" * 50)
                
                self.log("✨ ¡Enhorabuena! Cerrando la máquina en 3 segundos...")
                time.sleep(3)
                self.stop_challenge()
            else:
                self.log("❌ RESULTADO: SISTEMA VULNERABLE")
                self.log("Revisa la configuración y vuelve a intentarlo.")

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
        
        self.frame_lista_container.pack(pady=5, padx=20, fill="both", expand=True, before=self.textbox_log)
        
        # --- RESTAURAR LA TERMINAL A SU TAMAÑO NORMAL AL VOLVER AL MENÚ ---
        self.textbox_log.pack_configure(expand=False, fill="x")
        
        self.ruta_check_actual = None
        self.usuario_terminal_actual = "root"
        self.puntuacion_base_actual = 0
        self.start_time = 0
        
        self.reto_seleccionado_id.set(-1)
        for card in self.tarjetas_retos.values():
            card.configure(fg_color="#222222", border_color="#222222")
        
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
