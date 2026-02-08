import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui
from pynput import keyboard
from pynput.keyboard import Controller as KeyboardController
import os
import webbrowser

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

# --- Icône ---
def apply_icon(root):
    try:
        icon_path = "icon-autoclicker.ico"
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception:
        pass

# --- Fenêtre ---
root = tk.Tk()
root.title("AutoClicker")
root.geometry("400x380")
root.resizable(False, False)
apply_icon(root)

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.keyboard_controller = KeyboardController()
        self.is_running = False

        self.delay_var = tk.StringVar(value="100")
        self.unit_var = tk.StringVar(value="Millisecondes")
        self.mode_var = tk.StringVar(value="mouse")
        self.mouse_btn_var = tk.StringVar(value="left")
        self.hold_var = tk.BooleanVar(value=False)

        self.target_key_display = tk.StringVar(value="a")
        self.target_key_code = "a"

        self.hotkey_var = tk.StringVar(value="F6")
        self.hotkey_code = keyboard.Key.f6

        # --- Conteneur principal ---
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Intervalle ---
        self.delay_frame = ttk.LabelFrame(main_frame, text="Intervalle / Vitesse", padding=10)
        self.delay_frame.pack(fill=tk.X, pady=5)

        delay_container = ttk.Frame(self.delay_frame)
        delay_container.pack(fill=tk.X)

        self.delay_entry = ttk.Entry(delay_container, textvariable=self.delay_var, width=10)
        self.delay_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.unit_combo = ttk.Combobox(delay_container, textvariable=self.unit_var, width=12, state="readonly")
        self.unit_combo["values"] = ("Millisecondes", "Secondes", "Minutes")
        self.unit_combo.pack(side=tk.LEFT)

        # --- Mode ---
        mode_frame = ttk.LabelFrame(main_frame, text="Type d'action", padding=10)
        mode_frame.pack(fill=tk.X, pady=5)

        mouse_container = ttk.Frame(mode_frame)
        mouse_container.pack(fill=tk.X)
        ttk.Radiobutton(mouse_container, text="Souris", variable=self.mode_var, value="mouse").pack(side=tk.LEFT)
        self.mouse_combo = ttk.Combobox(mouse_container, textvariable=self.mouse_btn_var, width=10, state="readonly")
        self.mouse_combo["values"] = ("left", "right", "middle")
        self.mouse_combo.pack(side=tk.LEFT, padx=10)

        key_container = ttk.Frame(mode_frame)
        key_container.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(key_container, text="Clavier", variable=self.mode_var, value="keyboard").pack(side=tk.LEFT)
        ttk.Button(key_container, textvariable=self.target_key_display, command=self.start_key_binding, width=15).pack(side=tk.LEFT, padx=10)

        # --- Maintien ---
        ttk.Checkbutton(main_frame, text="Maintien continu (touche ou clic)", variable=self.hold_var, command=self.toggle_hold_state).pack(pady=5)

        # --- Statut ---
        self.status_label = ttk.Label(main_frame, text="Statut : ARRÊTÉ", foreground="red", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(pady=10)

        # --- Raccourci personnalisable en bas ---
        bottom_frame = ttk.Frame(root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        ttk.Label(bottom_frame, text="Raccourci Démarrer/Arrêter :").pack(side=tk.LEFT)
        ttk.Button(bottom_frame, textvariable=self.hotkey_var, command=self.start_hotkey_binding, width=8).pack(side=tk.LEFT, padx=5)

        # --- Contact Microsoft Forms ---
        spacer = ttk.Frame(bottom_frame)
        spacer.pack(side=tk.LEFT, expand=True)
        ttk.Button(bottom_frame, text="Contact", command=self.open_contact_form).pack(side=tk.RIGHT)

        # --- Hotkey listener ---
        self.listener = keyboard.Listener(on_press=self.on_global_hotkey)
        self.listener.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- Contact ---
    def open_contact_form(self):
        webbrowser.open("https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAN__mAHzLFUQ0o1U1FFRzEzSEk2SEJQRU1SOVJXNDhKUS4u")

    # --- Maintien ---
    def toggle_hold_state(self):
        state = tk.DISABLED if self.hold_var.get() else tk.NORMAL
        self.delay_entry.config(state=state)
        self.unit_combo.config(state="disabled" if state == tk.DISABLED else "readonly")

    # --- Hotkey ---
    def on_global_hotkey(self, key):
        try:
            if key == self.hotkey_code:
                self.root.after(0, self.toggle_clicking)
        except Exception:
            pass

    # --- Bind touche ---
    def start_key_binding(self):
        if self.is_running:
            return
        self.target_key_display.set("Appuyez...")
        self.root.bind("<Key>", self.on_key_setup_press)

    def on_key_setup_press(self, event):
        self.target_key_code = event.keysym.lower()
        self.target_key_display.set(f"Touche : {event.keysym}")
        self.root.unbind("<Key>")

    # --- Bind hotkey ---
    def start_hotkey_binding(self):
        self.hotkey_var.set("Appuyez...")
        self.root.bind("<Key>", self.on_hotkey_setup_press)

    def on_hotkey_setup_press(self, event):
        key_name = event.keysym
        self.hotkey_var.set(key_name)
        # Convertir en code pynput si possible
        try:
            self.hotkey_code = getattr(keyboard.Key, key_name.lower())
        except AttributeError:
            self.hotkey_code = key_name.lower()
        self.root.unbind("<Key>")

    # --- Start / Stop ---
    def toggle_clicking(self):
        if self.is_running:
            self.stop_clicker()
        else:
            self.start_clicker()

    def start_clicker(self):
        self.is_running = True
        self.status_label.config(text="Statut : EN COURS...", foreground="green")
        threading.Thread(target=self.run_loop, daemon=True).start()

    def stop_clicker(self):
        self.is_running = False
        self.release_inputs()
        self.status_label.config(text="Statut : ARRÊTÉ", foreground="red")

    def release_inputs(self):
        try:
            if self.mode_var.get() == "mouse":
                pyautogui.mouseUp(button=self.mouse_btn_var.get())
            else:
                self.keyboard_controller.release(self.target_key_code)
        except Exception:
            pass

    def run_loop(self):
        delay = float(self.delay_var.get()) / 1000
        while self.is_running:
            if self.hold_var.get():
                if self.mode_var.get() == "mouse":
                    pyautogui.mouseDown(button=self.mouse_btn_var.get())
                else:
                    self.keyboard_controller.press(self.target_key_code)
                while self.is_running:
                    time.sleep(0.05)
                if self.mode_var.get() == "mouse":
                    pyautogui.mouseUp(button=self.mouse_btn_var.get())
                else:
                    self.keyboard_controller.release(self.target_key_code)
            else:
                if self.mode_var.get() == "mouse":
                    pyautogui.click(button=self.mouse_btn_var.get())
                else:
                    self.keyboard_controller.press(self.target_key_code)
                    self.keyboard_controller.release(self.target_key_code)
                time.sleep(delay)

    def on_close(self):
        self.is_running = False
        self.listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    AutoClickerApp(root)
    root.mainloop()

