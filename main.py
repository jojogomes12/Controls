import pygame
import pyautogui
import threading
import tkinter as tk
from tkinter import ttk
import sqlite3
from PIL import ImageTk, Image
DB_FILE = "config.db"

class ConfigurationApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")
        self.root.title("Configuração de Controle, Tecla e Botão")
        self.root.iconbitmap("control.ico")  # Substitua pelo caminho real do ícone

        self.create_database()
        self.init_pygame()
        self.init_ui()

        self.event_thread = threading.Thread(target=self.process_events)
        self.event_thread.start()

    def create_database(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS config
                          (id INTEGER PRIMARY KEY, selected_button INTEGER, selected_key TEXT, selected_joystick INTEGER)''')
        conn.commit()
        conn.close()

    def read_configs(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM config")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def write_config(self, selected_button, selected_key, selected_joystick):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("INSERT OR REPLACE INTO config (selected_button, selected_key, selected_joystick) VALUES (?, ?, ?)",
                       (selected_button, selected_key, selected_joystick))

        conn.commit()
        conn.close()

    def init_pygame(self):
        pygame.init()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

    def process_events(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.KEYDOWN:
                    print(f"Tecla pressionada: {pygame.key.name(event.key)}")
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.handle_joystick_button_press(event)

    def handle_joystick_button_press(self, event):
        selected_joystick_index = self.combo_joysticks.current()
        selected_button_index = self.combo_buttons.current()

        if selected_joystick_index >= 0 and selected_button_index >= 0:
            selected_joystick = self.joysticks[selected_joystick_index]

            for config in self.read_configs():
                if event.button == config[1] and selected_joystick_index == config[3]:
                    selected_key = config[2]
                    if selected_key == "botão direito do mouse":
                        pyautogui.click(button='right')
                    else:
                        t = threading.Thread(target=self.emulate_selected_key, args=(selected_key,))
                        t.start()
                    print(f"Botão do controle {event.button} pressionado!")

    def emulate_selected_key(self, selected_key):
        pyautogui.press(selected_key)

    def init_ui(self):
        joystick_names = [joystick.get_name() for joystick in self.joysticks]
        
        # Carregar a imagem
        img = Image.open("images/xbox.png")  # Substitua pelo caminho real da imagem
        img = img.resize((200, 200))  # Redimensionar a imagem, se necessário
        self.photo = ImageTk.PhotoImage(img)

    # Criar um widget Label para exibir a imagem
        self.image_label = tk.Label(self.root, image=self.photo)
        self.image_label.grid(row=4, column=0, columnspan=10, padx=0, pady=50)  # Mova a imagem para a primeira coluna
        self.combo_joysticks = ttk.Combobox(self.root, values=joystick_names, width=30)
        self.combo_joysticks.set("Selecione um controle...")
        self.combo_joysticks.grid(row=0, column=0, padx=(10, 40), pady=10)
        

        keys_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                     "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                     "u", "v", "w", "x", "y", "z", "0", "1", "2", "3",
                     "4", "5", "6", "7", "8", "9", "esc", "enter", "space",
                     "botão direito do mouse"]

        self.combo_keys = ttk.Combobox(self.root, values=keys_list, width=30)
        self.combo_keys.set("Selecione uma tecla...")
        self.combo_keys.grid(row=0, column=1, padx=(10, 40), pady=20)
        

        buttons_list = [f"Botão {i}" for i in range(16)]
        self.combo_buttons = ttk.Combobox(self.root, values=buttons_list, width=30)
        self.combo_buttons.set("Selecione um botão...")
      
        self.combo_buttons.grid(row=0, column=2,padx=(10, 50), pady=50)

        save_button = tk.Button(self.root, text="Salvar", command=self.save_config)
        save_button.grid(row=1, columnspan=3, pady=10)
        

        self.config_listbox = tk.Listbox(self.root, width=50, height=10)
        self.config_listbox.grid(row=2, columnspan=3, padx=10, pady=10)
        

        self.refresh_comboboxes()

    def refresh_comboboxes(self):
        joystick_names = [joystick.get_name() for joystick in self.joysticks]
        self.combo_joysticks["values"] = joystick_names
        self.combo_buttons["values"] = [f"Botão {i}" for i in range(16)]
        self.combo_keys["values"] = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                                     "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                                     "u", "v", "w", "x", "y", "z", "0", "1", "2", "3",
                                     "4", "5", "6", "7", "8", "9", "esc", "enter", "space",
                                     "botão direito do mouse"]
        self.config_listbox.delete(0, tk.END)
        configs = self.read_configs()
        for config in configs:
            joystick_index, button_index, key = config[3], config[1], config[2]
            self.config_listbox.insert(tk.END, f"Controle: {joystick_names[joystick_index]}, Botão: {button_index}, Tecla: {key}")

    def save_config(self):
        selected_joystick_index = self.combo_joysticks.current()
        selected_button_index = self.combo_buttons.current()
        selected_key = self.combo_keys.get()

        if selected_joystick_index >= 0 and selected_button_index >= 0 and selected_key:
            self.write_config(selected_button_index, selected_key, selected_joystick_index)
            self.refresh_comboboxes()  # Update the comboboxes to show the new configuration

def main():
    try:
        
        root = tk.Tk()
        app = ConfigurationApp(root)
        root.mainloop()

    except Exception as e:
        print("Erro:", e)

    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
