import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui
from pynput import keyboard
from pynput.keyboard import Controller as KeyboardController
import os

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
root.geometry("400x420")
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

        ttk.Button(
            key_container,
            textvariable=self.target_key_display,
            command=self.start_key_binding,
            width=15
        ).pack(side=tk.LEFT, padx=10)

        # --- Maintien ---
        ttk.Checkbutton(
            main_frame,
            text="Maintien continu (touche ou clic)",
            variable=self.hold_var,
            command=self.toggle_hold_state
        ).pack(pady=5)

        # --- Statut ---
        self.status_label = ttk.Label(
            main_frame,
            text="Statut : ARRÊTÉ",
            foreground="red",
            font=("Segoe UI", 12, "bold")
        )
        self.status_label.pack(pady=10)

        ttk.Label(
            main_frame,
            text="F6 pour démarrer/arrêter le programme",
            font=("Segoe UI", 9)
        ).pack()

        # --- Bouton contact en bas à droite ---
        bottom_bar = ttk.Frame(root)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        spacer = ttk.Frame(bottom_bar)
        spacer.pack(side=tk.LEFT, expand=True)

        ttk.Button(
            bottom_bar,
            text="?",
            width=3,
            command=self.show_contact
        ).pack(side=tk.RIGHT)

        # --- Hotkey ---
        self.listener = keyboard.Listener(on_press=self.on_global_hotkey)
        self.listener.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- Contact ---
    def show_contact(self):
        win = tk.Toplevel(self.root)
        win.title("Contact")
        win.resizable(False, False)
        win.geometry("260x80")
        ttk.Label(win, text="Contact :", font=("Segoe UI", 10, "bold")).pack(pady=5)
        ttk.Label(win, text="nathacool82@gmail.com").pack()

    # --- Maintien ---
    def toggle_hold_state(self):
        state = tk.DISABLED if self.hold_var.get() else tk.NORMAL
        self.delay_entry.config(state=state)
        self.unit_combo.config(state="disabled" if state == tk.DISABLED else "readonly")

    # --- Hotkey ---
    def on_global_hotkey(self, key):
        if key == keyboard.Key.f6:
            self.root.after(0, self.toggle_clicking)

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
            pyautogui.mouseUp()
            self.keyboard_controller.release(self.target_key_code)
        except Exception:
            pass

    def run_loop(self):
        delay = float(self.delay_var.get()) / 1000
        while self.is_running:
            if self.hold_var.get():
                pyautogui.mouseDown()
                while self.is_running:
                    time.sleep(0.05)
                pyautogui.mouseUp()
            else:
                pyautogui.click()
                time.sleep(delay)

    def on_close(self):
        self.is_running = False
        self.listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    AutoClickerApp(root)
    root.mainloop()

