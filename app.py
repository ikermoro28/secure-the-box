import customtkinter as ctk
import os
import subprocess
import threading
import sqlite3
import json
import time

# Apariencia global
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Colores etiquetas de dificultad
DIFICULTAD_COLORS = {
    '1': '#28a745',  # Fácil
    '2': '#fd7e14',  # Media
    '3': '#dc3545',  # Difícil
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
        self.label_title = ctk.CTkLabel(self, text="🛡️ SECURE THE BOX", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=15)

        self.frame_lista_container = ctk.CTkFrame(self)
        self.frame_lista_container.pack(pady=5, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(self.frame_lista_container, text="MÁQUINAS DISPONIBLES:", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.frame_lista = ctk.CTkScrollableFrame(self.frame_lista_container)
        self.frame_lista.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.frame_lista.grid_columnconfigure(0, weight=1, uniform="grupo1")
        self.frame_lista.grid_columnconfigure(1, weight=1, uniform="grupo1")

        self.cargar_lista_retos()

        self.textbox_log = ctk.CTkTextbox(self, height=150, font=("Consolas", 12))
        self.textbox_log.pack(pady=10, padx=20, fill="x")
        self.log("Sistema iniciado. Selecciona una máquina y despliega el escenario...")

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
        try:
            conexion = sqlite3.connect('sqlite-scripts.db')
            cursor = conexion.cursor()
            cursor.execute("SELECT rowid, nombre_script, nivel_dificultad, descripcion, ruta_script, ruta_check, puntos_base FROM scripts")
            retos = cursor.fetchall()
            conexion.close()

            for index, reto in enumerate(retos):
                r_id, nombre_s, dif, desc, r_script, r_check, puntos = reto
                self.datos_retos[r_id] = reto
                
                dif = str(dif)
                color_dif = DIFICULTAD_COLORS.get(dif.lower(), '#cccccc') 

                card = ctk.CTkFrame(self.frame_lista, fg_color="#222222", corner_radius=10, border_width=2, border_color="#222222")
                fila = index // 2
                columna = index % 2
                card.grid(row=fila, column=columna, pady=10, padx=10, sticky="nsew")
                self.tarjetas_retos[r_id] = card 

                header_frame = ctk.CTkFrame(card, fg_color="transparent")
                header_frame.pack(fill="x", padx=15, pady=(15, 5))

                diff_label_frame = ctk.CTkFrame(header_frame, fg_color=color_dif, corner_radius=5)
                diff_label_frame.pack(side="left")
                ctk.CTkLabel(diff_label_frame, text=dif.upper(), text_color="white", 
                             font=ctk.CTkFont(size=11, weight="bold")).pack(padx=8, pady=3)

                title_label = ctk.CTkLabel(card, text=nombre_s, anchor="w", font=ctk.CTkFont(size=18, weight="bold"))
                title_label.pack(fill="x", padx=15, pady=(10, 5))

                desc_label = ctk.CTkLabel(card, text=desc, anchor="nw", justify="left", text_color="#cccccc", wraplength=350, font=ctk.CTkFont(size=13))
                desc_label.pack(fill="both", expand=True, padx=15, pady=(0, 15))

                ctk.CTkFrame(card, height=1, fg_color="#333333").pack(fill="x", padx=15, pady=(0, 10))
                footer_frame = ctk.CTkFrame(card, fg_color="transparent")
                footer_frame.pack(fill="x", padx=15, pady=(0, 15))
                ctk.CTkLabel(footer_frame, text=f"{puntos} PTS", text_color=color_dif, font=ctk.CTkFont(size=16, weight="bold")).pack(side="right")

                self.bind_recursion(card, r_id)
        except Exception as e:
            self.log(f"Error al cargar retos: {e}")

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
        self.log(f"Máquina seleccionada: {reto_info[1]}")

    def log(self, message):
        if message.strip() == "" or message.startswith("="):
            self.textbox_log.insert("end", f"{message}\n")
        else:
            self.textbox_log.insert("end", f" >> {message}\n")
            self.textbox_log.see("end")
            self.update()

    def show_inline_confirmation(self):
        self.btn_launch.grid_remove()
        self.btn_stop.grid_remove()
        self.btn_check.grid_remove()
        self.btn_confirm_yes.grid(row=0, column=0, padx=10)
        self.btn_confirm_no.grid(row=0, column=1, padx=10)

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

    def start_launch_thread(self):
        threading.Thread(target=self.launch_challenge, daemon=True).start()

    def start_stop_thread(self):
        threading.Thread(target=self.stop_challenge, daemon=True).start()

    def start_check_thread(self):
        threading.Thread(target=self.check_challenge, daemon=True).start()

    def launch_challenge(self):
        r_id = self.reto_seleccionado_id.get()
        if r_id == -1:
            self.log("ERROR: Selecciona una máquina.")
            return
            
        reto = self.datos_retos.get(r_id)
        _, nombre_s, _, _, ruta_script, self.ruta_check_actual, self.puntuacion_base_actual = reto
        
        try:
            with open("challenge_data.json", "r", encoding='utf-8') as f:
                datos = json.load(f)
                usuario_objetivo = datos.get("username", "admin")
        except:
            usuario_objetivo = "admin"

        self.btn_launch.configure(state="disabled", text="CONSTRUYENDO...")
        
        try:
            self.log(f"Iniciando: {nombre_s}")
            
            # capture_output=True añadido para silenciar la terminal física
            subprocess.run(["docker", "build", "-q", "-t", "secure-the-box", "."], check=True, capture_output=True)
            subprocess.run(["docker", "rm", "-f", self.nombre_contenedor], capture_output=True)
            
            comando_docker = ["docker", "run", "-d", "-it", "--name", self.nombre_contenedor, "--hostname", "securethebox", "--dns", "8.8.8.8"]
            if nombre_s == "Web Securing":
                subprocess.run(["fuser", "-k", "6067/tcp"], capture_output=True)
                comando_docker.extend(["-p", "6067:80"])
                
            comando_docker.extend(["secure-the-box", "/bin/bash"])
            # Silenciamos la salida del ID del contenedor, así no damos pistas al usuario
            subprocess.run(comando_docker, check=True, capture_output=True)
            
            # Silenciamos el mensaje de Successfully copied, nuevamente para no dar pistas
            subprocess.run(["docker", "cp", ruta_script, f"{self.nombre_contenedor}:/tmp/setup.sh"], check=True, capture_output=True)
            
            subprocess.run(["docker", "exec", self.nombre_contenedor, "/bin/bash", "-c", 
                            f"echo 'Acquire::ForceIPv4 \"true\";' > /etc/apt/apt.conf.d/99force-ipv4 && export DEBIAN_FRONTEND=noninteractive; bash /tmp/setup.sh {usuario_objetivo}"], 
                            capture_output=True)

            # Obtener usuario final
            res = subprocess.run(["docker", "exec", self.nombre_contenedor, "cat", "/tmp/terminal_user.txt"], capture_output=True, text=True)
            if res.returncode == 0:
                self.usuario_terminal_actual = res.stdout.strip()
            else:
                check_user = subprocess.run(["docker", "exec", self.nombre_contenedor, "id", "-u", usuario_objetivo], capture_output=True)
                self.usuario_terminal_actual = usuario_objetivo if check_user.returncode == 0 else "root"
            
            if self.usuario_terminal_actual == "root":
                home_dir = "/root"
            else:
                home_dir = f"/home/{self.usuario_terminal_actual}"

            self.frame_lista_container.pack_forget()
            self.textbox_log.pack_configure(expand=True, fill="both")
            self.container_running = True
            
            self.log(f"¡Listo! Terminal abierta en {home_dir} como {self.usuario_terminal_actual}")
            self.start_time = time.time() 
            self.btn_launch.configure(text="✅ RETO ACTIVO")
            self.btn_stop.configure(state="normal")
            self.btn_check.grid(row=0, column=2, padx=10)
            
            subprocess.Popen(["gnome-terminal", "--", "docker", "exec", "-it", 
                            "-u", self.usuario_terminal_actual, 
                            "-w", home_dir, 
                            self.nombre_contenedor, "/bin/bash"])
    
        except Exception as e:
            self.log(f"ERROR: {e}")
            self.reset_ui()

    def check_challenge(self):
        if not self.container_running: return
        self.log("Auditando sistema...")
        try:
            # Silenciamos la copia del script de check
            subprocess.run(["docker", "cp", self.ruta_check_actual.strip(), f"{self.nombre_contenedor}:/tmp/check.py"], check=True, capture_output=True)
            
            res = subprocess.run(["docker", "exec", self.nombre_contenedor, "python3", "/tmp/check.py"], capture_output=True, text=True)
            if res.returncode == 0:
                self.log("✅ SISTEMA SEGURO")
                time.sleep(2)
                self.stop_challenge()
            else:
                self.log("❌ SISTEMA VULNERABLE")
        except Exception as e:
            self.log(f"Error en auditoría: {e}")

    def stop_challenge(self):
        subprocess.run(["docker", "rm", "-f", self.nombre_contenedor], capture_output=True)
        self.reset_ui()

    def reset_ui(self):
        self.btn_launch.configure(state="normal", text="🚀 DESPLEGAR ESCENARIO")
        self.btn_stop.configure(state="disabled")
        self.btn_check.grid_remove()
        self.container_running = False
        self.frame_lista_container.pack(pady=5, padx=20, fill="both", expand=True, before=self.textbox_log)
        self.textbox_log.pack_configure(expand=False, fill="x")
        self.reto_seleccionado_id.set(-1)
        for card in self.tarjetas_retos.values():
            card.configure(fg_color="#222222", border_color="#222222")
        
    def on_closing(self):
        if self.container_running:
            CustomConfirmDialog(self, "Salir", "¿Destruir reto y salir?", self.destroy_and_quit)
        else:
            self.destroy()

    def destroy_and_quit(self):
        subprocess.run(["docker", "rm", "-f", self.nombre_contenedor], capture_output=True)
        self.destroy()

if __name__ == "__main__":
    app = SecureTheBoxApp()
    app.mainloop()
