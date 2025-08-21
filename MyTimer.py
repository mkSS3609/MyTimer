import customtkinter as ctk
import pygame
import time
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Константы
COLOR_BG = '#4d2673'
COLOR_BUTTON = '#5e2f8c'
COLOR_ACCENT = '#6b35a1'
SYMBOL_START = "▶"
SYMBOL_PAUSE = "⏸"
SYMBOL_STOP = "⏹"
SYMBOL_RESUME = "▷"
INTERVALS = [180, 60, 180, 60, 180, 60, 180, 60]
SOUND_FILE = resource_path('sound.wav')
ICON_FILE = resource_path('icon.ico')

class MyTimer:
    def __init__(self, root):
        self.root = root
        self.root.configure(fg_color=COLOR_BG)
        self.root.iconbitmap(ICON_FILE)
        self.root.title("MyTimer")
        self.root.geometry('220x140')
        self.root.resizable(False, False)
        self.root.wm_attributes('-alpha', 0.96)
        self.root.attributes('-topmost', True)

        pygame.mixer.init()

        self.timer_page = None
        self.timer_id = None
        self.is_timer_running = False
        self.is_timer_paused = False
        self.remaining_time = 0
        self.current_index = 0
        self.start_time = 0
        self.close_after_finish = ctk.BooleanVar(value=True)

        self.start_button = None
        self.pause_button = None
        self.progress_bar = None
        self.textbox_water = None

        self.setup_ui()

    def setup_ui(self):
        self.timer_page = ctk.CTkFrame(self.root, fg_color="transparent")
        self.timer_page.pack(expand=True, fill="both")

        self.start_button = ctk.CTkButton(
            self.timer_page,
            text=SYMBOL_START,
            font=("Segoe UI Symbol", 16),
            corner_radius=10,
            fg_color=COLOR_BUTTON,
            text_color="white",
            width=60,
            hover_color=COLOR_ACCENT,
            command=self.toggle_timer
        )
        self.start_button.place(x=10, y=10)

        self.pause_button = ctk.CTkButton(
            self.timer_page,
            text=SYMBOL_PAUSE,
            font=("Segoe UI Symbol", 16),
            corner_radius=10,
            fg_color=COLOR_BUTTON,
            text_color="white",
            width=60,
            hover_color=COLOR_ACCENT,
            command=self.toggle_pause
        )
        self.pause_button.place(x=80, y=10)

        close_checkbox = ctk.CTkCheckBox(
            self.timer_page,
            text="",
            fg_color=COLOR_BUTTON,
            text_color="white",
            hover_color=COLOR_ACCENT,
            border_color=COLOR_BUTTON,
            border_width=2,
            corner_radius=10,
            checkbox_width=60,
            checkbox_height=30,
            variable=self.close_after_finish
        )
        close_checkbox.place(x=150, y=10)

        self.progress_bar = ctk.CTkProgressBar(
            self.timer_page,
            width=200,
            height=20,
            corner_radius=10,
            fg_color=COLOR_BUTTON,
            progress_color="#7B4A9E"
        )
        self.progress_bar.place(x=10, y=50)
        self.progress_bar.set(0)

        self.textbox_water = ctk.CTkLabel(
            self.timer_page, text="", font=("Book Antiqua", 20, "bold"),
            text_color="white", fg_color=COLOR_BUTTON, width=200, height=50,
            corner_radius=20
        )
        self.textbox_water.place(x=10, y=80, anchor="nw")

    @staticmethod
    def play_sound():
        if os.path.exists(SOUND_FILE):
            try:
                pygame.mixer.music.load(SOUND_FILE)
                pygame.mixer.music.play()
            except pygame.error as e:
                print(f"Ошибка воспроизведения звука: {e}")
        else:
            print(f"Звуковой файл {SOUND_FILE} не найден")

    def update_progress_bar(self):
        if self.is_timer_running and not self.is_timer_paused:
            elapsed = time.time() - self.start_time
            interval = INTERVALS[self.current_index]
            progress = min(elapsed / interval, 1.0)
            self.progress_bar.set(progress)
            if progress < 1.0:
                self.root.after(100, self.update_progress_bar)
            else:
                self.progress_bar.set(0)

    def run_timer(self, index=0):
        self.current_index = index
        if index < len(INTERVALS) and self.is_timer_running:
            interval = INTERVALS[index]
            if not self.is_timer_paused:
                water_state = "ГОРЯЧАЯ" if index % 2 == 0 else "ХОЛОДНАЯ"
                self.textbox_water.configure(text=f"{index + 1}/8 {water_state}")
                self.play_sound()
                self.remaining_time = interval
                self.start_time = time.time()
                self.update_progress_bar()
            self.timer_id = self.root.after(
                int(self.remaining_time * 1000),
                lambda: self.run_timer(index + 1)
            )
        else:
            self.textbox_water.configure(text="")
            self.play_sound()
            self.reset_timer()
            if self.close_after_finish.get():
                self.root.after(5000, self.root.destroy)

    def toggle_timer(self):
        if not self.is_timer_running:
            self.is_timer_running = True
            self.is_timer_paused = False
            self.start_button.configure(text=SYMBOL_STOP)
            self.pause_button.configure(text=SYMBOL_PAUSE)
            self.textbox_water.configure(text="")
            self.run_timer()
        else:
            self.reset_timer()

    def toggle_pause(self):
        if self.is_timer_running:
            if not self.is_timer_paused:
                self.is_timer_paused = True
                if self.timer_id is not None:
                    self.root.after_cancel(self.timer_id)
                    self.timer_id = None
                self.pause_button.configure(text=SYMBOL_RESUME)
                self.remaining_time = INTERVALS[self.current_index] - (time.time() - self.start_time)
            else:
                self.is_timer_paused = False
                self.pause_button.configure(text=SYMBOL_PAUSE)
                self.start_time = time.time() - (INTERVALS[self.current_index] - self.remaining_time)
                self.update_progress_bar()
                self.timer_id = self.root.after(
                    int(self.remaining_time * 1000), lambda: self.run_timer(self.current_index + 1)
                )

    def reset_timer(self):
        self.is_timer_running = False
        self.is_timer_paused = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.start_button.configure(text=SYMBOL_START)
        self.pause_button.configure(text=SYMBOL_PAUSE)
        self.progress_bar.set(0)
        self.textbox_water.configure(text="")
        self.remaining_time = 0
        self.current_index = 0

def main():
    root = ctk.CTk()
    MyTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
