import dearpygui.dearpygui as dpg
import ntpath
import json
from mutagen.mp3 import MP3
from tkinter import Tk, filedialog
import threading
import pygame
import time
import random
import os
import atexit

_DEFAULT_MUSIC_VOLUME = 0.5


class MusicPlayer:
    def __init__(self):
        dpg.create_context()
        dpg.create_viewport(title="El - Sambo Music",
                            large_icon="music.ico", small_icon="music.ico")
        pygame.mixer.init()
        self.state = None
        self.no = 0
        self.DEFAULT_MUSIC_VOLUME = 0.5
        pygame.mixer.music.set_volume(self.DEFAULT_MUSIC_VOLUME)
        # ... (other initialization code)

    def update_volume(self, sender, app_data):
        pygame.mixer.music.set_volume(app_data / 100.0)
        # ... (other methods related to music playing)

    def load_database(self):
        songs = json.load(open("data/songs.json", "r+"))["songs"]
        for filename in songs:
            dpg.add_button(label=f"{ntpath.basename(filename)}", callback=self.play, width=-1,
                           height=25, user_data=filename.replace("\\", "/"), parent="list")
            dpg.add_spacer(height=2, parent="list")
        # ... (other database-related methods)

    def update_slider(self):
        while pygame.mixer.music.get_busy() or self.state != 'paused':
            dpg.configure_item(
                item="pos", default_value=pygame.mixer.music.get_pos() / 1000)
            time.sleep(0.7)
        self.state = None
        dpg.configure_item("cstate", default_value=f"State: None")
        dpg.configure_item("csong", default_value="Now Playing : ")
        dpg.configure_item("play", label="Play")
        dpg.configure_item(item="pos", max_value=100)
        dpg.configure_item(item="pos", default_value=0)
        # ... (other slider-related methods)

    def toggle_repeat(self):
        self.is_repeating = not self.is_repeating
        if self.is_repeating:
            pygame.mixer.music.play(-1)  # Ulangi lagu saat selesai
        else:
            pygame.mixer.music.play()
    
    def play(self, sender, app_data, user_data):
        if user_data:
            self.no = user_data
            pygame.mixer.music.load(user_data)
            audio = MP3(user_data)
            dpg.configure_item(item="pos", max_value=audio.info.length)
            pygame.mixer.music.play()
            thread = threading.Thread(
                target=self.update_slider, daemon=False).start()
            if pygame.mixer.music.get_busy():
                dpg.configure_item("play", label="Pause")
                self.state = "playing"
                dpg.configure_item("cstate", default_value=f"State: Playing")
                dpg.configure_item(
                    "csong", default_value=f"Now Playing : {ntpath.basename(user_data)}")
                
        # ... (other play-related methods)

    def play_pause(self):
        if self.state == "playing":
            self.state = "paused"
            pygame.mixer.music.pause()
            dpg.configure_item("play", label="Play")
            dpg.configure_item("cstate", default_value=f"State: Paused")
        elif self.state == "paused":
            self.state = "playing"
            pygame.mixer.music.unpause()
            dpg.configure_item("play", label="Pause")
            dpg.configure_item("cstate", default_value=f"State: Playing")
        else:
            song = json.load(open("data/songs.json", "r"))["songs"]
            if song:
                song = random.choice(song)
                self.no = song
                pygame.mixer.music.load(song)
                pygame.mixer.music.play()
                thread = threading.Thread(
                    target=self.update_slider, daemon=False).start()
                dpg.configure_item("play", label="Pause")
                if pygame.mixer.music.get_busy():
                    audio = MP3(song)
                    dpg.configure_item(item="pos", max_value=audio.info.length)
                    self.state = "playing"
                    dpg.configure_item(
                        "csong", default_value=f"Now Playing : {ntpath.basename(song)}")
                    dpg.configure_item(
                        "cstate", default_value=f"State: Playing")

    def pre(self):
        songs = json.load(open('data/songs.json', 'r'))["songs"]
        try:
            n = songs.index(self.no)
            if n == 0:
                n = len(songs)
            self.play(sender=any, app_data=any, user_data=songs[n - 1])
        except:
            pass
        # ... (other pre-related methods)

    def next(self):
        songs = json.load(open('data/songs.json', 'r'))["songs"]
        try:
            n = songs.index(self.no)
            if n == len(songs) - 1:
                n = -1
            self.play(sender=any, app_data=any, user_data=songs[n + 1])
        except:
            pass
        # ... (other next-related methods)

    def stop(self):
        pygame.mixer.music.stop()
        self.state = None
        # ... (other stop-related methods)


class MusicDatabase:
    def add_files(self):
        data = json.load(open("data/songs.json", "r"))
        root = Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(
            filetypes=[("Music Files", ("*.mp3", "*.wav", "*.ogg"))])
        root.quit()
        if filename.endswith((".mp3", ".wav", ".ogg")):
            if filename not in data["songs"]:
                self.update_database(filename)
                dpg.add_button(label=f"{ntpath.basename(filename)}", callback=music_player.play,
                               width=-1, height=25, user_data=filename.replace("\\", "/"), parent="list")
                dpg.add_spacer(height=2, parent="list")

    def add_folder(self):
        data = json.load(open("data/songs.json", "r"))
        root = Tk()
        root.withdraw()
        folder = filedialog.askdirectory()
        root.quit()
        for filename in os.listdir(folder):
            if filename.endswith((".mp3", ".wav", ".ogg")):
                if filename not in data["songs"]:
                    self.update_database(os.path.join(
                        folder, filename).replace("\\", "/"))
                    dpg.add_button(label=f"{ntpath.basename(filename)}", callback=music_player.play,
                                   width=-1, height=25, user_data=os.path.join(folder, filename).replace("\\", "/"),
                                   parent="list")
                    dpg.add_spacer(height=2, parent="list")

    def search(self, sender, app_data, user_data):
        songs = json.load(open("data/songs.json", "r"))["songs"]
        dpg.delete_item("list", children_only=True)
        for index, song in enumerate(songs):
            if app_data in song.lower():
                dpg.add_button(label=f"{ntpath.basename(song)}", callback=music_player.play,
                               width=-1, height=25, user_data=song, parent="list")
                dpg.add_spacer(height=2, parent="list")

    def remove_all(self):
        songs = json.load(open("data/songs.json", "r"))
        songs["songs"].clear()
        json.dump(songs, open("data/songs.json", "w"), indent=4)
        dpg.delete_item("list", children_only=True)
        music_player.load_database()

    def update_database(self, filename: str):
        data = json.load(open("data/songs.json", "r+"))
        if filename not in data["songs"]:
            data["songs"] += [filename]
        json.dump(data, open("data/songs.json", "r+"), indent=4)


class GUI:
    def setup_theme(self):
        with dpg.theme(tag="base"):
            with dpg.theme_component():
                dpg.add_theme_color(dpg.mvThemeCol_Button, (130, 142, 250))
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonActive, (137, 142, 255, 95))
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonHovered, (137, 142, 255))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4, 4)
                dpg.add_theme_style(
                    dpg.mvStyleVar_WindowTitleAlign, 0.50, 0.50)
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 14)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (25, 25, 25))
                dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0))
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (0, 0, 0, 0))
                dpg.add_theme_color(
                    dpg.mvThemeCol_TitleBgActive, (130, 142, 250))
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (221, 166, 185))
                dpg.add_theme_color(
                    dpg.mvThemeCol_FrameBgHovered, (172, 174, 197))

            with dpg.theme(tag="slider_thin"):
                with dpg.theme_component():
                    dpg.add_theme_color(
                        dpg.mvThemeCol_FrameBgActive, (130, 142, 250, 99))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_FrameBgHovered, (130, 142, 250, 99))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_SliderGrab, (255, 255, 255))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_FrameBg, (130, 142, 250, 99))
                    dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
                    dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

            with dpg.theme(tag="slider"):
                with dpg.theme_component():
                    dpg.add_theme_color(
                        dpg.mvThemeCol_FrameBgActive, (130, 142, 250, 99))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_FrameBgHovered, (130, 142, 250, 99))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_SliderGrab, (255, 255, 255))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_FrameBg, (130, 142, 250, 99))
                    dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
                    dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

            with dpg.theme(tag="songs"):
                with dpg.theme_component():
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)
                    dpg.add_theme_color(
                        dpg.mvThemeCol_Button, (89, 89, 144, 40))
                    dpg.add_theme_color(
                        dpg.mvThemeCol_ButtonHovered, (0, 0, 0, 0))

            with dpg.font_registry():
                monobold = dpg.add_font("fonts/MonoLisa-Bold.ttf", 12)
                head = dpg.add_font("fonts/MonoLisa-Bold.ttf", 15)

        dpg.bind_theme("base")
        dpg.bind_font(monobold)

    def create_gui(self):
        def add_files_callback():
            music_database.add_files()

        def add_folder_callback():
            music_database.add_folder()

        def removeall_callback():
            music_database.remove_all()

        def play_pause_callback():
            music_player.play_pause()

        def pre_callback():
            music_player.pre()

        def next_callback():
            music_player.next()

        def stop_callback():
            music_player.stop()

        def update_volume_callback():
            music_player.update_volume()

        def search_callback():
            music_database.search()

        def load_database_callback():
            music_player.load_database()
        
        def toggle_repeat_callback():
            music_player.toggle_repeat()

        with dpg.window(tag="main", label="window title"):
            with dpg.child_window(autosize_x=True, height=45, no_scrollbar=True):
                dpg.add_text(f"Now Playing : ", tag="csong")
            dpg.add_spacer(height=2)

            with dpg.group(horizontal=True):
                with dpg.child_window(width=200, tag="sidebar"):
                    dpg.add_text("El - Sambo Musicart", color=(137, 142, 255))
                    dpg.add_text("Build by Kelompok 2")
                    dpg.add_spacer(height=2)
                    dpg.add_button(label="Support", width=-1, height=23)
                    dpg.add_spacer(height=5)
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    dpg.add_button(label="Add File", width=-1,
                                   height=28, callback=add_files_callback)
                    dpg.add_button(label="Add Folder", width=-1,
                                   height=28, callback=add_folder_callback)
                    dpg.add_button(label="Remove All Songs", width=-1,
                                   height=28, callback=removeall_callback)
                    dpg.add_spacer(height=5)
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    dpg.add_text(f"State: {music_player.state}", tag="cstate")
                    dpg.add_spacer(height=5)
                    dpg.add_separator()

                with dpg.child_window(autosize_x=True, height=620, no_scrollbar=True):

                    with dpg.child_window(autosize_x=True, height=550, delay_search=True):
                        with dpg.group(horizontal=True, tag="query"):
                            dpg.add_input_text(
                                hint="Search for a song", width=-1, callback=search_callback)
                        dpg.add_spacer(height=5)
                        with dpg.child_window(autosize_x=True, height=470, delay_search=True, tag="list"):
                            load_database_callback()
                    
                    with dpg.group(horizontal=True, pos=(372, 580)):
                        dpg.add_button(
                            label="Repeat", callback=toggle_repeat_callback, width=80, height=30)
                        dpg.add_button(
                            label="Play", width=65, height=30, tag="play", callback=play_pause_callback)
                        dpg.add_button(
                            label="Pre", width=65, height=30, show=True, tag="pre", callback=pre_callback)
                        dpg.add_button(
                            label="Next", tag="next", show=True, callback=next_callback, width=65, height=30)
                        dpg.add_button(
                            label="Stop", callback=stop_callback, width=65, height=30)
                        
                    with dpg.child_window(autosize_x=True, height=30, no_scrollbar=True, pos=(5, 530)):
                        with dpg.group(horizontal=True):
                            with dpg.group(horizontal=True):
                                dpg.add_slider_float(tag="volume", width=120, height=5, pos=(
                                    10, 0), format="%.0f%.0%", default_value=_DEFAULT_MUSIC_VOLUME * 100, callback=update_volume_callback)
                                dpg.add_slider_float(
                                    tag="pos", width=-1, pos=(140, 0), format="")

            dpg.bind_item_theme("volume", "slider_thin")
            dpg.bind_item_theme("pos", "slider")
            dpg.bind_item_theme("list", "songs")
            dpg.set_primary_window("main", True)

    def safe_exit(self):
        pygame.mixer.music.stop()
        pygame.quit()

    def run_gui(self):
        self.setup_theme()
        atexit.register(GUI.safe_exit)
        self.create_gui()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main", True)
        dpg.maximize_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


# Inisialisasi MusicPlayer dan GUI
music_player = MusicPlayer()
music_database = MusicDatabase()
gui_instance = GUI()  # Buat objek dari kelas GUI
gui_instance.run_gui()  # Panggil metode run_gui() dari objek yang telah dibuat