# ============================================================
#  Timer.py  —  HUD-themed Countdown Timer
#  Matches the design language of AlarmClock.py and the
#  Combined Daily Task Manager
# ============================================================

import threading
import tkinter as tk
from tkinter import messagebox
import sys
import os

# ── Cross-platform alarm sound ──────────────────────────────
def _play_alarm():
    """
    Loops a beeping sound until the global `timer_ringing` flag is False.
    Uses winsound on Windows, afplay on macOS, terminal bell on Linux.
    """
    while timer_ringing:
        if sys.platform == "win32":
            import winsound
            winsound.Beep(1000, 500)
        elif sys.platform == "darwin":
            os.system("afplay /System/Library/Sounds/Ping.aiff 2>/dev/null")
            threading.Event().wait(0.1)
        else:
            print("\a", end="", flush=True)
            threading.Event().wait(0.6)

# ── Shared state ─────────────────────────────────────────────
timer_ringing = False    # True while the timer is going off

# ── Theme (identical HUD palette) ────────────────────────────
THEME = {
    "bg":            "#0e1621",
    "panel_outer":   "#101c2a",
    "panel_inner":   "#182636",
    "stroke_dark":   "#0a111a",
    "stroke_mid":    "#2a3c52",
    "stroke_light":  "#47647f",
    "accent":        "#6fb3c8",
    "text":          "#dce8f2",
    "muted":         "#9fb4c6",
    "danger":        "#ff5a5a",
    "ok":            "#44ff99",
    "btn_bg":        "#1a2a3c",
    "btn_bg_hover":  "#22384f",
    "warn":          "#f0a500",
}

def _on_hover(btn, normal, hover):
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=normal))

# ── HUD Panel (same as AlarmClock / Task Manager) ────────────
class HudPanel(tk.Canvas):
    """Decorative HUD frame; real widgets live inside self.content."""

    def __init__(self, master, width=520, height=560, padding=22, **kwargs):
        super().__init__(
            master,
            width=width, height=height,
            bg=THEME["bg"],
            highlightthickness=0, bd=0,
            **kwargs
        )
        self.padding = padding
        self._cw, self._ch = width, height

        self.content = tk.Frame(self, bg=THEME["panel_inner"])
        self._cwin = self.create_window(
            padding, padding, anchor="nw",
            window=self.content,
            width=width  - 2 * padding,
            height=height - 2 * padding,
        )
        self.bind("<Configure>", self._redraw)
        self._redraw()

    def _redraw(self, event=None):
        w = event.width  if event else self._cw
        h = event.height if event else self._ch
        self._cw, self._ch = w, h
        pad = self.padding

        self.itemconfig(self._cwin,
                        width=max(10, w - 2 * pad),
                        height=max(10, h - 2 * pad))
        self.delete("hud")

        self.create_rectangle(
            pad-10, pad-10, w-(pad-10), h-(pad-10),
            fill=THEME["panel_outer"], outline=THEME["stroke_dark"], width=2, tags="hud"
        )
        self.create_rectangle(
            pad, pad, w-pad, h-pad,
            fill=THEME["panel_inner"], outline=THEME["stroke_mid"], width=2, tags="hud"
        )
        self.create_line(
            pad+16, pad+10, w-pad-90, pad+10,
            fill=THEME["accent"], width=2, tags="hud"
        )
        self.create_rectangle(
            w-pad-88, pad+4, w-pad-14, pad+16,
            fill=THEME["panel_inner"], outline=THEME["accent"], width=2, tags="hud"
        )
        c = 18
        for x1,y1,x2,y2,x3,y3 in [
            (pad,pad+c,  pad,pad,  pad+c,pad),
            (w-pad-c,pad,  w-pad,pad,  w-pad,pad+c),
            (pad,h-pad-c,  pad,h-pad,  pad+c,h-pad),
            (w-pad-c,h-pad,  w-pad,h-pad,  w-pad,h-pad-c),
        ]:
            self.create_line(x1,y1,x2,y2,x3,y3,
                             fill=THEME["stroke_light"], width=2, tags="hud")

# ── Progress Bar Widget ───────────────────────────────────────
class HudProgressBar(tk.Frame):
    """
    A simple horizontal progress bar that fits the HUD theme.
    Inherits from Frame (not Canvas) to avoid tkinter TclErrors
    when width/height integers are passed during construction.
    Call .set(fraction, color) with a value 0.0–1.0 to update.
    """
    def __init__(self, master, width=440, height=16, **kwargs):
        # Strip width/height from kwargs so Frame doesn't get confused
        super().__init__(master, bg=THEME["panel_inner"],
                         width=width, height=height, **kwargs)
        self.pack_propagate(False)   # honour the fixed width/height

        self._fraction = 1.0
        self._color    = THEME["ok"]

        # The actual drawing surface lives inside the Frame
        self._canvas = tk.Canvas(
            self, bg=THEME["btn_bg"],
            highlightthickness=1,
            highlightbackground=THEME["stroke_mid"],
            bd=0
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)
        self._canvas.bind("<Configure>", self._draw)

    def set(self, fraction, color=None):
        self._fraction = max(0.0, min(1.0, fraction))
        if color:
            self._color = color
        self._draw()

    def _draw(self, event=None):
        c = self._canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 2 or h < 2:
            return

        # Filled portion
        fill_w = int(w * self._fraction)
        if fill_w > 1:
            c.create_rectangle(0, 0, fill_w, h,
                                fill=self._color, outline="")

        # Tick marks every 10 %
        for i in range(1, 10):
            x = int(w * i / 10)
            c.create_line(x, h - 5, x, h,
                          fill=THEME["stroke_light"], width=1)

# ── Quick-set preset button ───────────────────────────────────
def _preset_btn(parent, label, h, m, s, callback):
    btn = tk.Button(
        parent, text=label,
        bg=THEME["btn_bg"], fg=THEME["accent"],
        activebackground=THEME["btn_bg_hover"], activeforeground=THEME["accent"],
        font=("Courier", 10, "bold"),
        bd=0, highlightthickness=1,
        highlightbackground=THEME["stroke_mid"],
        highlightcolor=THEME["accent"],
        padx=10, pady=6,
        command=lambda: callback(h, m, s)
    )
    _on_hover(btn, THEME["btn_bg"], THEME["btn_bg_hover"])
    return btn

# ── Main App ─────────────────────────────────────────────────
class TimerApp:
    """
    HUD Countdown Timer.

    How it works
    ────────────
    1.  Enter hours, minutes, and seconds in the three entry boxes
        (or click one of the quick-preset buttons).
    2.  Press START — the big countdown display begins ticking down.
    3.  You can PAUSE / RESUME at any time.
    4.  The progress bar drains left-to-right as time elapses.
        It turns yellow under 20 % remaining, red under 10 %.
    5.  When it hits 00:00:00 the panel flashes red and the alarm
        sound plays in a background thread.
    6.  Press STOP to silence the alarm, or EXIT to close.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HUD Timer")
        self.root.geometry("520x580")
        self.root.resizable(False, False)
        self.root.configure(bg=THEME["bg"])

        # ── Timer state ───────────────────────────────────────
        self._total_seconds   = 0      # original duration (for progress bar)
        self._remaining       = 0      # seconds left
        self._running         = False  # actively counting down
        self._flash_on        = False  # for ringing flash
        global timer_ringing
        timer_ringing = False

        # ── Build UI ──────────────────────────────────────────
        self.panel = HudPanel(root, width=520, height=580, padding=22)
        self.panel.pack()
        cf = self.panel.content

        # Title
        title_row = tk.Frame(cf, bg=THEME["panel_inner"])
        title_row.pack(fill=tk.X, padx=14, pady=(14, 2))
        tk.Label(title_row, text="COUNTDOWN TIMER",
                 font=("Courier", 16, "bold"),
                 fg=THEME["muted"], bg=THEME["panel_inner"]
                 ).pack(side=tk.LEFT)

        # ── Big countdown display ─────────────────────────────
        self.display_lbl = tk.Label(
            cf, text="00:00:00",
            font=("Courier", 58, "bold"),
            fg=THEME["ok"],
            bg=THEME["panel_inner"]
        )
        self.display_lbl.pack(pady=(10, 4))

        # Status line
        self.status_lbl = tk.Label(
            cf, text="READY",
            font=("Courier", 13, "bold"),
            fg=THEME["muted"],
            bg=THEME["panel_inner"]
        )
        self.status_lbl.pack(pady=(0, 8))

        # Progress bar
        self.progress = HudProgressBar(cf, width=440, height=16)
        self.progress.pack(padx=14, pady=(0, 10))

        # Divider
        tk.Frame(cf, bg=THEME["stroke_mid"], height=1).pack(fill=tk.X, padx=14, pady=(2, 12))

        # ── Input row  H : M : S ──────────────────────────────
        input_section = tk.Frame(cf, bg=THEME["panel_inner"])
        input_section.pack(fill=tk.X, padx=14, pady=(0, 6))

        tk.Label(input_section, text="SET DURATION",
                 font=("Arial", 11, "bold"),
                 fg=THEME["muted"], bg=THEME["panel_inner"]
                 ).pack(anchor="w", pady=(0, 8))

        fields_row = tk.Frame(input_section, bg=THEME["panel_inner"])
        fields_row.pack(anchor="center")

        entry_cfg = dict(
            font=("Courier", 22, "bold"),
            fg=THEME["accent"],
            bg=THEME["btn_bg"],
            insertbackground=THEME["accent"],
            relief=tk.FLAT, bd=0,
            highlightthickness=2,
            highlightbackground=THEME["stroke_mid"],
            highlightcolor=THEME["accent"],
            width=3, justify="center"
        )
        lbl_cfg = dict(
            font=("Courier", 22, "bold"),
            fg=THEME["stroke_light"],
            bg=THEME["panel_inner"]
        )

        self.hours_var   = tk.StringVar(value="0")
        self.minutes_var = tk.StringVar(value="0")
        self.seconds_var = tk.StringVar(value="0")

        self.hours_entry   = tk.Entry(fields_row, textvariable=self.hours_var,   **entry_cfg)
        self.minutes_entry = tk.Entry(fields_row, textvariable=self.minutes_var, **entry_cfg)
        self.seconds_entry = tk.Entry(fields_row, textvariable=self.seconds_var, **entry_cfg)

        self.hours_entry.pack(side=tk.LEFT, ipady=8)
        tk.Label(fields_row, text=" H  ", **lbl_cfg).pack(side=tk.LEFT)
        self.minutes_entry.pack(side=tk.LEFT, ipady=8)
        tk.Label(fields_row, text=" M  ", **lbl_cfg).pack(side=tk.LEFT)
        self.seconds_entry.pack(side=tk.LEFT, ipady=8)
        tk.Label(fields_row, text=" S",   **lbl_cfg).pack(side=tk.LEFT)

        # Tab / Enter navigation between fields
        self.hours_entry.bind("<Tab>",    lambda e: (self.minutes_entry.focus(), "break"))
        self.minutes_entry.bind("<Tab>",  lambda e: (self.seconds_entry.focus(), "break"))
        self.seconds_entry.bind("<Tab>",  lambda e: (self.hours_entry.focus(),   "break"))
        self.seconds_entry.bind("<Return>", lambda e: self.start_timer())

        # ── Quick preset buttons ──────────────────────────────
        presets_lbl = tk.Label(input_section,
                               text="QUICK SET",
                               font=("Arial", 10, "bold"),
                               fg=THEME["muted"], bg=THEME["panel_inner"])
        presets_lbl.pack(anchor="w", pady=(12, 6))

        presets_row = tk.Frame(input_section, bg=THEME["panel_inner"])
        presets_row.pack(anchor="w")

        presets = [
            ("1 min",  0,  1, 0),
            ("5 min",  0,  5, 0),
            ("10 min", 0, 10, 0),
            ("15 min", 0, 15, 0),
            ("30 min", 0, 30, 0),
            ("1 hr",   1,  0, 0),
        ]
        for label, h, m, s in presets:
            btn = _preset_btn(presets_row, label, h, m, s, self._apply_preset)
            btn.pack(side=tk.LEFT, padx=(0, 6))

        # Divider
        tk.Frame(cf, bg=THEME["stroke_mid"], height=1).pack(fill=tk.X, padx=14, pady=(12, 12))

        # ── Control buttons ───────────────────────────────────
        ctrl_row = tk.Frame(cf, bg=THEME["panel_inner"])
        ctrl_row.pack(fill=tk.X, padx=14, pady=(0, 6))

        # START / PAUSE  (same button, label changes)
        self.start_btn = tk.Button(
            ctrl_row, text="▶  START",
            bg=THEME["ok"], fg=THEME["bg"],
            activebackground="#33cc77", activeforeground=THEME["bg"],
            font=("Arial", 12, "bold"),
            bd=0, highlightthickness=0,
            padx=14, pady=10,
            command=self.start_timer
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = tk.Button(
            ctrl_row, text="⏹  STOP",
            bg=THEME["danger"], fg=THEME["text"],
            activebackground="#cc3333", activeforeground=THEME["text"],
            font=("Arial", 12, "bold"),
            bd=0, highlightthickness=0,
            padx=14, pady=10,
            state=tk.DISABLED,
            command=self.stop_timer
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 8))

        reset_btn = tk.Button(
            ctrl_row, text="↺  RESET",
            bg=THEME["btn_bg"], fg=THEME["text"],
            activebackground=THEME["btn_bg_hover"], activeforeground=THEME["text"],
            font=("Arial", 12, "bold"),
            bd=0, highlightthickness=1,
            highlightbackground=THEME["stroke_mid"],
            highlightcolor=THEME["accent"],
            padx=14, pady=10,
            command=self.reset_timer
        )
        reset_btn.pack(side=tk.LEFT, padx=(0, 8))
        _on_hover(reset_btn, THEME["btn_bg"], THEME["btn_bg_hover"])

        exit_btn = tk.Button(
            ctrl_row, text="⏻  EXIT",
            bg=THEME["btn_bg"], fg=THEME["text"],
            activebackground=THEME["btn_bg_hover"], activeforeground=THEME["text"],
            font=("Arial", 12, "bold"),
            bd=0, highlightthickness=1,
            highlightbackground=THEME["stroke_mid"],
            highlightcolor=THEME["accent"],
            padx=14, pady=10,
            command=self.root.quit
        )
        exit_btn.pack(side=tk.RIGHT)
        _on_hover(exit_btn, THEME["btn_bg"], THEME["btn_bg_hover"])

    # ─────────────────────────────────────────────────────────
    #  Preset helper
    # ─────────────────────────────────────────────────────────
    def _apply_preset(self, h: int, m: int, s: int):
        """Fill the entry boxes with a preset and auto-start."""
        self.hours_var.set(str(h))
        self.minutes_var.set(str(m))
        self.seconds_var.set(str(s))
        self.start_timer()

    # ─────────────────────────────────────────────────────────
    #  Parse entry boxes
    # ─────────────────────────────────────────────────────────
    def _read_inputs(self) -> int | None:
        """
        Reads H / M / S entry boxes and returns total seconds.
        Returns None and shows an error if the input is invalid.
        """
        try:
            h = int(self.hours_var.get()   or 0)
            m = int(self.minutes_var.get() or 0)
            s = int(self.seconds_var.get() or 0)
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Hours, minutes, and seconds must be whole numbers.")
            return None

        if h < 0 or m < 0 or s < 0:
            messagebox.showerror("Invalid Input", "Values cannot be negative.")
            return None
        if m > 59 or s > 59:
            messagebox.showerror("Invalid Input",
                                 "Minutes and seconds must be between 0 and 59.")
            return None

        total = h * 3600 + m * 60 + s
        if total == 0:
            messagebox.showwarning("No Time Set",
                                   "Please enter a duration greater than zero.")
            return None
        return total

    # ─────────────────────────────────────────────────────────
    #  Format seconds → HH:MM:SS string
    # ─────────────────────────────────────────────────────────
    @staticmethod
    def _fmt(secs: int) -> str:
        secs = max(0, secs)
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    # ─────────────────────────────────────────────────────────
    #  Update progress bar colour based on remaining fraction
    # ─────────────────────────────────────────────────────────
    def _progress_color(self, fraction: float) -> str:
        if fraction > 0.20:
            return THEME["ok"]      # green  — plenty of time
        elif fraction > 0.10:
            return THEME["warn"]    # yellow — getting close
        else:
            return THEME["danger"]  # red    — almost done

    # ─────────────────────────────────────────────────────────
    #  START / PAUSE toggle
    # ─────────────────────────────────────────────────────────
    def start_timer(self):
        global timer_ringing

        # If alarm is currently ringing, START acts as STOP
        if timer_ringing:
            self.stop_timer()
            return

        # If already running → PAUSE
        if self._running:
            self._running = False
            self.start_btn.config(text="▶  RESUME")
            self.status_lbl.config(text="PAUSED", fg=THEME["warn"])
            return

        # If paused (remaining > 0) → RESUME
        if self._remaining > 0 and not self._running:
            self._running = True
            self.start_btn.config(text="⏸  PAUSE")
            self.status_lbl.config(text="RUNNING", fg=THEME["ok"])
            self._tick()
            return

        # Fresh start — read inputs
        total = self._read_inputs()
        if total is None:
            return

        self._total_seconds = total
        self._remaining     = total
        self._running       = True

        self.start_btn.config(text="⏸  PAUSE")
        self.stop_btn.config(state=tk.NORMAL)
        self.status_lbl.config(text="RUNNING", fg=THEME["ok"])
        self.display_lbl.config(text=self._fmt(total), fg=THEME["ok"],
                                bg=THEME["panel_inner"])

        self._tick()

    # ─────────────────────────────────────────────────────────
    #  STOP  (silences alarm OR stops countdown)
    # ─────────────────────────────────────────────────────────
    def stop_timer(self):
        global timer_ringing

        timer_ringing   = False
        self._running   = False
        self._flash_on  = False

        self.start_btn.config(text="▶  START")
        self.stop_btn.config(state=tk.DISABLED)
        self.status_lbl.config(text="STOPPED", fg=THEME["muted"])

        # Restore backgrounds
        for w in (self.panel.content,
                  self.display_lbl, self.status_lbl):
            w.config(bg=THEME["panel_inner"])

    # ─────────────────────────────────────────────────────────
    #  RESET  — go back to 00:00:00 and clear inputs
    # ─────────────────────────────────────────────────────────
    def reset_timer(self):
        global timer_ringing

        timer_ringing      = False
        self._running      = False
        self._remaining    = 0
        self._total_seconds = 0
        self._flash_on     = False

        self.hours_var.set("0")
        self.minutes_var.set("0")
        self.seconds_var.set("0")

        self.display_lbl.config(text="00:00:00", fg=THEME["ok"],
                                bg=THEME["panel_inner"])
        self.status_lbl.config(text="READY", fg=THEME["muted"],
                               bg=THEME["panel_inner"])
        self.progress.set(1.0, THEME["ok"])
        self.start_btn.config(text="▶  START")
        self.stop_btn.config(state=tk.DISABLED)

        for w in (self.panel.content, self.display_lbl, self.status_lbl):
            w.config(bg=THEME["panel_inner"])

    # ─────────────────────────────────────────────────────────
    #  TICK — called every 1 000 ms while running
    # ─────────────────────────────────────────────────────────
    def _tick(self):
        global timer_ringing

        if not self._running:
            return   # paused or stopped — do nothing

        if self._remaining <= 0:
            # Time's up!
            self._running = False
            self._trigger_alarm()
            return

        # Update display
        frac  = self._remaining / self._total_seconds if self._total_seconds else 0
        color = self._progress_color(frac)

        self.display_lbl.config(text=self._fmt(self._remaining), fg=color)
        self.progress.set(frac, color)

        self._remaining -= 1
        self.root.after(1000, self._tick)

    # ─────────────────────────────────────────────────────────
    #  Trigger alarm when countdown reaches zero
    # ─────────────────────────────────────────────────────────
    def _trigger_alarm(self):
        global timer_ringing

        timer_ringing = True

        self.display_lbl.config(text="00:00:00", fg=THEME["danger"])
        self.progress.set(0.0, THEME["danger"])
        self.status_lbl.config(text="⚠  TIME'S UP  ⚠", fg=THEME["danger"])
        self.start_btn.config(text="▶  START")
        self.stop_btn.config(state=tk.NORMAL)

        # Start sound on background thread
        t = threading.Thread(target=_play_alarm, daemon=True)
        t.start()

        self._flash()

    # ─────────────────────────────────────────────────────────
    #  Flash animation while alarm is ringing
    # ─────────────────────────────────────────────────────────
    def _flash(self):
        global timer_ringing

        if not timer_ringing:
            # Restore backgrounds once ringing stops
            for w in (self.panel.content, self.display_lbl, self.status_lbl):
                w.config(bg=THEME["panel_inner"])
            return

        self._flash_on = not self._flash_on
        bg = THEME["danger"] if self._flash_on else THEME["panel_inner"]

        for w in (self.panel.content, self.display_lbl, self.status_lbl):
            w.config(bg=bg)

        self.root.after(500, self._flash)


# ── Entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = TimerApp(root)
    root.mainloop()