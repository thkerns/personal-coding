# ============================================================
#  AlarmClock.py  —  HUD-themed Alarm Clock
#  Matches the design language of the Combined Daily Task Manager
# ============================================================

import datetime
import threading
import tkinter as tk
from tkinter import messagebox
import winsound  # Windows built-in beep (replaced below for cross-platform)
import sys
import os

# ── Cross-platform alarm sound ──────────────────────────────
def _play_alarm():
    """
    Loops a beeping sound until the global `alarm_active` flag is False.
    Uses winsound on Windows, and the terminal bell on macOS/Linux.
    """
    while alarm_active:
        if sys.platform == "win32":
            winsound.Beep(1000, 500)   # frequency=1000 Hz, duration=500 ms
        else:
            # On macOS/Linux we use the 'afplay' system sound or terminal bell
            if sys.platform == "darwin":
                os.system("afplay /System/Library/Sounds/Ping.aiff 2>/dev/null &")
                threading.Event().wait(0.6)
            else:
                print("\a", end="", flush=True)   # terminal bell
                threading.Event().wait(0.6)

# ── Shared flag ──────────────────────────────────────────────
alarm_active = False          # True while the alarm is ringing
alarm_thread  = None          # background thread that plays the sound

# ── Theme (identical palette to your original HUD app) ───────
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
}

# ── Helper ───────────────────────────────────────────────────
def _on_hover(btn, normal, hover):
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=normal))

# ── HUD panel (same canvas-based panel as the original) ──────
class HudPanel(tk.Canvas):
    """Decorative HUD frame; real widgets live inside self.content."""

    def __init__(self, master, width=520, height=540, padding=22, **kwargs):
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
            height=height - 2 * padding
        )
        self.bind("<Configure>", self._redraw)
        self._redraw()

    def _redraw(self, event=None):
        w = event.width  if event else self._cw
        h = event.height if event else self._ch
        self._cw, self._ch = w, h
        pad = self.padding

        self.itemconfig(self._cwin,
                        width=max(10, w - 2*pad),
                        height=max(10, h - 2*pad))
        self.delete("hud")

        # Outer rect
        self.create_rectangle(
            pad-10, pad-10, w-(pad-10), h-(pad-10),
            fill=THEME["panel_outer"], outline=THEME["stroke_dark"], width=2, tags="hud"
        )
        # Inner rect
        self.create_rectangle(
            pad, pad, w-pad, h-pad,
            fill=THEME["panel_inner"], outline=THEME["stroke_mid"], width=2, tags="hud"
        )
        # Top accent line + small box (brand detail)
        self.create_line(
            pad+16, pad+10, w-pad-90, pad+10,
            fill=THEME["accent"], width=2, tags="hud"
        )
        self.create_rectangle(
            w-pad-88, pad+4, w-pad-14, pad+16,
            fill=THEME["panel_inner"], outline=THEME["accent"], width=2, tags="hud"
        )
        # Corner brackets
        c = 18
        for x1,y1,x2,y2,x3,y3 in [
            (pad,pad+c, pad,pad, pad+c,pad),
            (w-pad-c,pad, w-pad,pad, w-pad,pad+c),
            (pad,h-pad-c, pad,h-pad, pad+c,h-pad),
            (w-pad-c,h-pad, w-pad,h-pad, w-pad,h-pad-c),
        ]:
            self.create_line(x1,y1,x2,y2,x3,y3,
                             fill=THEME["stroke_light"], width=2, tags="hud")

# ── Main Application ─────────────────────────────────────────
class AlarmClockApp:
    """
    Alarm Clock with a HUD aesthetic.

    How it works
    ────────────
    1.  The top section shows a live clock (updates every second).
    2.  The middle section lets you type in a target time (HH:MM:SS  or  HH:MM)
        in 12-hour or 24-hour format, then press SET ALARM.
    3.  Once set, a countdown appears showing how long until the alarm fires.
    4.  When the alarm time is reached, the panel flashes, a sound plays in a
        background thread, and the STOP button becomes active.
    5.  Pressing STOP silences the alarm and resets everything.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("HUD Alarm Clock")
        self.root.geometry("520x560")
        self.root.resizable(False, False)
        self.root.configure(bg=THEME["bg"])

        # State
        self.alarm_time: datetime.time | None = None   # target time
        self.alarm_set   = False                        # countdown active
        self._flash_on   = False                        # for flashing animation

        # ── Build UI ─────────────────────────────────────────
        self.panel = HudPanel(root, width=520, height=540, padding=22)
        self.panel.pack(padx=0, pady=0)

        cf = self.panel.content   # shorthand

        # Title bar
        title_row = tk.Frame(cf, bg=THEME["panel_inner"])
        title_row.pack(fill=tk.X, padx=14, pady=(14, 4))

        tk.Label(title_row, text="ALARM CLOCK",
                 font=("Courier", 16, "bold"),
                 fg=THEME["muted"], bg=THEME["panel_inner"]
                 ).pack(side=tk.LEFT)

        # ── Live clock display ────────────────────────────────
        self.live_time_lbl = tk.Label(
            cf,
            text="",
            font=("Courier", 52, "bold"),
            fg=THEME["ok"],
            bg=THEME["panel_inner"]
        )
        self.live_time_lbl.pack(pady=(8, 2))

        self.live_date_lbl = tk.Label(
            cf, text="",
            font=("Arial", 13),
            fg=THEME["text"],
            bg=THEME["panel_inner"]
        )
        self.live_date_lbl.pack(pady=(0, 6))

        # Divider
        tk.Frame(cf, bg=THEME["stroke_mid"], height=1).pack(fill=tk.X, padx=14, pady=(4, 14))

        # ── Alarm-time entry ──────────────────────────────────
        entry_row = tk.Frame(cf, bg=THEME["panel_inner"])
        entry_row.pack(fill=tk.X, padx=14, pady=(0, 6))

        tk.Label(entry_row, text="SET ALARM TIME",
                 font=("Arial", 11, "bold"),
                 fg=THEME["muted"], bg=THEME["panel_inner"]
                 ).pack(anchor="w", pady=(0, 6))

        input_frame = tk.Frame(entry_row, bg=THEME["panel_inner"])
        input_frame.pack(fill=tk.X)

        # Text box where user types e.g. "07:30" or "7:30 AM"
        self.time_entry = tk.Entry(
            input_frame,
            font=("Courier", 18, "bold"),
            fg=THEME["accent"],
            bg=THEME["btn_bg"],
            insertbackground=THEME["accent"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=2,
            highlightbackground=THEME["stroke_mid"],
            highlightcolor=THEME["accent"],
            width=14,
            justify="center"
        )
        self.time_entry.insert(0, "HH:MM:SS")
        self.time_entry.pack(side=tk.LEFT, ipady=8, padx=(0, 10))

        # Clicking the entry clears the placeholder
        self.time_entry.bind("<FocusIn>",  self._clear_placeholder)
        self.time_entry.bind("<FocusOut>", self._restore_placeholder)
        self.time_entry.bind("<Return>",   lambda e: self.set_alarm())

        set_btn = tk.Button(
            input_frame, text="SET ALARM",
            bg=THEME["btn_bg"], fg=THEME["text"],
            activebackground=THEME["btn_bg_hover"], activeforeground=THEME["text"],
            font=("Arial", 11, "bold"),
            bd=0, highlightthickness=1,
            highlightbackground=THEME["stroke_mid"],
            highlightcolor=THEME["accent"],
            padx=14, pady=8,
            command=self.set_alarm
        )
        set_btn.pack(side=tk.LEFT)
        _on_hover(set_btn, THEME["btn_bg"], THEME["btn_bg_hover"])

        # ── Format hint ───────────────────────────────────────
        tk.Label(cf,
                 text="Accepted formats:  7:30   07:30   7:30 AM   19:45   7:30:00 PM",
                 font=("Arial", 9),
                 fg=THEME["muted"],
                 bg=THEME["panel_inner"]
                 ).pack(pady=(2, 10))

        # Divider
        tk.Frame(cf, bg=THEME["stroke_mid"], height=1).pack(fill=tk.X, padx=14, pady=(0, 14))

        # ── Status / countdown area ───────────────────────────
        self.status_lbl = tk.Label(
            cf, text="NO ALARM SET",
            font=("Courier", 14, "bold"),
            fg=THEME["muted"],
            bg=THEME["panel_inner"]
        )
        self.status_lbl.pack(pady=(0, 6))

        self.countdown_lbl = tk.Label(
            cf, text="",
            font=("Courier", 28, "bold"),
            fg=THEME["accent"],
            bg=THEME["panel_inner"]
        )
        self.countdown_lbl.pack(pady=(0, 14))

        # ── Stop / Cancel buttons ─────────────────────────────
        btn_row = tk.Frame(cf, bg=THEME["panel_inner"])
        btn_row.pack(fill=tk.X, padx=14, pady=(0, 6))

        self.stop_btn = tk.Button(
            btn_row, text="⏹  STOP ALARM",
            bg=THEME["danger"], fg=THEME["text"],
            activebackground="#cc3333", activeforeground=THEME["text"],
            font=("Arial", 12, "bold"),
            bd=0, highlightthickness=0,
            padx=18, pady=10,
            state=tk.DISABLED,
            command=self.stop_alarm
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        cancel_btn = tk.Button(
            btn_row, text="✕  CANCEL",
            bg=THEME["btn_bg"], fg=THEME["text"],
            activebackground=THEME["btn_bg_hover"], activeforeground=THEME["text"],
            font=("Arial", 12, "bold"),
            bd=0, highlightthickness=1,
            highlightbackground=THEME["stroke_mid"],
            highlightcolor=THEME["accent"],
            padx=18, pady=10,
            command=self.cancel_alarm
        )
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        _on_hover(cancel_btn, THEME["btn_bg"], THEME["btn_bg_hover"])

        exit_btn = tk.Button(
            btn_row, text="⏻  EXIT",
            bg=THEME["btn_bg"], fg=THEME["text"],
            activebackground=THEME["btn_bg_hover"], activeforeground=THEME["text"],
            font=("Arial", 12, "bold"),
            bd=0, highlightthickness=1,
            highlightbackground=THEME["stroke_mid"],
            highlightcolor=THEME["accent"],
            padx=18, pady=10,
            command=self.root.quit
        )
        exit_btn.pack(side=tk.LEFT)
        _on_hover(exit_btn, THEME["btn_bg"], THEME["btn_bg_hover"])

        # ── Start the loops ───────────────────────────────────
        self._tick()   # updates the live clock + countdown every second

    # ─────────────────────────────────────────────────────────
    #  Entry placeholder helpers
    # ─────────────────────────────────────────────────────────
    def _clear_placeholder(self, _event=None):
        if self.time_entry.get() == "HH:MM:SS":
            self.time_entry.delete(0, tk.END)
            self.time_entry.config(fg=THEME["accent"])

    def _restore_placeholder(self, _event=None):
        if not self.time_entry.get().strip():
            self.time_entry.insert(0, "HH:MM:SS")
            self.time_entry.config(fg=THEME["muted"])

    # ─────────────────────────────────────────────────────────
    #  Parse the user's time string
    # ─────────────────────────────────────────────────────────
    def _parse_time(self, raw: str) -> datetime.time | None:
        """
        Tries multiple time formats so the user doesn't have to be exact.
        Returns a datetime.time on success, None on failure.
        """
        raw = raw.strip()
        formats = [
            "%I:%M:%S %p",   # 07:30:00 AM
            "%I:%M %p",      # 07:30 AM  (or 7:30 am, case-insensitive)
            "%H:%M:%S",      # 19:30:00
            "%H:%M",         # 19:30
            "%I:%M:%S%p",    # 07:30:00AM  (no space)
            "%I:%M%p",       # 07:30AM
        ]
        for fmt in formats:
            try:
                return datetime.datetime.strptime(raw.upper(), fmt.upper()).time()
            except ValueError:
                continue
        return None

    # ─────────────────────────────────────────────────────────
    #  Set the alarm
    # ─────────────────────────────────────────────────────────
    def set_alarm(self):
        """
        Reads the entry box, parses the time, and starts the countdown.
        If the time has already passed today, the alarm is set for tomorrow.
        """
        global alarm_active

        raw = self.time_entry.get()
        if raw == "HH:MM:SS":
            messagebox.showwarning("No Time Entered",
                                   "Please type a time before pressing SET ALARM.")
            return

        parsed = self._parse_time(raw)
        if parsed is None:
            messagebox.showerror("Invalid Time",
                                 "Could not understand that time.\n"
                                 "Try formats like:  7:30   07:30   7:30 AM   19:45")
            return

        # Build a full datetime for today; if already past, use tomorrow
        now = datetime.datetime.now()
        target = datetime.datetime.combine(now.date(), parsed)
        if target <= now:
            target += datetime.timedelta(days=1)

        self.alarm_time = target
        self.alarm_set  = True
        alarm_active    = False   # not ringing yet

        self.status_lbl.config(
            text=f"ALARM SET  ▶  {target.strftime('%I:%M:%S %p')}",
            fg=THEME["accent"]
        )
        self.stop_btn.config(state=tk.DISABLED)

    # ─────────────────────────────────────────────────────────
    #  Cancel before it fires
    # ─────────────────────────────────────────────────────────
    def cancel_alarm(self):
        """Discard the alarm without stopping a currently ringing one."""
        global alarm_active

        if alarm_active:
            self.stop_alarm()
            return

        self.alarm_set  = False
        self.alarm_time = None

        self.status_lbl.config(text="NO ALARM SET",  fg=THEME["muted"])
        self.countdown_lbl.config(text="",           fg=THEME["accent"])
        # Reset panel colour back to normal
        self.panel.content.config(bg=THEME["panel_inner"])
        self.live_time_lbl.config(bg=THEME["panel_inner"])
        self.live_date_lbl.config(bg=THEME["panel_inner"])
        self.status_lbl.config(bg=THEME["panel_inner"])
        self.countdown_lbl.config(bg=THEME["panel_inner"])

    # ─────────────────────────────────────────────────────────
    #  Stop the ringing alarm
    # ─────────────────────────────────────────────────────────
    def stop_alarm(self):
        """Stop the alarm sound and reset the UI."""
        global alarm_active

        alarm_active   = False
        self.alarm_set = False
        self.alarm_time = None
        self._flash_on  = False

        self.stop_btn.config(state=tk.DISABLED)
        self.status_lbl.config(text="ALARM STOPPED", fg=THEME["ok"])
        self.countdown_lbl.config(text="",            fg=THEME["accent"])

        # Restore all backgrounds
        for w in (self.panel.content,
                  self.live_time_lbl, self.live_date_lbl,
                  self.status_lbl, self.countdown_lbl):
            w.config(bg=THEME["panel_inner"])

    # ─────────────────────────────────────────────────────────
    #  Trigger the alarm (called when countdown reaches zero)
    # ─────────────────────────────────────────────────────────
    def _trigger_alarm(self):
        """Switch into 'ringing' mode: enable Stop, start sound thread, flash."""
        global alarm_active, alarm_thread

        alarm_active = True
        self.stop_btn.config(state=tk.NORMAL)
        self.status_lbl.config(text="⚠  ALARM RINGING  ⚠", fg=THEME["danger"])
        self.countdown_lbl.config(text="", fg=THEME["danger"])

        # Start sound on a daemon thread so it doesn't block the UI
        alarm_thread = threading.Thread(target=_play_alarm, daemon=True)
        alarm_thread.start()

        self._flash()  # begin visual flash loop

    # ─────────────────────────────────────────────────────────
    #  Visual flash loop while alarm is ringing
    # ─────────────────────────────────────────────────────────
    def _flash(self):
        """Alternates the panel background colour to grab attention."""
        global alarm_active
        if not alarm_active:
            return

        self._flash_on = not self._flash_on
        colour = THEME["danger"] if self._flash_on else THEME["panel_inner"]

        for w in (self.panel.content,
                  self.live_time_lbl, self.live_date_lbl,
                  self.status_lbl, self.countdown_lbl):
            w.config(bg=colour)

        self.root.after(500, self._flash)   # repeat every 500 ms

    # ─────────────────────────────────────────────────────────
    #  Main tick — runs every second
    # ─────────────────────────────────────────────────────────
    def _tick(self):
        """Updates the live clock and the countdown display once per second."""
        global alarm_active

        now = datetime.datetime.now()

        # Update live clock
        self.live_time_lbl.config(text=now.strftime("%I:%M:%S %p"))
        self.live_date_lbl.config(text=now.strftime("%A, %B %d  %Y"))

        # Countdown logic
        if self.alarm_set and self.alarm_time is not None and not alarm_active:
            remaining = self.alarm_time - now

            if remaining.total_seconds() <= 0:
                # Time to ring!
                self.alarm_set = False
                self._trigger_alarm()
            else:
                # Format remaining as  HH:MM:SS
                total_secs = int(remaining.total_seconds())
                hh  = total_secs // 3600
                mm  = (total_secs % 3600) // 60
                ss  = total_secs % 60
                self.countdown_lbl.config(
                    text=f"RINGS IN  {hh:02d}:{mm:02d}:{ss:02d}",
                    fg=THEME["accent"]
                )

        self.root.after(1000, self._tick)   # schedule next tick in 1 second

# ── Entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = AlarmClockApp(root)
    root.mainloop()