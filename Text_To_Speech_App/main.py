import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyttsx3
import threading
import os
import sys
import subprocess
import re
import time


class TextToSpeechApp:

    def __init__(self, root):

        # =====================================================
        # WINDOW
        # =====================================================

        self.root = root

        self.root.title(
            "VocalDesk - Text to Speech"
        )

        self.root.geometry(
            "1100x760"
        )

        self.root.minsize(
            900,
            680
        )

        self.root.configure(
            bg="#0f172a"
        )

        # =====================================================
        # COLORS
        # =====================================================

        self.BG = "#0f172a"
        self.SIDEBAR = "#111c33"
        self.CARD = "#17233a"
        self.CARD_2 = "#1d2a43"

        self.WHITE = "#f8fafc"
        self.TEXT = "#e2e8f0"
        self.MUTED = "#94a3b8"

        self.BLUE = "#3b82f6"
        self.BLUE_HOVER = "#2563eb"

        self.GREEN = "#22c55e"
        self.GREEN_HOVER = "#16a34a"

        self.ORANGE = "#f59e0b"
        self.ORANGE_HOVER = "#d97706"

        self.RED = "#ef4444"
        self.RED_HOVER = "#dc2626"

        self.PURPLE = "#8b5cf6"
        self.PURPLE_HOVER = "#7c3aed"

        self.BORDER = "#263650"

        # =====================================================
        # SPEECH STATE
        # =====================================================

        self.current_engine = None

        self.speech_thread = None

        self.engine_lock = threading.Lock()

        self.stop_requested = False
        self.pause_requested = False

        self.is_speaking = False
        self.is_paused = False

        self.current_text = ""

        self.sentences = []

        self.current_sentence_index = 0

        # =====================================================
        # VOICES
        # =====================================================

        self.voices = []

        # =====================================================
        # OUTPUT
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

        self.speed_text = tk.StringVar(
            value="170 WPM"
        )

        self.volume_text = tk.StringVar(
            value="100%"
        )

        self.status_var = tk.StringVar(
            value="Ready"
        )

        self.counter_var = tk.StringVar(
            value="0 characters  •  0 words"
        )

        self.progress_var = tk.DoubleVar(
            value=0
        )

        self.progress_text = tk.StringVar(
            value="Ready to speak"
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
        # LOAD SYSTEM VOICES
        # =====================================================

        self.load_voices()

        # =====================================================
        # CLOSE EVENT
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
            style.theme_use(
                "clam"
            )
        except tk.TclError:
            pass

        style.configure(
            "Modern.TCombobox",
            fieldbackground="#0f1a2d",
            background="#0f1a2d",
            foreground=self.TEXT,
            arrowcolor=self.MUTED,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER,
            padding=8
        )

        style.map(
            "Modern.TCombobox",
            fieldbackground=[
                ("readonly", "#0f1a2d")
            ],
            foreground=[
                ("readonly", self.TEXT)
            ]
        )

        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor="#0f1a2d",
            background=self.BLUE,
            bordercolor="#0f1a2d",
            lightcolor=self.BLUE,
            darkcolor=self.BLUE,
            thickness=7
        )

    # =========================================================
    # GUI
    # =========================================================

    def create_gui(self):

        # =====================================================
        # TOP BAR
        # =====================================================

        top = tk.Frame(
            self.root,
            bg=self.SIDEBAR,
            height=78
        )

        top.pack(
            fill="x"
        )

        top.pack_propagate(
            False
        )

        # Logo
        logo_frame = tk.Frame(
            top,
            bg=self.SIDEBAR
        )

        logo_frame.pack(
            side="left",
            padx=30
        )

        logo = tk.Label(
            logo_frame,
            text="V",
            font=(
                "Segoe UI",
                22,
                "bold"
            ),
            bg=self.BLUE,
            fg="white",
            width=2,
            height=1
        )

        logo.pack(
            side="left",
            padx=(0, 12)
        )

        title_frame = tk.Frame(
            logo_frame,
            bg=self.SIDEBAR
        )

        title_frame.pack(
            side="left"
        )

        tk.Label(
            title_frame,
            text="VocalDesk",
            font=(
                "Segoe UI",
                17,
                "bold"
            ),
            bg=self.SIDEBAR,
            fg=self.WHITE
        ).pack(
            anchor="w"
        )

        tk.Label(
            title_frame,
            text="TEXT TO SPEECH",
            font=(
                "Segoe UI",
                8,
                "bold"
            ),
            bg=self.SIDEBAR,
            fg=self.MUTED
        ).pack(
            anchor="w"
        )

        # Right side
        tk.Label(
            top,
            text="OFFLINE SPEECH ENGINE",
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            bg=self.SIDEBAR,
            fg=self.GREEN
        ).pack(
            side="right",
            padx=30
        )

        # =====================================================
        # MAIN
        # =====================================================

        main = tk.Frame(
            self.root,
            bg=self.BG
        )

        main.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        # =====================================================
        # PAGE TITLE
        # =====================================================

        tk.Label(
            main,
            text="Create spoken audio",
            font=(
                "Segoe UI",
                25,
                "bold"
            ),
            bg=self.BG,
            fg=self.WHITE
        ).pack(
            anchor="w"
        )

        tk.Label(
            main,
            text="Type your text, customize the voice, and listen instantly.",
            font=(
                "Segoe UI",
                10
            ),
            bg=self.BG,
            fg=self.MUTED
        ).pack(
            anchor="w",
            pady=(4, 18)
        )

        # =====================================================
        # EDITOR CARD
        # =====================================================

        editor = tk.Frame(
            main,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        editor.pack(
            fill="both",
            expand=True
        )

        # =====================================================
        # EDITOR HEADER
        # =====================================================

        editor_header = tk.Frame(
            editor,
            bg=self.CARD
        )

        editor_header.pack(
            fill="x",
            padx=22,
            pady=(18, 10)
        )

        tk.Label(
            editor_header,
            text="Your text",
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            bg=self.CARD,
            fg=self.WHITE
        ).pack(
            side="left"
        )

        tk.Label(
            editor_header,
            textvariable=self.counter_var,
            font=(
                "Segoe UI",
                9
            ),
            bg=self.CARD,
            fg=self.MUTED
        ).pack(
            side="right"
        )

        # =====================================================
        # TEXT AREA
        # =====================================================

        text_container = tk.Frame(
            editor,
            bg="#0d1729",
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        text_container.pack(
            fill="both",
            expand=True,
            padx=22
        )

        self.text_box = tk.Text(
            text_container,
            height=12,
            wrap="word",
            font=(
                "Segoe UI",
                12
            ),
            bg="#0d1729",
            fg="#e5edf8",
            insertbackground="#ffffff",
            selectbackground="#2563eb",
            selectforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=18,
            pady=15,
            undo=True
        )

        self.text_box.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = tk.Scrollbar(
            text_container,
            orient="vertical",
            command=self.text_box.yview,
            bg="#1e293b",
            troughcolor="#0d1729",
            activebackground="#3b82f6",
            width=12
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
            self.update_counter
        )

        # =====================================================
        # SETTINGS
        # =====================================================

        settings = tk.Frame(
            editor,
            bg=self.CARD
        )

        settings.pack(
            fill="x",
            padx=22,
            pady=16
        )

        # -----------------------------------------------------
        # VOICE
        # -----------------------------------------------------

        voice_box = tk.Frame(
            settings,
            bg=self.CARD
        )

        voice_box.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 20)
        )

        tk.Label(
            voice_box,
            text="VOICE",
            font=(
                "Segoe UI",
                8,
                "bold"
            ),
            bg=self.CARD,
            fg=self.MUTED
        ).pack(
            anchor="w"
        )

        self.voice_combo = ttk.Combobox(
            voice_box,
            textvariable=self.voice_var,
            state="readonly",
            style="Modern.TCombobox"
        )

        self.voice_combo.pack(
            fill="x",
            pady=(5, 0)
        )

        # -----------------------------------------------------
        # SPEED
        # -----------------------------------------------------

        speed_box = tk.Frame(
            settings,
            bg=self.CARD,
            width=230
        )

        speed_box.pack(
            side="left",
            padx=(0, 20)
        )

        speed_header = tk.Frame(
            speed_box,
            bg=self.CARD
        )

        speed_header.pack(
            fill="x"
        )

        tk.Label(
            speed_header,
            text="SPEED",
            font=(
                "Segoe UI",
                8,
                "bold"
            ),
            bg=self.CARD,
            fg=self.MUTED
        ).pack(
            side="left"
        )

        tk.Label(
            speed_header,
            textvariable=self.speed_text,
            font=(
                "Segoe UI",
                8,
                "bold"
            ),
            bg=self.CARD,
            fg=self.BLUE
        ).pack(
            side="right"
        )

        self.speed_scale = tk.Scale(
            speed_box,
            from_=50,
            to=300,
            orient="horizontal",
            variable=self.speed_var,
            showvalue=False,
            bg=self.CARD,
            fg=self.WHITE,
            troughcolor="#263650",
            activebackground=self.BLUE,
            highlightthickness=0,
            bd=0,
            width=8,
            length=210,
            command=self.speed_changed
        )

        self.speed_scale.pack()

        # -----------------------------------------------------
        # VOLUME
        # -----------------------------------------------------

        volume_box = tk.Frame(
            settings,
            bg=self.CARD,
            width=190
        )

        volume_box.pack(
            side="left"
        )

        volume_header = tk.Frame(
            volume_box,
            bg=self.CARD
        )

        volume_header.pack(
            fill="x"
        )

        tk.Label(
            volume_header,
            text="VOLUME",
            font=(
                "Segoe UI",
                8,
                "bold"
            ),
            bg=self.CARD,
            fg=self.MUTED
        ).pack(
            side="left"
        )

        tk.Label(
            volume_header,
            textvariable=self.volume_text,
            font=(
                "Segoe UI",
                8,
                "bold"
            ),
            bg=self.CARD,
            fg=self.GREEN
        ).pack(
            side="right"
        )

        self.volume_scale = tk.Scale(
            volume_box,
            from_=0,
            to=1,
            resolution=0.1,
            orient="horizontal",
            variable=self.volume_var,
            showvalue=False,
            bg=self.CARD,
            fg=self.WHITE,
            troughcolor="#263650",
            activebackground=self.GREEN,
            highlightthickness=0,
            bd=0,
            width=8,
            length=170,
            command=self.volume_changed
        )

        self.volume_scale.pack()

        # =====================================================
        # PROGRESS
        # =====================================================

        progress_frame = tk.Frame(
            editor,
            bg=self.CARD
        )

        progress_frame.pack(
            fill="x",
            padx=22
        )

        progress_header = tk.Frame(
            progress_frame,
            bg=self.CARD
        )

        progress_header.pack(
            fill="x"
        )

        tk.Label(
            progress_header,
            textvariable=self.progress_text,
            font=(
                "Segoe UI",
                9
            ),
            bg=self.CARD,
            fg=self.MUTED
        ).pack(
            side="left"
        )

        self.progress = ttk.Progressbar(
            progress_frame,
            style="Modern.Horizontal.TProgressbar",
            variable=self.progress_var,
            maximum=100
        )

        self.progress.pack(
            fill="x",
            pady=(6, 16)
        )

        # =====================================================
        # CONTROLS
        # =====================================================

        controls = tk.Frame(
            editor,
            bg=self.CARD
        )

        controls.pack(
            fill="x",
            padx=22,
            pady=(0, 20)
        )

        # Play
        self.play_button = self.make_button(
            controls,
            "▶  Play",
            self.play_text,
            self.BLUE,
            self.BLUE_HOVER,
            width=12
        )

        self.play_button.pack(
            side="left",
            padx=(0, 8)
        )

        # PAUSE / RESUME - ONE BUTTON
        self.pause_resume_button = self.make_button(
            controls,
            "Ⅱ  Pause",
            self.pause_or_resume,
            self.ORANGE,
            self.ORANGE_HOVER,
            width=13
        )

        self.pause_resume_button.pack(
            side="left",
            padx=8
        )

        # STOP
        self.stop_button = self.make_button(
            controls,
            "■  Stop",
            self.stop_speech,
            self.RED,
            self.RED_HOVER,
            width=11
        )

        self.stop_button.pack(
            side="left",
            padx=8
        )

        # SAVE
        self.save_button = self.make_button(
            controls,
            "↓  Save Audio",
            self.save_audio,
            self.PURPLE,
            self.PURPLE_HOVER,
            width=15
        )

        self.save_button.pack(
            side="left",
            padx=8
        )

        # CLEAR
        self.make_button(
            controls,
            "Clear",
            self.clear_text,
            "#334155",
            "#475569",
            width=9
        ).pack(
            side="left",
            padx=8
        )

        # OUTPUT
        self.make_button(
            controls,
            "Output Folder",
            self.open_output_folder,
            "#334155",
            "#475569",
            width=14
        ).pack(
            side="right"
        )

        # =====================================================
        # BOTTOM STATUS
        # =====================================================

        bottom = tk.Frame(
            self.root,
            bg=self.BG
        )

        bottom.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        status_left = tk.Frame(
            bottom,
            bg=self.BG
        )

        status_left.pack(
            side="left"
        )

        status_dot = tk.Label(
            status_left,
            text="●",
            font=("Segoe UI", 9),
            bg=self.BG,
            fg=self.GREEN
        )

        status_dot.pack(
            side="left",
            padx=(0, 6)
        )

        tk.Label(
            status_left,
            textvariable=self.status_var,
            font=(
                "Segoe UI",
                9
            ),
            bg=self.BG,
            fg=self.MUTED
        ).pack(
            side="left"
        )

        tk.Label(
            bottom,
            text="Python  •  Tkinter  •  pyttsx3",
            font=(
                "Segoe UI",
                9
            ),
            bg=self.BG,
            fg="#64748b"
        ).pack(
            side="right"
        )

    # =========================================================
    # BUTTON CREATOR
    # =========================================================

    def make_button(
        self,
        parent,
        text,
        command,
        color,
        hover,
        width=12
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            font=(
                "Segoe UI",
                9,
                "bold"
            ),
            bg=color,
            fg="white",
            activebackground=hover,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=8,
            pady=9,
            cursor="hand2"
        )

        button.bind(
            "<Enter>",
            lambda event: button.configure(
                bg=hover
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

            temp_engine = pyttsx3.init()

            self.voices = (
                temp_engine.getProperty(
                    "voices"
                )
            )

            try:
                temp_engine.stop()
            except Exception:
                pass

            names = []

            for index, voice in enumerate(
                self.voices
            ):

                name = getattr(
                    voice,
                    "name",
                    None
                )

                if not name:
                    name = (
                        f"Voice {index + 1}"
                    )

                names.append(
                    name
                )

            self.voice_combo["values"] = names

            if names:

                self.voice_combo.current(
                    0
                )

                self.update_status(
                    f"{len(names)} system voice(s) available"
                )

            else:

                self.update_status(
                    "No system voices found"
                )

        except Exception as error:

            messagebox.showerror(
                "Voice Error",
                "Could not load system voices.\n\n"
                + str(error)
            )

    # =========================================================
    # SPEED
    # =========================================================

    def speed_changed(
        self,
        value
    ):

        speed = int(
            float(value)
        )

        self.speed_text.set(
            f"{speed} WPM"
        )

    # =========================================================
    # VOLUME
    # =========================================================

    def volume_changed(
        self,
        value
    ):

        volume = float(
            value
        )

        self.volume_text.set(
            f"{int(volume * 100)}%"
        )

    # =========================================================
    # COUNTER
    # =========================================================

    def update_counter(
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

        self.counter_var.set(
            f"{characters} characters  •  "
            f"{words} words"
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
    # SPLIT TEXT INTO SENTENCES
    # =========================================================

    def split_sentences(
        self,
        text
    ):

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        if not sentences and text:
            sentences = [text]

        return sentences

    # =========================================================
    # CREATE NEW ENGINE
    # =========================================================

    def create_engine(self):

        engine = pyttsx3.init()

        # Speed
        engine.setProperty(
            "rate",
            self.speed_var.get()
        )

        # Volume
        engine.setProperty(
            "volume",
            self.volume_var.get()
        )

        # Voice
        voice_index = (
            self.voice_combo.current()
        )

        if (
            voice_index >= 0
            and voice_index < len(self.voices)
        ):

            try:

                engine.setProperty(
                    "voice",
                    self.voices[
                        voice_index
                    ].id
                )

            except Exception:
                pass

        return engine

    # =========================================================
    # PLAY FROM BEGINNING
    # =========================================================

    def play_text(self):

        text = self.get_text()

        if not text:

            messagebox.showwarning(
                "No Text",
                "Please enter some text first."
            )

            return

        # Stop anything currently running
        self.stop_requested = True
        self.pause_requested = False

        if self.current_engine:

            try:
                self.current_engine.stop()
            except Exception:
                pass

        # New text
        self.current_text = text

        self.sentences = (
            self.split_sentences(
                text
            )
        )

        self.current_sentence_index = 0

        self.stop_requested = False
        self.pause_requested = False
        self.is_paused = False

        self.progress_var.set(
            0
        )

        self.progress_text.set(
            "Preparing speech..."
        )

        self.update_toggle_button(
            "pause"
        )

        self.start_worker()

    # =========================================================
    # START SPEECH WORKER
    # =========================================================

    def start_worker(self):

        if (
            self.speech_thread
            and self.speech_thread.is_alive()
        ):

            return

        self.speech_thread = threading.Thread(
            target=self.speak_worker,
            daemon=True
        )

        self.speech_thread.start()

    # =========================================================
    # SPEECH WORKER
    # =========================================================

    def speak_worker(self):

        self.is_speaking = True

        try:

            while (
                self.current_sentence_index
                < len(self.sentences)
            ):

                # Stop
                if self.stop_requested:
                    break

                # Pause
                if self.pause_requested:
                    break

                index = (
                    self.current_sentence_index
                )

                sentence = (
                    self.sentences[index]
                )

                total = len(
                    self.sentences
                )

                percentage = (
                    index / total
                ) * 100

                self.update_progress(
                    percentage,
                    f"Speaking "
                    f"{index + 1} of "
                    f"{total}"
                )

                # -------------------------------------------------
                # NEW ENGINE FOR EACH SENTENCE
                # -------------------------------------------------

                with self.engine_lock:

                    if self.stop_requested:
                        break

                    if self.pause_requested:
                        break

                    engine = self.create_engine()

                    self.current_engine = (
                        engine
                    )

                    try:

                        engine.say(
                            sentence
                        )

                        engine.runAndWait()

                    finally:

                        try:
                            engine.stop()
                        except Exception:
                            pass

                        self.current_engine = None

                # -------------------------------------------------
                # IMPORTANT
                #
                # If pause happened, DON'T move to next sentence.
                # Resume will repeat this interrupted sentence.
                # -------------------------------------------------

                if self.pause_requested:

                    break

                if self.stop_requested:

                    break

                # Sentence completed
                self.current_sentence_index += 1

            # =====================================================
            # FINAL STATE
            # =====================================================

            if self.stop_requested:

                self.update_status(
                    "Stopped"
                )

                self.progress_text.set(
                    "Playback stopped"
                )

                self.update_toggle_button(
                    "pause"
                )

            elif self.pause_requested:

                self.is_paused = True

                self.update_status(
                    "Paused"
                )

                self.progress_text.set(
                    "Paused — press Resume to continue"
                )

                self.update_toggle_button(
                    "resume"
                )

            elif (
                self.current_sentence_index
                >= len(self.sentences)
            ):

                self.update_progress(
                    100,
                    "Finished"
                )

                self.update_status(
                    "Finished"
                )

                self.progress_text.set(
                    "Speech completed"
                )

                self.update_toggle_button(
                    "pause"
                )

        except Exception as error:

            self.update_status(
                "Speech error"
            )

            self.update_toggle_button(
                "pause"
            )

            self.show_error(
                "Speech Error",
                str(error)
            )

        finally:

            self.is_speaking = False

    # =========================================================
    # ONE PAUSE / RESUME BUTTON
    # =========================================================

    def pause_or_resume(self):

        # -----------------------------------------------------
        # CURRENTLY SPEAKING
        # -----------------------------------------------------

        if self.is_speaking:

            self.pause_requested = True

            self.update_status(
                "Pausing..."
            )

            self.progress_text.set(
                "Pausing speech..."
            )

            # Interrupt current engine
            if self.current_engine:

                try:

                    self.current_engine.stop()

                except Exception:
                    pass

            # Wait until worker is finished
            self.wait_until_paused()

            return

        # -----------------------------------------------------
        # CURRENTLY PAUSED
        # -----------------------------------------------------

        if self.is_paused:

            self.resume_speech()

            return

        # -----------------------------------------------------
        # NOTHING PLAYING
        # -----------------------------------------------------

        text = self.get_text()

        if not text:

            messagebox.showwarning(
                "No Text",
                "Please enter some text first."
            )

            return

        self.play_text()

    # =========================================================
    # WAIT UNTIL PAUSED
    # =========================================================

    def wait_until_paused(self):

        if (
            self.speech_thread
            and self.speech_thread.is_alive()
        ):

            self.root.after(
                50,
                self.wait_until_paused
            )

            return

        self.is_speaking = False
        self.is_paused = True

        self.update_status(
            "Paused"
        )

        self.progress_text.set(
            "Paused — press Resume to continue"
        )

        self.update_toggle_button(
            "resume"
        )

    # =========================================================
    # RESUME
    # =========================================================

    def resume_speech(self):

        if not self.sentences:

            text = self.get_text()

            if not text:
                return

            self.current_text = text

            self.sentences = (
                self.split_sentences(
                    text
                )
            )

            self.current_sentence_index = 0

        # Make sure old thread is completely finished
        if (
            self.speech_thread
            and self.speech_thread.is_alive()
        ):

            self.root.after(
                100,
                self.resume_speech
            )

            return

        self.pause_requested = False
        self.stop_requested = False
        self.is_paused = False
        self.is_speaking = False

        self.update_status(
            "Resuming..."
        )

        self.progress_text.set(
            "Resuming speech..."
        )

        self.update_toggle_button(
            "pause"
        )

        self.start_worker()

    # =========================================================
    # STOP
    # =========================================================

    def stop_speech(self):

        self.stop_requested = True
        self.pause_requested = False
        self.is_paused = False

        if self.current_engine:

            try:

                self.current_engine.stop()

            except Exception:
                pass

        self.current_sentence_index = 0

        self.is_speaking = False

        self.progress_var.set(
            0
        )

        self.progress_text.set(
            "Playback stopped"
        )

        self.update_status(
            "Stopped"
        )

        self.update_toggle_button(
            "pause"
        )

    # =========================================================
    # TOGGLE BUTTON
    # =========================================================

    def update_toggle_button(
        self,
        mode
    ):

        def update():

            if mode == "resume":

                self.pause_resume_button.config(
                    text="▶  Resume",
                    bg=self.GREEN
                )

            else:

                self.pause_resume_button.config(
                    text="Ⅱ  Pause",
                    bg=self.ORANGE
                )

        try:

            self.root.after(
                0,
                update
            )

        except tk.TclError:
            pass

    # =========================================================
    # PROGRESS
    # =========================================================

    def update_progress(
        self,
        value,
        text
    ):

        def update():

            self.progress_var.set(
                value
            )

            self.progress_text.set(
                text
            )

        try:

            self.root.after(
                0,
                update
            )

        except tk.TclError:
            pass

    # =========================================================
    # SAVE AUDIO
    # =========================================================

    def save_audio(self):

        text = self.get_text()

        if not text:

            messagebox.showwarning(
                "No Text",
                "Please enter text before saving."
            )

            return

        # Don't save while playing
        if (
            self.is_speaking
            or (
                self.speech_thread
                and self.speech_thread.is_alive()
            )
        ):

            messagebox.showwarning(
                "Speech In Progress",
                "Please stop or finish the current speech "
                "before saving audio."
            )

            return

        filename = filedialog.asksaveasfilename(
            title="Save Audio",
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

        thread = threading.Thread(
            target=self.save_audio_worker,
            args=(
                text,
                filename
            ),
            daemon=True
        )

        thread.start()

    # =========================================================
    # SAVE AUDIO WORKER
    # =========================================================

    def save_audio_worker(
        self,
        text,
        filename
    ):

        try:

            self.update_status(
                "Creating audio..."
            )

            engine = self.create_engine()

            engine.save_to_file(
                text,
                filename
            )

            engine.runAndWait()

            try:
                engine.stop()
            except Exception:
                pass

            self.update_status(
                "Audio saved successfully"
            )

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Audio Saved",
                    "Your audio file was saved successfully.\n\n"
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

        self.stop_speech()

        self.text_box.delete(
            "1.0",
            tk.END
        )

        self.current_text = ""

        self.sentences = []

        self.current_sentence_index = 0

        self.counter_var.set(
            "0 characters  •  0 words"
        )

        self.progress_var.set(
            0
        )

        self.progress_text.set(
            "Ready to speak"
        )

        self.update_status(
            "Ready"
        )

    # =========================================================
    # OUTPUT FOLDER
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
    # ERROR
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
    # CLOSE
    # =========================================================

    def close_app(self):

        self.stop_requested = True
        self.pause_requested = False

        if self.current_engine:

            try:

                self.current_engine.stop()

            except Exception:
                pass

        self.root.destroy()


# =============================================================
# APPLICATION START
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = TextToSpeechApp(
        root
    )

    root.mainloop()
