import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyttsx3
import threading
import os
import sys
import subprocess
import re


class TextToSpeechApp:

    def __init__(self, root):

        # =====================================================
        # WINDOW
        # =====================================================

        self.root = root

        self.root.title(
            "Text-to-Speech Desktop App"
        )

        self.root.geometry(
            "1000x720"
        )

        self.root.minsize(
            850,
            650
        )

        self.root.configure(
            bg="#f4f6f8"
        )

        # =====================================================
        # COLORS
        # =====================================================

        self.BG = "#f4f6f8"
        self.CARD = "#ffffff"
        self.TEXT = "#111827"
        self.SECONDARY = "#6b7280"
        self.BORDER = "#e5e7eb"

        self.BLUE = "#2563eb"
        self.BLUE_HOVER = "#1d4ed8"

        self.GREEN = "#16a34a"
        self.GREEN_HOVER = "#15803d"

        self.ORANGE = "#f59e0b"
        self.ORANGE_HOVER = "#d97706"

        self.RED = "#dc2626"
        self.RED_HOVER = "#b91c1c"

        self.PURPLE = "#7c3aed"
        self.PURPLE_HOVER = "#6d28d9"

        self.GRAY = "#64748b"
        self.GRAY_HOVER = "#475569"

        # =====================================================
        # SPEECH ENGINE
        # =====================================================

        try:

            self.engine = pyttsx3.init()

        except Exception as error:

            messagebox.showerror(
                "Speech Engine Error",
                "Unable to start the speech engine.\n\n"
                + str(error)
            )

            self.root.destroy()
            return

        # =====================================================
        # STATE
        # =====================================================

        self.voices = []

        self.is_speaking = False
        self.is_paused = False
        self.stop_requested = False

        self.current_text = ""

        self.current_sentence_index = 0

        self.sentences = []

        # =====================================================
        # OUTPUT FOLDER
        # =====================================================

        self.output_folder = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "output"
        )

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

        # =====================================================
        # VARIABLES
        # =====================================================

        self.speed_var = tk.IntVar(
            value=170
        )

        self.volume_var = tk.DoubleVar(
            value=1.0
        )

        self.voice_var = tk.StringVar()

        self.speed_text_var = tk.StringVar(
            value="170"
        )

        self.volume_text_var = tk.StringVar(
            value="100%"
        )

        self.status_var = tk.StringVar(
            value="Ready"
        )

        self.count_var = tk.StringVar(
            value="0 characters | 0 words"
        )

        # =====================================================
        # STYLE
        # =====================================================

        self.setup_style()

        # =====================================================
        # GUI
        # =====================================================

        self.create_gui()

        # =====================================================
        # LOAD VOICES
        # =====================================================

        self.load_voices()

        # =====================================================
        # WINDOW CLOSE
        # =====================================================

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

    # =========================================================
    # STYLE
    # =========================================================

    def setup_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")

        except tk.TclError:
            pass

        style.configure(
            "TCombobox",
            padding=8,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Horizontal.TProgressbar",
            thickness=6
        )

    # =========================================================
    # CREATE GUI
    # =========================================================

    def create_gui(self):

        # =====================================================
        # HEADER
        # =====================================================

        header = tk.Frame(
            self.root,
            bg=self.BG
        )

        header.pack(
            fill="x",
            padx=30,
            pady=(20, 8)
        )

        title = tk.Label(
            header,
            text="Text-to-Speech",
            font=(
                "Segoe UI",
                27,
                "bold"
            ),
            bg=self.BG,
            fg=self.TEXT
        )

        title.pack(
            anchor="w"
        )

        subtitle = tk.Label(
            header,
            text="Convert typed text into spoken audio",
            font=(
                "Segoe UI",
                11
            ),
            bg=self.BG,
            fg=self.SECONDARY
        )

        subtitle.pack(
            anchor="w",
            pady=(2, 0)
        )

        # =====================================================
        # MAIN CARD
        # =====================================================

        card = tk.Frame(
            self.root,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        card.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=12
        )

        # =====================================================
        # TEXT HEADER
        # =====================================================

        text_header = tk.Frame(
            card,
            bg=self.CARD
        )

        text_header.pack(
            fill="x",
            padx=22,
            pady=(18, 7)
        )

        text_title = tk.Label(
            text_header,
            text="Enter Text",
            font=(
                "Segoe UI",
                14,
                "bold"
            ),
            bg=self.CARD,
            fg=self.TEXT
        )

        text_title.pack(
            side="left"
        )

        count_label = tk.Label(
            text_header,
            textvariable=self.count_var,
            font=(
                "Segoe UI",
                9
            ),
            bg=self.CARD,
            fg=self.SECONDARY
        )

        count_label.pack(
            side="right"
        )

        # =====================================================
        # TEXT AREA
        # =====================================================

        text_frame = tk.Frame(
            card,
            bg=self.CARD
        )

        text_frame.pack(
            fill="x",
            padx=22
        )

        self.text_box = tk.Text(
            text_frame,
            height=12,
            wrap="word",
            font=(
                "Segoe UI",
                12
            ),
            bg="#fafafa",
            fg=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            bd=0,
            padx=15,
            pady=12,
            undo=True
        )

        self.text_box.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self.text_box.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.text_box.configure(
            yscrollcommand=scrollbar.set
        )

        self.text_box.bind(
            "<KeyRelease>",
            self.update_count
        )

        # =====================================================
        # SETTINGS AREA
        # =====================================================

        settings = tk.Frame(
            card,
            bg=self.CARD
        )

        settings.pack(
            fill="x",
            padx=22,
            pady=(15, 8)
        )

        # -----------------------------------------------------
        # VOICE
        # -----------------------------------------------------

        voice_label = tk.Label(
            settings,
            text="Voice",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg=self.CARD,
            fg=self.TEXT
        )

        voice_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8)
        )

        self.voice_combo = ttk.Combobox(
            settings,
            textvariable=self.voice_var,
            state="readonly",
            width=28
        )

        self.voice_combo.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 20)
        )

        # -----------------------------------------------------
        # SPEED
        # -----------------------------------------------------

        speed_label = tk.Label(
            settings,
            text="Speed",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg=self.CARD,
            fg=self.TEXT
        )

        speed_label.grid(
            row=0,
            column=2,
            sticky="w"
        )

        self.speed_scale = tk.Scale(
            settings,
            from_=50,
            to=300,
            orient="horizontal",
            variable=self.speed_var,
            showvalue=False,
            bg=self.CARD,
            fg=self.TEXT,
            highlightthickness=0,
            troughcolor="#dbeafe",
            activebackground=self.BLUE,
            width=10,
            length=150,
            command=self.speed_changed
        )

        self.speed_scale.grid(
            row=0,
            column=3,
            padx=(5, 5)
        )

        speed_value = tk.Label(
            settings,
            textvariable=self.speed_text_var,
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            bg=self.CARD,
            fg=self.BLUE,
            width=4
        )

        speed_value.grid(
            row=0,
            column=4,
            padx=(0, 18)
        )

        # -----------------------------------------------------
        # VOLUME
        # -----------------------------------------------------

        volume_label = tk.Label(
            settings,
            text="Volume",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg=self.CARD,
            fg=self.TEXT
        )

        volume_label.grid(
            row=0,
            column=5,
            sticky="w"
        )

        self.volume_scale = tk.Scale(
            settings,
            from_=0,
            to=1,
            resolution=0.1,
            orient="horizontal",
            variable=self.volume_var,
            showvalue=False,
            bg=self.CARD,
            fg=self.TEXT,
            highlightthickness=0,
            troughcolor="#dcfce7",
            activebackground=self.GREEN,
            width=10,
            length=130,
            command=self.volume_changed
        )

        self.volume_scale.grid(
            row=0,
            column=6,
            padx=(5, 5)
        )

        volume_value = tk.Label(
            settings,
            textvariable=self.volume_text_var,
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            bg=self.CARD,
            fg=self.GREEN,
            width=5
        )

        volume_value.grid(
            row=0,
            column=7
        )

        settings.columnconfigure(
            1,
            weight=1
        )

        # =====================================================
        # BUTTONS
        # =====================================================

        button_frame = tk.Frame(
            card,
            bg=self.CARD
        )

        button_frame.pack(
            fill="x",
            padx=22,
            pady=(5, 18)
        )

        # Play
        self.play_button = self.create_button(
            button_frame,
            "▶  Play",
            self.play_text,
            self.BLUE,
            self.BLUE_HOVER
        )

        self.play_button.pack(
            side="left",
            padx=(0, 6)
        )

        # Pause
        self.pause_button = self.create_button(
            button_frame,
            "⏸  Pause",
            self.pause_speech,
            self.ORANGE,
            self.ORANGE_HOVER
        )

        self.pause_button.pack(
            side="left",
            padx=6
        )

        # Resume
        self.resume_button = self.create_button(
            button_frame,
            "▶  Resume",
            self.resume_speech,
            self.GREEN,
            self.GREEN_HOVER
        )

        self.resume_button.pack(
            side="left",
            padx=6
        )

        # Stop
        self.stop_button = self.create_button(
            button_frame,
            "⏹  Stop",
            self.stop_speech,
            self.RED,
            self.RED_HOVER
        )

        self.stop_button.pack(
            side="left",
            padx=6
        )

        # Save
        self.save_button = self.create_button(
            button_frame,
            "💾  Save Audio",
            self.save_audio,
            self.PURPLE,
            self.PURPLE_HOVER
        )

        self.save_button.pack(
            side="left",
            padx=6
        )

        # Clear
        self.clear_button = self.create_button(
            button_frame,
            "Clear",
            self.clear_text,
            self.GRAY,
            self.GRAY_HOVER
        )

        self.clear_button.pack(
            side="left",
            padx=6
        )

        # Output folder
        self.folder_button = self.create_button(
            button_frame,
            "Output Folder",
            self.open_output_folder,
            "#334155",
            "#1e293b"
        )

        self.folder_button.pack(
            side="right"
        )

        # =====================================================
        # STATUS BAR
        # =====================================================

        status_frame = tk.Frame(
            self.root,
            bg=self.BG
        )

        status_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 12)
        )

        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=(
                "Segoe UI",
                9
            ),
            bg=self.BG,
            fg=self.SECONDARY
        )

        status_label.pack(
            side="left"
        )

        technology_label = tk.Label(
            status_frame,
            text="Python  •  Tkinter  •  pyttsx3",
            font=(
                "Segoe UI",
                9
            ),
            bg=self.BG,
            fg=self.SECONDARY
        )

        technology_label.pack(
            side="right"
        )

    # =========================================================
    # BUTTON CREATOR
    # =========================================================

    def create_button(
        self,
        parent,
        text,
        command,
        color,
        hover_color
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            bg=color,
            fg="white",
            activebackground=hover_color,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2"
        )

        button.bind(
            "<Enter>",
            lambda event: button.configure(
                bg=hover_color
            )
        )

        button.bind(
            "<Leave>",
            lambda event: button.configure(
                bg=color
            )
        )

        return button

    # =========================================================
    # LOAD VOICES
    # =========================================================

    def load_voices(self):

        try:

            self.voices = self.engine.getProperty(
                "voices"
            )

            voice_names = []

            for index, voice in enumerate(
                self.voices
            ):

                name = getattr(
                    voice,
                    "name",
                    None
                )

                if not name:
                    name = f"Voice {index + 1}"

                voice_names.append(
                    name
                )

            self.voice_combo["values"] = (
                voice_names
            )

            if voice_names:

                self.voice_combo.current(0)

                self.update_status(
                    f"{len(voice_names)} voice(s) available"
                )

            else:

                self.update_status(
                    "No system voices found"
                )

        except Exception as error:

            messagebox.showerror(
                "Voice Error",
                "Could not load voices.\n\n"
                + str(error)
            )

    # =========================================================
    # SPEED
    # =========================================================

    def speed_changed(self, value):

        speed = int(
            float(value)
        )

        self.speed_text_var.set(
            str(speed)
        )

    # =========================================================
    # VOLUME
    # =========================================================

    def volume_changed(self, value):

        volume = float(value)

        percentage = int(
            volume * 100
        )

        self.volume_text_var.set(
            f"{percentage}%"
        )

    # =========================================================
    # GET TEXT
    # =========================================================

    def get_text(self):

        return self.text_box.get(
            "1.0",
            tk.END
        ).strip()

    # =========================================================
    # SPLIT INTO SENTENCES
    # =========================================================

    def split_sentences(self, text):

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        return sentences

    # =========================================================
    # PLAY
    # =========================================================

    def play_text(self):

        text = self.get_text()

        if not text:

            messagebox.showwarning(
                "No Text",
                "Please enter some text first."
            )

            return

        # Stop previous speech
        try:
            self.engine.stop()
        except Exception:
            pass

        self.current_text = text

        self.sentences = self.split_sentences(
            text
        )

        self.current_sentence_index = 0

        self.stop_requested = False
        self.is_paused = False

        thread = threading.Thread(
            target=self.speak_from_current_sentence,
            daemon=True
        )

        thread.start()

    # =========================================================
    # SPEAK SENTENCES
    # =========================================================

    def speak_from_current_sentence(self):

        try:

            self.is_speaking = True

            self.configure_engine()

            total = len(
                self.sentences
            )

            while (
                self.current_sentence_index < total
                and not self.stop_requested
                and not self.is_paused
            ):

                sentence = self.sentences[
                    self.current_sentence_index
                ]

                self.update_status(
                    f"Speaking sentence "
                    f"{self.current_sentence_index + 1}"
                    f" of {total}..."
                )

                self.engine.say(
                    sentence
                )

                self.engine.runAndWait()

                if self.stop_requested:
                    break

                if self.is_paused:
                    break

                self.current_sentence_index += 1

            if (
                self.current_sentence_index >= total
                and not self.stop_requested
            ):

                self.update_status(
                    "Finished"
                )

                self.is_speaking = False

        except Exception as error:

            self.is_speaking = False

            self.update_status(
                "Speech error"
            )

            self.show_error(
                "Speech Error",
                str(error)
            )

        finally:

            if self.stop_requested:

                self.is_speaking = False

    # =========================================================
    # CONFIGURE ENGINE
    # =========================================================

    def configure_engine(self):

        self.engine.setProperty(
            "rate",
            self.speed_var.get()
        )

        self.engine.setProperty(
            "volume",
            self.volume_var.get()
        )

        voice_index = self.voice_combo.current()

        if (
            voice_index >= 0
            and voice_index < len(self.voices)
        ):

            self.engine.setProperty(
                "voice",
                self.voices[
                    voice_index
                ].id
            )

    # =========================================================
    # PAUSE
    # =========================================================

    def pause_speech(self):

        if not self.is_speaking:

            self.update_status(
                "Nothing is currently speaking"
            )

            return

        try:

            self.is_paused = True

            self.engine.stop()

            self.is_speaking = False

            self.update_status(
                "Paused"
            )

        except Exception as error:

            self.show_error(
                "Pause Error",
                str(error)
            )

    # =========================================================
    # RESUME
    # =========================================================

    def resume_speech(self):

        if not self.is_paused:

            self.update_status(
                "Speech is not paused"
            )

            return

        if not self.sentences:

            self.update_status(
                "No speech available to resume"
            )

            return

        self.stop_requested = False
        self.is_paused = False

        thread = threading.Thread(
            target=self.speak_from_current_sentence,
            daemon=True
        )

        thread.start()

    # =========================================================
    # STOP
    # =========================================================

    def stop_speech(self):

        try:

            self.stop_requested = True

            self.is_paused = False

            self.is_speaking = False

            self.engine.stop()

            self.current_sentence_index = 0

            self.update_status(
                "Stopped"
            )

        except Exception as error:

            self.show_error(
                "Stop Error",
                str(error)
            )

    # =========================================================
    # SAVE AUDIO
    # =========================================================

    def save_audio(self):

        text = self.get_text()

        if not text:

            messagebox.showwarning(
                "No Text",
                "Please enter some text before saving."
            )

            return

        filename = filedialog.asksaveasfilename(
            title="Save Speech Audio",
            initialdir=self.output_folder,
            initialfile="speech.wav",
            defaultextension=".wav",
            filetypes=[
                (
                    "WAV Audio",
                    "*.wav"
                )
            ]
        )

        if not filename:

            return

        try:

            self.configure_engine()

            self.update_status(
                "Creating audio file..."
            )

            thread = threading.Thread(
                target=self.save_audio_thread,
                args=(
                    text,
                    filename
                ),
                daemon=True
            )

            thread.start()

        except Exception as error:

            self.show_error(
                "Save Error",
                str(error)
            )

    # =========================================================
    # SAVE AUDIO THREAD
    # =========================================================

    def save_audio_thread(
        self,
        text,
        filename
    ):

        try:

            self.engine.save_to_file(
                text,
                filename
            )

            self.engine.runAndWait()

            self.update_status(
                "Audio saved successfully"
            )

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Audio Saved",
                    "Audio saved successfully!\n\n"
                    + filename
                )
            )

        except Exception as error:

            self.update_status(
                "Unable to save audio"
            )

            self.show_error(
                "Save Error",
                str(error)
            )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear_text(self):

        if self.is_speaking:

            self.stop_speech()

        self.text_box.delete(
            "1.0",
            tk.END
        )

        self.current_text = ""

        self.sentences = []

        self.current_sentence_index = 0

        self.update_count()

        self.update_status(
            "Ready"
        )

    # =========================================================
    # COUNT
    # =========================================================

    def update_count(
        self,
        event=None
    ):

        text = self.get_text()

        characters = len(
            text
        )

        words = len(
            text.split()
        )

        self.count_var.set(
            f"{characters} characters | "
            f"{words} words"
        )

    # =========================================================
    # STATUS
    # =========================================================

    def update_status(
        self,
        message
    ):

        try:

            self.root.after(
                0,
                lambda: self.status_var.set(
                    message
                )
            )

        except tk.TclError:
            pass

    # =========================================================
    # SHOW ERROR
    # =========================================================

    def show_error(
        self,
        title,
        message
    ):

        try:

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    title,
                    message
                )
            )

        except tk.TclError:
            pass

    # =========================================================
    # OPEN OUTPUT FOLDER
    # =========================================================

    def open_output_folder(self):

        try:

            os.makedirs(
                self.output_folder,
                exist_ok=True
            )

            if sys.platform.startswith(
                "win"
            ):

                os.startfile(
                    self.output_folder
                )

            elif sys.platform == "darwin":

                subprocess.Popen(
                    [
                        "open",
                        self.output_folder
                    ]
                )

            else:

                subprocess.Popen(
                    [
                        "xdg-open",
                        self.output_folder
                    ]
                )

        except Exception as error:

            self.show_error(
                "Folder Error",
                str(error)
            )

    # =========================================================
    # CLOSE APP
    # =========================================================

    def close_app(self):

        try:

            self.stop_requested = True

            self.engine.stop()

        except Exception:
            pass

        self.root.destroy()


# =============================================================
# START APPLICATION
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = TextToSpeechApp(
        root
    )

    root.mainloop()