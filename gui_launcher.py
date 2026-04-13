import customtkinter as ctk
import os
import subprocess
import threading
import sqlite3

# Configuración de apariencia global
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CustomConfirmDialog(ctk.CTkToplevel):
    # Esta ventana la dejamos SOLO para cuando se cierra la app con la X, ya que te funciona bien ahí
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
        super().__init__()
        self.title("Secure The Box - Defensive CTF Trainer")
        self.geometry("700x550")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variables de estado
        self.dificultad_var = ctk.StringVar(value="1")
        self.container_running = False
        self.nombre_contenedor = "maquina_reto"

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
        self.textbox_log = ctk.CTkTextbox(self, height=200, width=600, font=("Consolas", 12))
        self.textbox_log.pack(pady=10, padx=20)
        self.log("Esperando selección de reto...")

        # --- Botonera Principal Dinámica ---
        self.frame_buttons = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_buttons.pack(pady=20)

        # Botones Normales (Visibles por defecto)
        self.btn_launch = ctk.CTkButton(self.frame_buttons, text="🚀 DESPLEGAR ESCENARIO", command=self.start_launch_thread, font=ctk.CTkFont(weight="bold"))
        self.btn_launch.grid(row=0, column=0, padx=10)

        self.btn_stop = ctk.CTkButton(self.frame_buttons, text="⏹ DETENER RETO", command=self.show_inline_confirmation, 
                                      fg_color="#a51f1f", hover_color="#701414", font=ctk.CTkFont(weight="bold"), state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=10)

        # Botones de Confirmación (Ocultos por defecto)
        self.btn_confirm_yes = ctk.CTkButton(self.frame_buttons, text="⚠️ SÍ, DESTRUIR", command=self.execute_stop, 
                                             fg_color="#a51f1f", hover_color="#701414", font=ctk.CTkFont(weight="bold"))
        self.btn_confirm_no = ctk.CTkButton(self.frame_buttons, text="Cancelar", command=self.hide_inline_confirmation, font=ctk.CTkFont(weight="bold"))

    def log(self, message):
        self.textbox_log.insert("end", f"> {message}\n")
        self.textbox_log.see("end")

    # --- LÓGICA DE INTERFAZ DINÁMICA (En lugar de la ventana pop-up) ---
    def show_inline_confirmation(self):
        # Escondemos los botones normales
        self.btn_launch.grid_remove()
        self.btn_stop.grid_remove()
        # Mostramos los de confirmación
        self.btn_confirm_yes.grid(row=0, column=0, padx=10)
        self.btn_confirm_no.grid(row=0, column=1, padx=10)
        self.log("¿Estás seguro de que quieres detener el reto? El progreso no guardado se perderá.")

    def hide_inline_confirmation(self):
        # Escondemos confirmación
        self.btn_confirm_yes.grid_remove()
        self.btn_confirm_no.grid_remove()
        # Volvemos a mostrar botones normales
        self.btn_launch.grid()
        self.btn_stop.grid()
        self.log("Cancelado. El reto sigue activo.")

    def execute_stop(self):
        # Ocultamos la confirmación e iniciamos el hilo para detener
        self.hide_inline_confirmation()
        self.start_stop_thread()

    # --- LÓGICA DE DOCKER Y SUBPROCESOS ---
    def start_launch_thread(self):
        thread = threading.Thread(target=self.launch_challenge, daemon=True)
        thread.start()

    def start_stop_thread(self):
        thread = threading.Thread(target=self.stop_challenge, daemon=True)
        thread.start()

    def launch_challenge(self):
        dificultad = self.dificultad_var.get()
        self.btn_launch.configure(state="disabled", text="CONSTRUYENDO...")
        self.btn_stop.configure(state="disabled")
        
        try:
            # 1. Consulta DB
            self.log(f"Buscando reto de dificultad {dificultad}...")
            conexion = sqlite3.connect('sqlite-scripts.db')
            cursor = conexion.cursor()
            cursor.execute("SELECT ruta_script FROM scripts WHERE nivel_dificultad = ? ORDER BY RANDOM() LIMIT 1", (dificultad,))
            resultado = cursor.fetchone()
            conexion.close()

            if not resultado:
                self.log("ERROR: No se encontró el script en la DB.")
                self.reset_ui()
                return

            ruta_script = resultado[0]
            
            # 2. Docker Build
            self.log("Verificando imagen Docker base...")
            subprocess.run(["docker", "build", "-q", "-t", "secure-the-box", "."], check=True)

            # 3. Docker Run
            self.log("Levantando contenedor...")
            subprocess.run(["docker", "rm", "-f", self.nombre_contenedor], capture_output=True) 
            subprocess.run(["docker", "run", "-d", "-it", "--name", self.nombre_contenedor, "secure-the-box", "/bin/bash"], check=True)
            self.container_running = True

            # 4. Inyectar Vulnerabilidad
            self.log("Configurando escenario...")
            subprocess.run(["docker", "cp", ruta_script, f"{self.nombre_contenedor}:/tmp/setup.sh"], check=True)
            comando_setup = "bash /tmp/setup.sh && rm -f /tmp/setup.sh"
            subprocess.run(["docker", "exec", self.nombre_contenedor, "/bin/bash", "-c", comando_setup], check=True)

            # 5. Interfaz en modo "En Ejecución"
            self.log("¡LISTO! Terminal abierta.")
            self.btn_launch.configure(text="RETO ACTIVO")
            self.btn_stop.configure(state="normal")
            
            # Abrir Terminal
            subprocess.run(["gnome-terminal", "--", "docker", "exec", "-it", self.nombre_contenedor, "/bin/bash"])

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.reset_ui()

    def stop_challenge(self):
        self.btn_stop.configure(state="disabled", text="DETENIENDO...")
        try:
            self.log("Deteniendo y eliminando contenedor...")
            subprocess.run(["docker", "rm", "-f", self.nombre_contenedor], capture_output=True)
            self.container_running = False
            self.log("Entorno limpio. Puedes seleccionar otro reto.")
        except Exception as e:
            self.log(f"Error al detener: {e}")
        
        self.reset_ui()

    def reset_ui(self):
        # Restaura los botones a su estado inicial
        self.btn_launch.configure(state="normal", text="DESPLEGAR ESCENARIO")
        self.btn_stop.configure(state="disabled", text="DETENER RETO")
        self.container_running = False

    def on_closing(self):
        if self.container_running:
            CustomConfirmDialog(self, "Salir de la app", "Hay un reto en ejecución. ¿Destruir el contenedor y salir?", self.destroy_and_quit)
        else:
            self.destroy()

    def destroy_and_quit(self):
        subprocess.run(["docker", "rm", "-f", self.nombre_contenedor], capture_output=True)
        self.destroy()

if __name__ == "__main__":
    app = SecureTheBoxApp()
    app.mainloop()
