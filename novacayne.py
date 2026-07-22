import os
import time
import threading
import math
import random
import pygame
import customtkinter as ctk
from tkinter import filedialog
from mutagen.mp3 import MP3
from mutagen.mp3 import EasyMP3
from PIL import Image

# --- Configuration & Styling ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        pygame.mixer.init()

        # State Variables
        self.playlist = []
        self.current_track_index = -1
        self.is_playing = False
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)

        # Window Configuration
        self.title("NovaCAynE Player By: JethroTeK")
        self.geometry("1000x700")
        
        # Layout Config
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- UI Components ---
        # Left Side: Playlist Panel
        self.playlist_frame = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.playlist_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.label_list = ctk.CTkLabel(self.playlist_frame, text="LIBRARY", font=("Arial", 28, "bold"))
        self.label_list.pack(pady=(20, 10))

        self.scrollable_frame = ctk.CTkScrollableFrame(self.playlist_frame, width=320)
        self.scrollable_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Right Side: Player Control Panel
        self.player_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.player_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Track Information Display
        self.track_label = ctk.CTkLabel(self.player_frame, text="No Track Selected", font=("Arial", 36, "bold"))
        self.track_label.pack(pady=(120, 10))
        
        self.artist_label = ctk.CTkLabel(self.player_frame, text="Select a song to begin", font=("Arial", 18), text_color="gray")
        self.artist_label.pack(pady=5)

        # Seekable Progress Slider
        # Using a slider ensures that the mouse interaction is captured correctly by the OS/GUI layer.
        self.progress_slider = ctk.CTkSlider(
            self.player_frame, 
            from_=0, 
            to=1, 
            width=500, 
            height=20,
            button_color="#1f5bd1",
            button_hover_color="#3a86ff",
            progress_color="#1f5bd1"
        )
        self.progress_slider.set(0)
        # Bind the slider to the seek function
        self.progress_slider.configure(command=self.seek_music)
        self.progress_slider.pack(pady=10)

        # Media Control Row
        self.controls_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.controls_frame.pack(pady=20)

        self.btn_prev = ctk.CTkButton(self.controls_frame, text="⏮", width=60, command=self.prev_track)
        self.btn_prev.grid(row=0, column=0, padx=15)

        self.btn_play = ctk.CTkButton(self.controls_frame, text="▶", width=100, command=self.toggle_play)
        self.btn_play.grid(row=0, column=1, padx=15)

        self.btn_next = ctk.CTkButton(self.controls_frame, text="⏭", width=60, command=self.next_track)
        self.btn_next.grid(row=0, column=2, padx=15)

        # Volume Slider
        self.volume_slider = ctk.CTkSlider(self.player_frame, from_=0, to=1, width=400, command=self.set_volume)
        self.volume_slider.set(self.volume)
        self.volume_slider.pack(pady=20)

        # Branding / Logo Section
        self.branding_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.branding_frame.pack(side="bottom", pady=30)
        
        try:
            logo_path = "logo.png" # Replace with your actual file path
            if os.path.exists(logo_path):
                raw_img = Image.open(logo_path)
                new_width = 150
                w, h = raw_img.size
                aspect = h / w
                res_img = raw_img.resize((new_width, int(new_width * aspect)), Image.Resampling.LANCZOS)
                self.logo_image = ctk.CTkImage(light_image=res_img, dark_image=res_img, size=(150, int(150 * (h/w))))
                self.logo_label = ctk.CTkLabel(self.branding_frame, text="", image=self.logo_image)
            else:
                self.logo_label = ctk.CTkLabel(self.branding_frame, text="NovaCAynE Player By: JethroTeK", font=("Arial", 14, "bold"), text_color="#5a5a5a")
        except:
            self.logo_label = ctk.CTkLabel(self.branding_frame, text="NovaCAynE Player By: JethroTeK", font=("Arial", 14, "bold"), text_color="#5a5a5a")
        
        self.logo_label.pack()

        # Add Folder Button
        self.btn_add = ctk.CTkButton(self.playlist_frame, text="Add Music Folder", command=self.load_folder)
        self.btn_add.pack(side="bottom", pady=30)

        # Background Thread for Logic
        self.logic_thread = threading.Thread(target=self.update_engine, daemon=True)
        self.logic_thread.start()

    # --- Interaction Functions ---

    def load_folder(self):
        path = filedialog.askdirectory()
        if path:
            files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".mp3")]
            if files:
                self.playlist = files
                self.populate_playlist_ui()
                self.current_track_index = 0
                self.update_track_info()

    def populate_playlist_ui(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for i, track in enumerate(self.playlist):
            name = os.path.basename(track)
            btn = ctk.CTkButton(self.scrollable_frame, text=name, anchor="w", 
                                 fg_color="transparent", text_color="white", 
                                 hover_color="#333333", command=lambda i=i: self.select_track(i))
            btn.pack(fill="x", pady=2)

    def update_track_info(self):
        if self.current_track_index != -1:
            path = self.playlist[self.current_track_index]
            try:
                audio = EasyMP3(path)
                title = audio.get('title', [os.path.basename(path)])[0]
                artist = audio.get('artist', ['Unknown Artist'])[0]
                self.track_label.configure(text=title[:45])
                self.artist_label.configure(text=f"{artist} | {title}")
            except:
                name = os.path.basename(path)
                self.track_label.configure(text=name[:45])
                self.artist_label.configure(text="Unknown Artist")

    def select_track(self, index):
        self.current_track_index = index
        self.update_track_info()
        if not self.is_playing:
            self.play_music()
        else:
            pygame.mixer.music.load(self.playlist[index])
            pygame.mixer.music.play()

    def play_music(self):
        if self.current_track_index != -1:
            pygame.mixer.music.load(self.playlist[self.current_track_index])
            pygame.mixer.music.play()
            self.is_playing = True
            self.btn_play.configure(text="⏸")

    def toggle_play(self):
        if not self.is_playing and self.current_track_index != -1:
            self.play_music()
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.configure(text="▶")

    def next_track(self):
        if self.current_track_index != -1:
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
            self.update_track_info()
            self.play_music()

    def prev_track(self):
        if self.current_track_index != -1:
            self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
            self.update_track_info()
            self.play_music()

    def set_volume(self, val):
        self.volume = float(val)
        pygame.mixer.music.set_volume(self.volume)

    def seek_music(self, value):
        """Handles the calculation when a user drags or clicks the slider."""
        if self.current_track_index != -1:
            path = self.playlist[self.current_track_index]
            audio_info = MP3(path)
            duration = audio_info.info.length
            # Calculate new position and tell pygame to jump there
            # duration is in seconds, value is 0.0 - 1.0
            new_time = value * duration
            pygame.mixer.music.play(start=new_time)

    def update_engine(self):
        """Background thread handles progress syncing and auto-advance."""
        while True:
            time.sleep(1)
            if self.is_playing and self.current_track_index != -1:
                try:
                    pos = pygame.mixer.music.get_pos() # ms
                    path = self.playlist[self.current_track_index]
                    audio_info = MP3(path)
                    duration = audio_info.info.length # seconds

                    if duration > 0:
                        # Update the slider position to match current play time automatically
                        progress = pos / (duration * 1000)
                        self.progress_slider.set(min(progress, 1.0))

                    # Auto-advance logic
                    if pos >= (duration * 1000 - 2000): # 2 second buffer
                        self.next_track()
                except:
                    pass
            else:
                self.progress_slider.set(0)

if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()