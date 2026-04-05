import customtkinter as ctk
import subprocess
import threading
import os
import sys
import webbrowser

# Настройка темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """ Функция для поиска ресурсов внутри EXE (PyInstaller) """
    try:
        # PyInstaller создает временную папку _MEIxxxx
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class KiloFarshZapret(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KiloFarsh - Zapret GUI")
        self.geometry("600x520")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.process = None

        # --- Заголовок ---
        self.header = ctk.CTkLabel(self, text="ZAPRET CONTROL", font=("Fira Code", 26, "bold"), text_color="#F70707")
        self.header.pack(pady=(20, 10))

        # --- Поле ввода стратегии ---
        self.strategy_label = ctk.CTkLabel(self, text="Параметры запуска (Strategy):", font=("Arial", 12))
        self.strategy_label.pack()
        
        self.strategy_var = ctk.StringVar(value="--wf-tcp=443 --desync=fake")
        self.strategy_entry = ctk.CTkEntry(self, width=520, textvariable=self.strategy_var, font=("Consolas", 13))
        self.strategy_entry.pack(pady=5)

        # --- Кнопки ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=15)

        self.start_btn = ctk.CTkButton(self.btn_frame, text="СТАРТ", fg_color="#2eb82e", hover_color="#1e7b1e", command=self.start_service)
        self.start_btn.grid(row=0, column=0, padx=10)

        self.stop_btn = ctk.CTkButton(self.btn_frame, text="СТОП", fg_color="#ea4335", hover_color="#c62828", command=self.stop_service)
        self.stop_btn.grid(row=0, column=1, padx=10)

        # --- Логи ---
        self.log_box = ctk.CTkTextbox(self, width=550, height=220, font=("Consolas", 12), fg_color="#1a1a1a")
        self.log_box.pack(pady=10)
        self.log("Система готова. Запустите от имени Администратора!")

        # --- Ссылка на GitHub ---
        self.footer = ctk.CTkLabel(self, text="Developed by KiloFarsh", font=("Consolas", 13, "underline"), text_color="#33ccff", cursor="hand2")
        self.footer.pack(side="bottom", pady=15)
        self.footer.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/KiloFarsh"))

    def log(self, text):
        self.log_box.insert("end", f"> {text}\n")
        self.log_box.see("end")

    def start_service(self):
        if self.process: return
        threading.Thread(target=self.worker, daemon=True).start()
        self.start_btn.configure(state="disabled", text="ЗАПУЩЕНО")

    def worker(self):
        # Ищем winws.exe через ресурсный путь
        exe = resource_path(os.path.join("bin", "winws.exe"))
        
        if not os.path.exists(exe):
            self.log(f"ОШИБКА: {exe} не найден!")
            self.start_btn.configure(state="normal", text="СТАРТ")
            return

        cmd = f'"{exe}" {self.strategy_var.get()}'
        
        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                text=True, shell=True, creationflags=0x08000000 # CREATE_NO_WINDOW
            )
            for line in self.process.stdout:
                if line: self.log(line.strip())
        except Exception as e:
            self.log(f"Ошибка: {e}")
        finally:
            self.process = None
            self.start_btn.configure(state="normal", text="СТАРТ")

    def stop_service(self):
        subprocess.call("taskkill /F /IM winws.exe /T", shell=True)
        self.process = None
        self.log("Процессы winws остановлены.")
        self.start_btn.configure(state="normal", text="СТАРТ")

    def on_closing(self):
        self.stop_service()
        self.destroy()

if __name__ == "__main__":
    app = KiloFarshZapret()
    app.mainloop()