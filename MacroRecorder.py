#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recorder-PRO  (todo en un solo archivo)
Graba y reproduce acciones de raton y teclado. Interfaz morada, ES/EN.

REQUISITOS:
    pip install pynput
USO:
    python MacroRecorder.py
"""

import json
import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

try:
    import ctypes
    HAS_CTYPES = True
except Exception:
    HAS_CTYPES = False

from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController

HOTKEY_STOP = Key.esc
MOVE_THROTTLE = 0.015
SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".recorder_pro.json")

# ---------- Paleta (morado) ----------
BG      = "#1c0f33"
CARD    = "#2a1a4a"
HEADER  = "#140a26"
ACCENT  = "#a855f7"
RED     = "#e11d8f"
RED_D   = "#c01679"
GREEN   = "#8b5cf6"
GREEN_D = "#7c3aed"
TEXT    = "#f2e9ff"
MUTED   = "#b9a6d9"
FIELD   = "#ffffff"
FIELD_T = "#1a1030"
GOLD    = "#f0b6ff"
CARD_BD = "#3d2a63"
CHIP_BG = "#1b0f33"
BTN_BG  = "#3d2a63"

# ---------- Traducciones ----------
TEXTS = {
    "es": {
        "subtitle": "Graba y reproduce raton y teclado",
        "menu_file": "Archivo", "menu_save": "Guardar macro...", "menu_load": "Cargar macro...",
        "menu_clear": "Limpiar", "menu_exit": "Salir", "menu_macro": "Macro",
        "menu_rec": "Iniciar / Detener grabacion", "menu_play": "Reproducir / Detener",
        "menu_stop": "Detener reproduccion (Esc)", "menu_help": "Ayuda",
        "menu_howto": "Como se usa", "menu_about": "Acerca de",
        "ready": "Listo", "recording": "\u25cf GRABANDO", "playing": "\u25b6 REPRODUCIENDO",
        "scheduled": "\u23f0 PROGRAMADO", "press_key": "Pulsa una tecla...",
        "counter": "Acciones grabadas: {n}",
        "btn_record": "\u25cf  Grabar", "btn_stop": "\u25a0  Parar", "btn_play": "\u25b6  Reproducir",
        "one_pass": "Una pasada: {a}   |   Total x{r}: {b}",
        "one_pass_inf": "Una pasada: {a}   |   Repeticiones: infinito",
        "count_fin": "Repeticion {c}/{t}   |   Quedan: {r}",
        "count_inf": "Repeticion {c}   |   Transcurrido: {e}  (infinito)",
        "starting": "Empezando...", "starts_in": "\u23f0 Empieza en: {r}",
        "card_keys": "TECLAS", "lbl_rec": "Grabar:", "lbl_play": "Reproducir:", "btn_change": "Cambiar",
        "card_opts": "OPCIONES", "lbl_repeats": "Repeticiones (0 = infinito):",
        "lbl_speed": "Velocidad (1 = normal):", "lbl_delay": "Espera al pulsar Reproducir (seg):",
        "chk_kbd": "Grabar teclado", "chk_mouse": "Grabar movimientos de raton",
        "chk_sound": "Alerta de sonido",
        "chk_awake": "Mantener el equipo despierto (evita bloqueo por inactividad)",
        "card_sched": "PROGRAMAR INICIO AUTOMATICO", "lbl_start_in": "Empezar dentro de:",
        "btn_schedule": "Programar", "btn_cancel": "Cancelar",
        "btn_save": "Guardar", "btn_load": "Cargar", "btn_clear": "Limpiar",
        "btn_delete": "\U0001f5d1 Borrar grabacion",
        "footer": "Esc = detener la reproduccion",
        "howto_body": ("1. Elige tu tecla para GRABAR y tu tecla para REPRODUCIR.\n"
                       "2. Pulsa la tecla de grabar, haz tus acciones, pulsala otra vez para parar.\n"
                       "3. Pon las repeticiones y pulsa la tecla de reproducir.\n\n"
                       "ESPERA AL PULSAR REPRODUCIR (segundos):\n"
                       "   Espera corta para colocarte en la ventana correcta antes de empezar.\n\n"
                       "PROGRAMAR INICIO AUTOMATICO (horas/minutos):\n"
                       "   Para irte y que arranque solo mas tarde.\n\n"
                       "   Esc = detener la reproduccion."),
        "about_body": ("Recorder-PRO\nGraba y reproduce raton y teclado.\nTodo en un solo archivo."),
        "nothing_rec": "No hay nada grabado todavia.",
        "nothing_save": "No hay nada que guardar.",
        "saved": "Guardado ({n} acciones).", "loaded": "Cargado ({n} acciones).",
        "err_save": "Error al guardar: {e}", "err_load": "Error al cargar: {e}",
        "sched_no_rec": "No hay nada grabado para programar.",
        "sched_bad_num": "Horas y minutos deben ser numeros enteros.",
        "sched_zero": "Pon un tiempo mayor que cero (horas y/o minutos).",
        "sched_ok": ("Programado. La reproduccion empezara dentro de {t}.\n"
                     "Deja el programa abierto y no apagues el ordenador."),
    },
    "en": {
        "subtitle": "Record and replay mouse and keyboard",
        "menu_file": "File", "menu_save": "Save macro...", "menu_load": "Load macro...",
        "menu_clear": "Clear", "menu_exit": "Exit", "menu_macro": "Macro",
        "menu_rec": "Start / Stop recording", "menu_play": "Play / Stop",
        "menu_stop": "Stop playback (Esc)", "menu_help": "Help",
        "menu_howto": "How to use", "menu_about": "About",
        "ready": "Ready", "recording": "\u25cf RECORDING", "playing": "\u25b6 PLAYING",
        "scheduled": "\u23f0 SCHEDULED", "press_key": "Press a key...",
        "counter": "Recorded actions: {n}",
        "btn_record": "\u25cf  Record", "btn_stop": "\u25a0  Stop", "btn_play": "\u25b6  Play",
        "one_pass": "One pass: {a}   |   Total x{r}: {b}",
        "one_pass_inf": "One pass: {a}   |   Repeats: infinite",
        "count_fin": "Repeat {c}/{t}   |   Remaining: {r}",
        "count_inf": "Repeat {c}   |   Elapsed: {e}  (infinite)",
        "starting": "Starting...", "starts_in": "\u23f0 Starts in: {r}",
        "card_keys": "KEYS", "lbl_rec": "Record:", "lbl_play": "Play:", "btn_change": "Change",
        "card_opts": "OPTIONS", "lbl_repeats": "Repeats (0 = infinite):",
        "lbl_speed": "Speed (1 = normal):", "lbl_delay": "Delay when pressing Play (sec):",
        "chk_kbd": "Record keyboard", "chk_mouse": "Record mouse movements",
        "chk_sound": "Sound alert",
        "chk_awake": "Keep the computer awake (prevents idle lock)",
        "card_sched": "SCHEDULE AUTO START", "lbl_start_in": "Start in:",
        "btn_schedule": "Schedule", "btn_cancel": "Cancel",
        "btn_save": "Save", "btn_load": "Load", "btn_clear": "Clear",
        "btn_delete": "\U0001f5d1 Delete recording",
        "footer": "Esc = stop playback",
        "howto_body": ("1. Choose your RECORD key and your PLAY key.\n"
                       "2. Press the record key, do your actions, press it again to stop.\n"
                       "3. Set the repeats and press the play key.\n\n"
                       "DELAY WHEN PRESSING PLAY (seconds):\n"
                       "   Short wait so you can click the right window before it starts.\n\n"
                       "SCHEDULE AUTO START (hours/minutes):\n"
                       "   Leave and let it start by itself later.\n\n"
                       "   Esc = stop playback."),
        "about_body": ("Recorder-PRO\nRecord and replay mouse and keyboard.\nAll in a single file."),
        "nothing_rec": "Nothing recorded yet.",
        "nothing_save": "Nothing to save.",
        "saved": "Saved ({n} actions).", "loaded": "Loaded ({n} actions).",
        "err_save": "Error saving: {e}", "err_load": "Error loading: {e}",
        "sched_no_rec": "Nothing recorded to schedule.",
        "sched_bad_num": "Hours and minutes must be whole numbers.",
        "sched_zero": "Set a time greater than zero (hours and/or minutes).",
        "sched_ok": ("Scheduled. Playback will start in {t}.\n"
                     "Leave the program open and don't turn off the computer."),
    },
}


def serialize_key(key):
    if isinstance(key, KeyCode):
        if key.char is not None:
            return {"kc": "char", "v": key.char}
        return {"kc": "vk", "v": key.vk}
    if isinstance(key, Key):
        return {"kc": "special", "v": key.name}
    return {"kc": "char", "v": str(key)}


def deserialize_key(d):
    if d["kc"] == "char":
        return KeyCode.from_char(d["v"])
    if d["kc"] == "vk":
        return KeyCode.from_vk(d["v"])
    return getattr(Key, d["v"])


def key_sig(key):
    """Firma normalizada de una tecla. Unifica las dos formas (char / vk)
    en que Windows puede mandar una misma letra, para que siempre coincida."""
    if key is None:
        return None
    if isinstance(key, Key):
        return ("k", key.name)
    ch = getattr(key, "char", None)
    vk = getattr(key, "vk", None)
    if ch:
        return ("c", ch.lower())
    if vk is not None:
        if 65 <= vk <= 90:            # A-Z
            return ("c", chr(vk).lower())
        if 48 <= vk <= 57:            # 0-9
            return ("c", chr(vk))
        if 96 <= vk <= 105:           # teclado numerico 0-9
            return ("c", chr(vk - 48))
        return ("v", vk)
    return ("r", repr(key))


def keys_match(a, b):
    sa = key_sig(a)
    return sa is not None and sa == key_sig(b)


def key_label(key):
    if isinstance(key, KeyCode):
        if key.char is not None:
            return key.char.upper()
        return f"tecla({key.vk})"
    if isinstance(key, Key):
        return key.name.upper()
    return str(key)


def fmt_hms(secs):
    secs = int(round(max(0, secs)))
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    parts = []
    if h:
        parts.append(f"{h}h")
    if m or h:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


class MacroRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Recorder-PRO")
        self.root.geometry("470x620")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.lang = "es"

        # Estado
        self.events = []
        self.recording = False
        self.playing = False
        self.last_event_time = None
        self.last_move_time = 0.0
        self.play_thread = None
        self.stop_flag = threading.Event()

        self.key_record = Key.f9
        self.key_play = Key.f10

        self._req_record = False
        self._req_play = False
        self._capturing = None
        self._rec_moves = True
        self._rec_kbd = True
        self._keep_awake = False

        self._play_started_at = None
        self._play_total_est = 0.0
        self._current_loop = 0
        self._total_loops = 0
        self._scheduled_at = None

        self.mouse_ctrl = MouseController()
        self.kbd_ctrl = KeyboardController()

        # Variables persistentes (se conservan al cambiar de idioma)
        self.repeat_var = tk.StringVar(value="1")
        self.speed_var = tk.StringVar(value="1.0")
        self.delay_var = tk.StringVar(value="0")
        self.sched_h_var = tk.StringVar(value="0")
        self.sched_m_var = tk.StringVar(value="0")
        self.kbd_var = tk.BooleanVar(value=True)
        self.moves_var = tk.BooleanVar(value=True)
        self.sound_var = tk.BooleanVar(value=HAS_SOUND)
        self.awake_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="")
        self.counter_var = tk.StringVar(value="")
        self.time_var = tk.StringVar(value="")
        self.sched_var = tk.StringVar(value="")
        self.dbg_var = tk.StringVar(value="diagnostico: pulsa una tecla")
        self._dbg = "diagnostico: pulsa una tecla"

        self._load_settings()

        self.body = None
        self._build_menu()
        self._build_scaffold()
        self._build_ui()

        self.mouse_listener = mouse.Listener(
            on_move=self._on_move, on_click=self._on_click, on_scroll=self._on_scroll)
        self.kbd_listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release)
        self.mouse_listener.start()
        self.kbd_listener.start()

        self._awake_thread = threading.Thread(target=self._awake_worker, daemon=True)
        self._awake_thread.start()

        self._refresh_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def t(self, key, **kw):
        s = TEXTS[self.lang].get(key, key)
        return s.format(**kw) if kw else s

    def set_lang(self, lang):
        if lang == self.lang:
            return
        self.lang = lang
        self._save_settings()
        self._build_menu()
        for w in self.body.winfo_children():
            w.destroy()
        self._build_ui()

    # ---------- Andamiaje con scroll ----------
    def _build_scaffold(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg=BG)
        self._body_win = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        def _on_body_config(e):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.body.bind("<Configure>", _on_body_config)

        def _on_canvas_config(e):
            self.canvas.itemconfig(self._body_win, width=e.width)
        self.canvas.bind("<Configure>", _on_canvas_config)

        def _on_wheel(e):
            self.canvas.yview_scroll(int(-e.delta / 120), "units")
        self.canvas.bind_all("<MouseWheel>", _on_wheel)

    # ---------- Menu ----------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label=self.t("menu_save"), command=self.save_macro)
        m_file.add_command(label=self.t("menu_load"), command=self.load_macro)
        m_file.add_command(label=self.t("menu_clear"), command=self.clear_macro)
        m_file.add_separator()
        m_file.add_command(label=self.t("menu_exit"), command=self._on_close)
        menubar.add_cascade(label=self.t("menu_file"), menu=m_file)

        m_macro = tk.Menu(menubar, tearoff=0)
        m_macro.add_command(label=self.t("menu_rec"), command=self.toggle_record)
        m_macro.add_command(label=self.t("menu_play"), command=self.toggle_play)
        m_macro.add_command(label=self.t("menu_stop"), command=lambda: self.stop_flag.set())
        menubar.add_cascade(label=self.t("menu_macro"), menu=m_macro)

        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label=self.t("menu_howto"), command=self._show_help)
        m_help.add_command(label=self.t("menu_about"), command=self._show_about)
        menubar.add_cascade(label=self.t("menu_help"), menu=m_help)
        self.root.config(menu=menubar)

    def _show_help(self):
        messagebox.showinfo(self.t("menu_howto"), self.t("howto_body"))

    def _show_about(self):
        messagebox.showinfo(self.t("menu_about"), self.t("about_body"))

    # ---------- Logo robot ----------
    @staticmethod
    def _round_rect(cv, x1, y1, x2, y2, r, **kw):
        pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2,
               x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return cv.create_polygon(pts, smooth=True, **kw)

    def _draw_robot(self, cv):
        cv.create_line(23, 10, 23, 16, fill="#e9d5ff", width=3, capstyle="round")
        cv.create_oval(19, 3, 27, 11, fill="#ff4d6d", outline="")
        self._round_rect(cv, 8, 15, 38, 39, 9, fill="#f3ecff", outline=ACCENT)
        cv.create_oval(14, 22, 21, 30, fill="#7c3aed", outline="")
        cv.create_oval(25, 22, 32, 30, fill="#7c3aed", outline="")
        cv.create_oval(15, 23, 18, 26, fill="#ffffff", outline="")
        cv.create_oval(26, 23, 29, 26, fill="#ffffff", outline="")
        self._round_rect(cv, 17, 33, 29, 36, 1.5, fill="#c4b5fd", outline="")
        cv.create_oval(4, 24, 9, 30, fill="#e9d5ff", outline="")
        cv.create_oval(37, 24, 42, 30, fill="#e9d5ff", outline="")

    # ---------- Componentes ----------
    def _card(self, parent, title):
        wrap = tk.Frame(parent, bg=CARD, highlightbackground=CARD_BD, highlightthickness=1, bd=0)
        wrap.pack(fill="x", padx=16, pady=7)
        tk.Label(wrap, text=title, bg=CARD, fg=ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        inner = tk.Frame(wrap, bg=CARD)
        inner.pack(fill="x", padx=12, pady=(0, 10))
        return inner

    def _field(self, parent, var, width=8):
        e = tk.Entry(parent, width=width, justify="center", bg=FIELD, fg=FIELD_T,
                     insertbackground=FIELD_T, relief="flat", font=("Segoe UI", 11, "bold"),
                     highlightbackground="#c9d2e0", highlightthickness=1, textvariable=var)
        return e

    def _row_label(self, parent, text):
        return tk.Label(parent, text=text, bg=CARD, fg=TEXT, font=("Segoe UI", 10))

    # ---------- Interfaz ----------
    def _build_ui(self):
        # Cabecera
        header = tk.Frame(self.body, bg=HEADER)
        header.pack(fill="x")
        hrow = tk.Frame(header, bg=HEADER)
        hrow.pack(fill="x", padx=16, pady=12)

        logo = tk.Canvas(hrow, width=46, height=46, bg=HEADER, highlightthickness=0)
        logo.pack(side="left")
        self._draw_robot(logo)

        titles = tk.Frame(hrow, bg=HEADER)
        titles.pack(side="left", padx=12)
        tk.Label(titles, text="Recorder-PRO  v2.1", bg=HEADER, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(titles, text=self.t("subtitle"), bg=HEADER, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w")

        # Selector de idioma (arriba a la derecha)
        langf = tk.Frame(hrow, bg=HEADER)
        langf.pack(side="right")
        for code in ("es", "en"):
            active = (self.lang == code)
            tk.Button(langf, text=code.upper(), width=3,
                      command=lambda c=code: self.set_lang(c),
                      bg=ACCENT if active else BTN_BG, fg="white",
                      activebackground=ACCENT, relief="flat", bd=0, cursor="hand2",
                      font=("Segoe UI", 9, "bold"), padx=6, pady=4).pack(side="left", padx=2)

        # Estado
        self.status_lbl = tk.Label(self.body, textvariable=self.status_var, bg=BG, fg=TEXT,
                                   font=("Segoe UI", 15, "bold"))
        self.status_lbl.pack(pady=(12, 2))
        tk.Label(self.body, textvariable=self.counter_var, bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack()
        tk.Label(self.body, textvariable=self.time_var, bg=BG, fg=GOLD,
                 font=("Segoe UI", 11, "bold")).pack(pady=(3, 8))

        # Botones principales
        btns = tk.Frame(self.body, bg=BG)
        btns.pack(pady=2)
        self.btn_record = tk.Button(btns, text=self.t("btn_record"), width=15, command=self.toggle_record,
                                    bg=RED, fg="white", activebackground=RED_D, activeforeground="white",
                                    relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"),
                                    padx=6, pady=8)
        self.btn_record.grid(row=0, column=0, padx=5)
        self.btn_play = tk.Button(btns, text=self.t("btn_play"), width=15, command=self.toggle_play,
                                  bg=GREEN, fg="white", activebackground=GREEN_D, activeforeground="white",
                                  relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"),
                                  padx=6, pady=8)
        self.btn_play.grid(row=0, column=1, padx=5)

        # Boton borrar grabacion
        self.btn_delete = tk.Button(self.body, text=self.t("btn_delete"), command=self.clear_macro,
                                    bg=BTN_BG, fg="white", activebackground=RED, activeforeground="white",
                                    relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 9, "bold"),
                                    padx=6, pady=5)
        self.btn_delete.pack(pady=(8, 2))

        # Tarjeta Teclas
        k = self._card(self.body, self.t("card_keys"))
        r0 = tk.Frame(k, bg=CARD); r0.pack(fill="x", pady=3)
        self._row_label(r0, self.t("lbl_rec")).pack(side="left")
        self.lbl_key_record = tk.Label(r0, text=key_label(self.key_record), width=8, bg=CHIP_BG,
                                       fg=GOLD, font=("Segoe UI", 10, "bold"), padx=6, pady=3)
        self.lbl_key_record.pack(side="left", padx=8)
        tk.Button(r0, text=self.t("btn_change"), command=lambda: self.capture_key("record"),
                  bg=BTN_BG, fg="white", activebackground=ACCENT, relief="flat", bd=0,
                  cursor="hand2", font=("Segoe UI", 9), padx=10, pady=3).pack(side="left")

        r1 = tk.Frame(k, bg=CARD); r1.pack(fill="x", pady=3)
        self._row_label(r1, self.t("lbl_play")).pack(side="left")
        self.lbl_key_play = tk.Label(r1, text=key_label(self.key_play), width=8, bg=CHIP_BG,
                                     fg=GOLD, font=("Segoe UI", 10, "bold"), padx=6, pady=3)
        self.lbl_key_play.pack(side="left", padx=8)
        tk.Button(r1, text=self.t("btn_change"), command=lambda: self.capture_key("play"),
                  bg=BTN_BG, fg="white", activebackground=ACCENT, relief="flat", bd=0,
                  cursor="hand2", font=("Segoe UI", 9), padx=10, pady=3).pack(side="left")

        # Tarjeta Opciones
        o = self._card(self.body, self.t("card_opts"))
        rr = tk.Frame(o, bg=CARD); rr.pack(fill="x", pady=3)
        self._row_label(rr, self.t("lbl_repeats")).pack(side="left")
        self._field(rr, self.repeat_var).pack(side="right")
        rs = tk.Frame(o, bg=CARD); rs.pack(fill="x", pady=3)
        self._row_label(rs, self.t("lbl_speed")).pack(side="left")
        self._field(rs, self.speed_var).pack(side="right")
        rd = tk.Frame(o, bg=CARD); rd.pack(fill="x", pady=3)
        self._row_label(rd, self.t("lbl_delay")).pack(side="left")
        self._field(rd, self.delay_var).pack(side="right")

        tk.Checkbutton(o, text=self.t("chk_kbd"), variable=self.kbd_var, bg=CARD, fg=TEXT,
                       activebackground=CARD, activeforeground=TEXT, selectcolor=CHIP_BG,
                       font=("Segoe UI", 10)).pack(anchor="w", pady=(8, 0))
        tk.Checkbutton(o, text=self.t("chk_mouse"), variable=self.moves_var, bg=CARD, fg=TEXT,
                       activebackground=CARD, activeforeground=TEXT, selectcolor=CHIP_BG,
                       font=("Segoe UI", 10)).pack(anchor="w")
        cb = tk.Checkbutton(o, text=self.t("chk_sound"), variable=self.sound_var, bg=CARD, fg=TEXT,
                            activebackground=CARD, activeforeground=TEXT, selectcolor=CHIP_BG,
                            font=("Segoe UI", 10))
        cb.pack(anchor="w")
        if not HAS_SOUND:
            cb.config(state="disabled")
        tk.Checkbutton(o, text=self.t("chk_awake"), variable=self.awake_var, bg=CARD, fg=TEXT,
                       activebackground=CARD, activeforeground=TEXT, selectcolor=CHIP_BG,
                       font=("Segoe UI", 9)).pack(anchor="w")

        # Tarjeta Programar
        pr = self._card(self.body, self.t("card_sched"))
        prow = tk.Frame(pr, bg=CARD); prow.pack(fill="x", pady=3)
        self._row_label(prow, self.t("lbl_start_in")).pack(side="left")
        self._field(prow, self.sched_h_var, width=4).pack(side="left", padx=(8, 2))
        tk.Label(prow, text="h", bg=CARD, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")
        self._field(prow, self.sched_m_var, width=4).pack(side="left", padx=(8, 2))
        tk.Label(prow, text="m", bg=CARD, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")
        pbtns = tk.Frame(pr, bg=CARD); pbtns.pack(fill="x", pady=(8, 2))
        tk.Button(pbtns, text=self.t("btn_schedule"), command=self.schedule_start, bg=ACCENT, fg="white",
                  activebackground="#9333ea", relief="flat", bd=0, cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=14, pady=5).pack(side="left")
        tk.Button(pbtns, text=self.t("btn_cancel"), command=self.cancel_schedule, bg=BTN_BG, fg="white",
                  activebackground=RED, relief="flat", bd=0, cursor="hand2",
                  font=("Segoe UI", 9), padx=14, pady=5).pack(side="left", padx=8)
        tk.Label(pr, textvariable=self.sched_var, bg=CARD, fg=GOLD,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 0))

        # Guardar / Cargar / Limpiar
        files = tk.Frame(self.body, bg=BG)
        files.pack(pady=(10, 4))
        for txt, cmd in ((self.t("btn_save"), self.save_macro), (self.t("btn_load"), self.load_macro),
                         (self.t("btn_clear"), self.clear_macro)):
            tk.Button(files, text=txt, width=9, command=cmd, bg=BTN_BG, fg="white",
                      activebackground=ACCENT, relief="flat", bd=0, cursor="hand2",
                      font=("Segoe UI", 9), pady=5).pack(side="left", padx=4)

        tk.Label(self.body, text=self.t("footer"), bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(pady=10)
        tk.Label(self.body, textvariable=self.dbg_var, bg=BG, fg="#7dd3fc",
                 font=("Consolas", 8)).pack(pady=(0, 10))

    # ---------- Programar ----------
    def schedule_start(self):
        if self.recording or self.playing or self._capturing:
            return
        if not self.events:
            messagebox.showinfo("Recorder-PRO", self.t("sched_no_rec"))
            return
        try:
            h = int(self.sched_h_var.get() or 0)
            m = int(self.sched_m_var.get() or 0)
        except ValueError:
            messagebox.showerror("Recorder-PRO", self.t("sched_bad_num"))
            return
        total = h * 3600 + m * 60
        if total <= 0:
            messagebox.showinfo("Recorder-PRO", self.t("sched_zero"))
            return
        self._scheduled_at = time.time() + total
        messagebox.showinfo("Recorder-PRO", self.t("sched_ok", t=fmt_hms(total)))

    def cancel_schedule(self):
        self._scheduled_at = None
        self.sched_var.set("")

    def capture_key(self, which):
        if self.recording or self.playing:
            return
        self._capturing = which

    # ---------- Refresco ----------
    def _refresh_ui(self):
        self._rec_moves = self.moves_var.get()
        self._rec_kbd = self.kbd_var.get()
        self._keep_awake = self.awake_var.get()

        # Procesar las teclas pulsadas (grabar / reproducir) en el hilo de la ventana
        if self._req_record:
            self._req_record = False
            self.toggle_record()
        if self._req_play:
            self._req_play = False
            self.toggle_play()

        scheduled = False
        if self._scheduled_at is not None and not self.playing and not self.recording and not self._capturing:
            remaining = self._scheduled_at - time.time()
            if remaining <= 0:
                self._scheduled_at = None
                self.sched_var.set("")
                self.toggle_play()
            else:
                scheduled = True
                self.sched_var.set(self.t("starts_in", r=fmt_hms(remaining)))
        elif self._scheduled_at is None and not self.playing:
            self.sched_var.set("")

        self.lbl_key_record.config(text=key_label(self.key_record))
        self.lbl_key_play.config(text=key_label(self.key_play))
        self.counter_var.set(self.t("counter", n=len(self.events)))
        self.dbg_var.set(self._dbg)

        if self._capturing:
            self.status_var.set(self.t("press_key"))
            self.status_lbl.config(fg=GOLD)
        elif self.recording:
            self.status_var.set(self.t("recording"))
            self.status_lbl.config(fg=RED)
            self.btn_record.config(text=self.t("btn_stop"))
            self.time_var.set("")
        elif self.playing:
            self.status_var.set(self.t("playing"))
            self.status_lbl.config(fg=GREEN)
            self.btn_play.config(text=self.t("btn_stop"))
            self._update_countdown()
        else:
            if scheduled:
                self.status_var.set(self.t("scheduled"))
                self.status_lbl.config(fg=GOLD)
                self.time_var.set(self.t("starts_in", r=fmt_hms(remaining)))
            else:
                self.status_var.set(self.t("ready"))
                self.status_lbl.config(fg=TEXT)
                self._update_estimate()
            self.btn_record.config(text=self.t("btn_record"))
            self.btn_play.config(text=self.t("btn_play"))

        self.root.after(150, self._refresh_ui)

    def _one_pass_seconds(self):
        return sum(ev.get("delay", 0) for ev in self.events)

    def _read_numbers(self):
        try:
            repeat = int(self.repeat_var.get())
        except ValueError:
            repeat = 1
        try:
            speed = float(self.speed_var.get())
        except ValueError:
            speed = 1.0
        if speed <= 0:
            speed = 1.0
        try:
            delay = float(self.delay_var.get())
        except ValueError:
            delay = 0.0
        return repeat, speed, delay

    def _update_estimate(self):
        if not self.events:
            self.time_var.set("")
            return
        repeat, speed, delay = self._read_numbers()
        one = self._one_pass_seconds() / speed
        if repeat > 0:
            total = delay + one * repeat
            self.time_var.set(self.t("one_pass", a=fmt_hms(one), r=repeat, b=fmt_hms(total)))
        else:
            self.time_var.set(self.t("one_pass_inf", a=fmt_hms(one)))

    def _update_countdown(self):
        if self._play_started_at is None:
            self.time_var.set(self.t("starting"))
            return
        elapsed = time.time() - self._play_started_at
        cur, tot = self._current_loop, self._total_loops
        if tot > 0:
            self.time_var.set(self.t("count_fin", c=cur, t=tot, r=fmt_hms(self._play_total_est - elapsed)))
        else:
            self.time_var.set(self.t("count_inf", c=cur, e=fmt_hms(elapsed)))

    def _beep(self, start=True):
        if HAS_SOUND and self.sound_var.get():
            try:
                winsound.Beep(880 if start else 440, 120)
            except Exception:
                pass

    # ---------- Grabacion ----------
    def toggle_record(self):
        if self.playing or self._capturing:
            return
        if self.recording:
            self.recording = False
            self._beep(start=False)
        else:
            self.events = []
            self.last_event_time = time.time()
            self.last_move_time = 0.0
            self.recording = True
            self._beep(start=True)

    def _record(self, ev):
        now = time.time()
        ev["delay"] = now - (self.last_event_time or now)
        self.last_event_time = now
        self.events.append(ev)

    def _on_move(self, x, y):
        try:
            if not self.recording or not self._rec_moves:
                return
            now = time.time()
            if now - self.last_move_time < MOVE_THROTTLE:
                return
            self.last_move_time = now
            self._record({"t": "move", "x": x, "y": y})
        except Exception:
            pass

    def _on_click(self, x, y, button, pressed):
        try:
            if not self.recording:
                return
            self._record({"t": "click", "x": x, "y": y, "b": button.name, "p": pressed})
        except Exception:
            pass

    def _on_scroll(self, x, y, dx, dy):
        try:
            if not self.recording:
                return
            self._record({"t": "scroll", "x": x, "y": y, "dx": dx, "dy": dy})
        except Exception:
            pass

    def _on_press(self, key):
        try:
            try:
                self._dbg = (f"tecla: {key_label(key)}  |  "
                             f"=grabar? {keys_match(key, self.key_record)}  |  "
                             f"=reprod? {keys_match(key, self.key_play)}")
            except Exception:
                pass
            if self._capturing:
                if self._capturing == "record":
                    self.key_record = key
                else:
                    self.key_play = key
                self._capturing = None
                self._save_settings()
                return
            if keys_match(key, self.key_record):
                self._req_record = True
                return
            if keys_match(key, self.key_play):
                self._req_play = True
                return
            if key == HOTKEY_STOP:
                if self.playing:
                    self.stop_flag.set()
                return
            if self.recording and self._rec_kbd:
                self._record({"t": "kdown", "k": serialize_key(key)})
        except Exception:
            pass

    def _on_release(self, key):
        try:
            if keys_match(key, self.key_record) or keys_match(key, self.key_play) or key == HOTKEY_STOP:
                return
            if self.recording and self._rec_kbd:
                self._record({"t": "kup", "k": serialize_key(key)})
        except Exception:
            pass

    # ---------- Reproduccion ----------
    def toggle_play(self):
        if self.recording or self._capturing:
            return
        if self.playing:
            self.stop_flag.set()
            return
        if not self.events:
            messagebox.showinfo("Recorder-PRO", self.t("nothing_rec"))
            return
        repeat, speed, start_delay = self._read_numbers()
        one = self._one_pass_seconds() / speed
        self._total_loops = repeat
        self._current_loop = 0
        self._play_total_est = (one * repeat) if repeat > 0 else 0.0
        self._play_started_at = None
        self.stop_flag.clear()
        self.playing = True
        self.play_thread = threading.Thread(
            target=self._play_worker, args=(repeat, speed, start_delay), daemon=True)
        self.play_thread.start()

    def _play_worker(self, repeat, speed, start_delay):
        waited = 0.0
        while waited < start_delay and not self.stop_flag.is_set():
            time.sleep(0.05)
            waited += 0.05
        self._play_started_at = time.time()
        loop = 0
        while not self.stop_flag.is_set():
            self._current_loop = loop + 1
            for ev in self.events:
                if self.stop_flag.is_set():
                    break
                d = ev.get("delay", 0) / speed
                slept = 0.0
                while slept < d and not self.stop_flag.is_set():
                    chunk = min(0.02, d - slept)
                    time.sleep(chunk)
                    slept += chunk
                if self.stop_flag.is_set():
                    break
                self._dispatch(ev)
            loop += 1
            if repeat != 0 and loop >= repeat:
                break
        self.playing = False
        self._play_started_at = None
        if HAS_SOUND and self.sound_var.get() and not self.stop_flag.is_set():
            try:
                winsound.Beep(660, 200)
            except Exception:
                pass

    def _dispatch(self, ev):
        try:
            t = ev["t"]
            if t == "move":
                self.mouse_ctrl.position = (ev["x"], ev["y"])
            elif t == "click":
                self.mouse_ctrl.position = (ev["x"], ev["y"])
                btn = getattr(Button, ev["b"])
                (self.mouse_ctrl.press if ev["p"] else self.mouse_ctrl.release)(btn)
            elif t == "scroll":
                self.mouse_ctrl.position = (ev["x"], ev["y"])
                self.mouse_ctrl.scroll(ev["dx"], ev["dy"])
            elif t == "kdown":
                self.kbd_ctrl.press(deserialize_key(ev["k"]))
            elif t == "kup":
                self.kbd_ctrl.release(deserialize_key(ev["k"]))
        except Exception:
            pass

    # ---------- Mantener despierto ----------
    def _awake_worker(self):
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002
        have_windll = HAS_CTYPES and hasattr(ctypes, "windll")
        while True:
            try:
                if self._keep_awake:
                    if have_windll:
                        ctypes.windll.kernel32.SetThreadExecutionState(
                            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
                    if not self.recording:
                        try:
                            k = KeyCode.from_vk(0x7E)
                            self.kbd_ctrl.press(k)
                            self.kbd_ctrl.release(k)
                        except Exception:
                            pass
                else:
                    if have_windll:
                        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            except Exception:
                pass
            time.sleep(30)

    # ---------- Ficheros ----------
    def save_macro(self):
        if not self.events:
            messagebox.showinfo("Recorder-PRO", self.t("nothing_save"))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("Macro JSON", "*.json"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"version": 4, "events": self.events}, f)
            messagebox.showinfo("Recorder-PRO", self.t("saved", n=len(self.events)))
        except Exception as e:
            messagebox.showerror("Recorder-PRO", self.t("err_save", e=e))

    def load_macro(self):
        path = filedialog.askopenfilename(
            filetypes=[("Macro JSON", "*.json"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.events = data.get("events", [])
            messagebox.showinfo("Recorder-PRO", self.t("loaded", n=len(self.events)))
        except Exception as e:
            messagebox.showerror("Recorder-PRO", self.t("err_load", e=e))

    def clear_macro(self):
        if self.recording or self.playing:
            return
        if not self.events:
            return
        if messagebox.askyesno("Recorder-PRO", "Borrar la grabacion actual? / Delete current recording?"):
            self.events = []

    # ---------- Ajustes (recordar teclas e idioma) ----------
    def _load_settings(self):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("lang") in ("es", "en"):
                self.lang = data["lang"]
            if "key_record" in data:
                self.key_record = deserialize_key(data["key_record"])
            if "key_play" in data:
                self.key_play = deserialize_key(data["key_play"])
            if "kbd" in data:
                self.kbd_var.set(bool(data["kbd"]))
            if "moves" in data:
                self.moves_var.set(bool(data["moves"]))
            if "sound" in data and HAS_SOUND:
                self.sound_var.set(bool(data["sound"]))
            if "awake" in data:
                self.awake_var.set(bool(data["awake"]))
        except Exception:
            pass  # Si no hay ajustes o falla, se usan los valores por defecto

    def _save_settings(self):
        try:
            data = {
                "lang": self.lang,
                "key_record": serialize_key(self.key_record),
                "key_play": serialize_key(self.key_play),
                "kbd": bool(self.kbd_var.get()),
                "moves": bool(self.moves_var.get()),
                "sound": bool(self.sound_var.get()),
                "awake": bool(self.awake_var.get()),
            }
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    def _on_close(self):
        self._save_settings()
        self.stop_flag.set()
        try:
            self.mouse_listener.stop()
            self.kbd_listener.stop()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    MacroRecorder(root)
    root.mainloop()


if __name__ == "__main__":
    main()