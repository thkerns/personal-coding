# Combined Daily Task Manager + Digital Clock/Calendar (HUD Theme)
# FIXES:
# - Top panel gets enough height so the FULL calendar is visible (like original)
# - Bottom Goals section remains scrollable
# - Fonts/sizes kept the same as your original scripts

import os
import json
import calendar
import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

calendar.setfirstweekday(calendar.SUNDAY)
TASKS_FILE = "tasks.json"

THEME = {
    "bg": "#0e1621",
    "panel_outer": "#101c2a",
    "panel_inner": "#182636",
    "stroke_dark": "#0a111a",
    "stroke_mid": "#2a3c52",
    "stroke_light": "#47647f",
    "accent": "#6fb3c8",
    "text": "#dce8f2",
    "muted": "#9fb4c6",
    "danger": "#ff5a5a",
    "ok": "#44ff99",
    "btn_bg": "#1a2a3c",
    "btn_bg_hover": "#22384f",
    "row_bg": "#162536",
    "row_bg_alt": "#142231",
    "cell_bg": "#162536",
    "cell_bg_alt": "#142231",
}

def _on_hover(btn, normal_bg, hover_bg):
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.configure(bg=normal_bg))

def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)

def get_today():
    return datetime.date.today().isoformat()

class HudPanel(tk.Canvas):
    """
    Canvas HUD panel; a normal Tk Frame (self.content) sits inside it.
    """
    def __init__(self, master, width=700, height=620, padding=22, **kwargs):
        super().__init__(
            master,
            width=width,
            height=height,
            bg=THEME["bg"],
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.padding = padding
        self._cw = width
        self._ch = height

        self.content = tk.Frame(self, bg=THEME["panel_inner"])
        self._content_window = self.create_window(
            padding, padding,
            anchor="nw",
            window=self.content,
            width=width - 2 * padding,
            height=height - 2 * padding
        )

        self.bind("<Configure>", self._redraw)
        self._redraw()

    def _redraw(self, event=None):
        w = event.width if event else self._cw
        h = event.height if event else self._ch
        self._cw, self._ch = w, h

        pad = self.padding
        inner_w = max(10, w - 2 * pad)
        inner_h = max(10, h - 2 * pad)
        self.itemconfig(self._content_window, width=inner_w, height=inner_h)

        self.delete("hud")

        self.create_rectangle(
            pad - 10, pad - 10, w - (pad - 10), h - (pad - 10),
            fill=THEME["panel_outer"],
            outline=THEME["stroke_dark"],
            width=2,
            tags="hud"
        )
        self.create_rectangle(
            pad, pad, w - pad, h - pad,
            fill=THEME["panel_inner"],
            outline=THEME["stroke_mid"],
            width=2,
            tags="hud"
        )

        self.create_line(
            pad + 16, pad + 10, w - pad - 90, pad + 10,
            fill=THEME["accent"],
            width=2,
            tags="hud"
        )
        self.create_rectangle(
            w - pad - 88, pad + 4, w - pad - 14, pad + 16,
            fill=THEME["panel_inner"],
            outline=THEME["accent"],
            width=2,
            tags="hud"
        )

        corner = 18
        self.create_line(pad, pad + corner, pad, pad, pad + corner, pad,
                         fill=THEME["stroke_light"], width=2, tags="hud")
        self.create_line(w - pad - corner, pad, w - pad, pad, w - pad, pad + corner,
                         fill=THEME["stroke_light"], width=2, tags="hud")
        self.create_line(pad, h - pad - corner, pad, h - pad, pad + corner, h - pad,
                         fill=THEME["stroke_light"], width=2, tags="hud")
        self.create_line(w - pad - corner, h - pad, w - pad, h - pad, w - pad, h - pad - corner,
                         fill=THEME["stroke_light"], width=2, tags="hud")

class ScrollableFrame(tk.Frame):
    """
    A frame with a vertical scrollbar. Put children inside `self.inner`.
    """
    def __init__(self, master, bg, *args, **kwargs):
        super().__init__(master, bg=bg, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=bg)
        self._window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self._bind_mousewheel(self.canvas)

    def _on_inner_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self._window_id, width=event.width)

    def _bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self._on_mousewheel)
        widget.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        widget.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_mousewheel(self, event):
        direction = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(direction, "units")

class TaskManagerApp:
    def __init__(self, content_frame):
        self.content = content_frame
        self.root = content_frame.winfo_toplevel()

        self.tasks = load_tasks()
        self.today = get_today()

        self.header_frame = tk.Frame(self.content, bg=THEME["panel_inner"])
        self.header_frame.pack(fill=tk.X, padx=14, pady=(12, 8))

        # (kept original font/size)
        self.title_label = tk.Label(
            self.header_frame,
            text="GOALS",
            font=("Arial", 18, "bold"),
            fg=THEME["text"],
            bg=THEME["panel_inner"]
        )
        self.title_label.pack(side=tk.LEFT)

        self.subtitle = tk.Label(
            self.header_frame,
            text=f"{self.today}",
            font=("Arial", 10, "bold"),
            fg=THEME["muted"],
            bg=THEME["panel_inner"]
        )
        self.subtitle.pack(side=tk.RIGHT)

        self.tasks_container = tk.Frame(self.content, bg=THEME["panel_inner"])
        self.tasks_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))

        self.scroll = ScrollableFrame(self.tasks_container, bg=THEME["panel_inner"])
        self.scroll.pack(fill=tk.BOTH, expand=True)

        self.buttons_frame = tk.Frame(self.content, bg=THEME["panel_inner"])
        self.buttons_frame.pack(fill=tk.X, padx=14, pady=(0, 14))

        self.add_button = tk.Button(
            self.buttons_frame, text="Add a Task",
            bg=THEME["btn_bg"], fg=THEME["text"],
            activebackground=THEME["btn_bg_hover"], activeforeground=THEME["text"],
            font=("Arial", 10, "bold"),
            bd=0, highlightthickness=1,
            highlightbackground=THEME["stroke_mid"], highlightcolor=THEME["accent"],
            padx=14, pady=8,
            command=self.add_task
        )
        self.add_button.pack(side=tk.LEFT, padx=(0, 8))
        _on_hover(self.add_button, THEME["btn_bg"], THEME["btn_bg_hover"])

        self.remove_button = tk.Button(
            self.buttons_frame, text="Remove a Task",
            bg=THEME["btn_bg"], fg=THEME["text"],
            activebackground=THEME["btn_bg_hover"], activeforeground=THEME["text"],
            font=("Arial", 10, "bold"),
            bd=0, highlightthickness=1,
            highlightbackground=THEME["stroke_mid"], highlightcolor=THEME["accent"],
            padx=14, pady=8,
            command=self.remove_task
        )
        self.remove_button.pack(side=tk.LEFT, padx=8)
        _on_hover(self.remove_button, THEME["btn_bg"], THEME["btn_bg_hover"])

        self.exit_button = tk.Button(
            self.buttons_frame, text="Exit",
            bg=THEME["btn_bg"], fg=THEME["text"],
            activebackground=THEME["btn_bg_hover"], activeforeground=THEME["text"],
            font=("Arial", 10, "bold"),
            bd=0, highlightthickness=1,
            highlightbackground=THEME["stroke_mid"], highlightcolor=THEME["accent"],
            padx=14, pady=8,
            command=self.exit_app
        )
        self.exit_button.pack(side=tk.RIGHT)
        _on_hover(self.exit_button, THEME["btn_bg"], THEME["btn_bg_hover"])

        self.save_button = tk.Button(
            self.buttons_frame, text="Save",
            bg=THEME["btn_bg"], fg=THEME["text"],
            activebackground=THEME["btn_bg_hover"], activeforeground=THEME["text"],
            font=("Arial", 10, "bold"),
            bd=0, highlightthickness=1,
            highlightbackground=THEME["stroke_mid"], highlightcolor=THEME["accent"],
            padx=14, pady=8,
            command=self.save
        )
        self.save_button.pack(side=tk.RIGHT, padx=(0, 8))
        _on_hover(self.save_button, THEME["btn_bg"], THEME["btn_bg_hover"])

        self.display_tasks()

    def display_tasks(self):
        for widget in self.scroll.inner.winfo_children():
            widget.destroy()

        section_title = tk.Label(
            self.scroll.inner,
            text="DAILY OBJECTIVES",
            fg=THEME["muted"],
            bg=THEME["panel_inner"],
            font=("Arial", 10, "bold")
        )
        section_title.pack(anchor="w", pady=(2, 8))

        if self.today not in self.tasks or not self.tasks[self.today]:
            tk.Label(
                self.scroll.inner,
                text="No tasks.",
                fg=THEME["text"],
                bg=THEME["panel_inner"],
                font=("Arial", 12)
            ).pack(pady=14)
            return

        for i, task in enumerate(self.tasks[self.today]):
            row_bg = THEME["row_bg"] if i % 2 == 0 else THEME["row_bg_alt"]

            task_frame = tk.Frame(
                self.scroll.inner,
                bg=row_bg,
                bd=0,
                highlightthickness=1,
                highlightbackground=THEME["stroke_mid"]
            )
            task_frame.pack(fill=tk.X, pady=4)

            status = task.get("status", "pending")
            if status == "completed":
                box_text, box_color = "[✓]", THEME["ok"]
            elif status == "failed":
                box_text, box_color = "[X]", THEME["danger"]
            else:
                box_text, box_color = "[ ]", THEME["text"]

            status_button = tk.Button(
                task_frame,
                text=box_text,
                fg=box_color,
                bg=row_bg,
                activebackground=row_bg,
                activeforeground=box_color,
                font=("Consolas", 16, "bold"),
                bd=0,
                padx=12,
                pady=10,
                command=lambda idx=i: self.toggle_status(idx)
            )
            status_button.pack(side=tk.LEFT)

            desc_label = tk.Label(
                task_frame,
                text=task.get("description", ""),
                fg=THEME["text"],
                bg=row_bg,
                font=("Arial", 12),
                anchor="w",
                padx=8,
                pady=10
            )
            desc_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def toggle_status(self, index):
        if self.today in self.tasks and 0 <= index < len(self.tasks[self.today]):
            current_status = self.tasks[self.today][index].get("status", "pending")
            if current_status == "pending":
                self.tasks[self.today][index]["status"] = "completed"
            elif current_status == "completed":
                self.tasks[self.today][index]["status"] = "failed"
            else:
                self.tasks[self.today][index]["status"] = "pending"
            self.display_tasks()

    def add_task(self):
        desc = simpledialog.askstring("Add Task", "Enter task description:")
        if desc and desc.strip() and desc.lower() != "cancel":
            if self.today not in self.tasks:
                self.tasks[self.today] = []
            self.tasks[self.today].append({"description": desc.strip(), "status": "pending"})
            self.display_tasks()

    def remove_task(self):
        if self.today not in self.tasks or not self.tasks[self.today]:
            messagebox.showinfo("No Tasks", "No tasks to remove.")
            return

        try:
            index = simpledialog.askinteger(
                "Remove Task",
                f"Enter task number to remove (1-{len(self.tasks[self.today])}):"
            )
            if index is not None and 1 <= index <= len(self.tasks[self.today]):
                removed_task = self.tasks[self.today].pop(index - 1)
                self.display_tasks()
                messagebox.showinfo("Removed", f"Task removed: {removed_task.get('description','')}")
            else:
                messagebox.showerror("Invalid", "Invalid task number.")
        except Exception:
            messagebox.showerror("Error", "Invalid input.")

    def save(self):
        save_tasks(self.tasks)

    def exit_app(self):
        self.root.quit()

class CombinedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily HUD - Clock + Tasks")
        # Give it enough height so the calendar is fully visible like original
        self.root.geometry("700x1200")
        self.root.minsize(640, 950)
        self.root.configure(bg=THEME["bg"])

        now = datetime.datetime.now()
        self.current_year = now.year
        self.current_month = now.month

        # PanedWindow lets the top keep the space it needs, bottom stays scrollable.
        self.paned = tk.PanedWindow(
            root,
            orient=tk.VERTICAL,
            bg=THEME["bg"],
            sashrelief=tk.FLAT,
            showhandle=False,
            bd=0
        )
        self.paned.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        # Top: Clock/Calendar panel (match original clock panel height ~620)
        self.clock_panel = HudPanel(self.paned, width=700, height=620, padding=22)
        self._build_clock_calendar(self.clock_panel.content)

        # Bottom: Task panel (scroll handles overflow)
        self.tasks_panel = HudPanel(self.paned, width=700, height=480, padding=22)
        self.tasks_app = TaskManagerApp(self.tasks_panel.content)

        # Add to paned with initial sizes (so full calendar shows)
        self.paned.add(self.clock_panel, minsize=620)
        self.paned.add(self.tasks_panel, minsize=260)

        # ---- FORCE initial split so the full calendar is visible on launch ----
        self.root.update_idletasks()

        # Put the divider BELOW the clock/calendar panel.
        # Tweak this number if you want slightly more/less calendar space.
        desired_top_height = 705

        # Sash index 0 = divider between pane 0 and pane 1
        self.paned.sash_place(0, 0, desired_top_height)

        # Start loops
        self.update_calendar()
        self.update_clock()

    def update_clock(self):
        now = datetime.datetime.now()
        self.time_label.config(text=now.strftime("%I:%M:%S %p"))
        self.date_label.config(text=now.strftime("%B %d, %Y"))
        self.day_label.config(text=now.strftime("%A"))
        self.root.after(1000, self.update_clock)

    # -------- Calendar --------
    def prev_month(self):
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()

    def update_calendar(self):
        self.month_year_label.config(text=f"{calendar.month_name[self.current_month]} {self.current_year}")

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        now = datetime.datetime.now()

        for week_idx in range(6):
            for day_idx in range(7):
                if week_idx < len(cal) and cal[week_idx][day_idx] != 0:
                    day_num = cal[week_idx][day_idx]
                    text = str(day_num)
                    is_today = (
                        day_num == now.day and
                        self.current_month == now.month and
                        self.current_year == now.year
                    )
                    fg = THEME["ok"] if is_today else THEME["accent"]
                else:
                    text = ""
                    fg = THEME["muted"]

                self.day_grid[week_idx][day_idx].config(text=text, fg=fg)

    def _build_clock_calendar(self, content):
        # Header (kept original font/size)
        header = tk.Frame(content, bg=THEME["panel_inner"])
        header.pack(fill=tk.X, padx=14, pady=(14, 6))

        title = tk.Label(
            header,
            text="CLOCK",
            font=("Arial", 16, "bold"),
            fg=THEME["muted"],
            bg=THEME["panel_inner"]
        )
        title.pack(side=tk.LEFT)

        # Time label (kept original)
        self.time_label = tk.Label(
            content,
            font=("Courier", 52, "bold"),
            fg=THEME["ok"],
            bg=THEME["panel_inner"]
        )
        self.time_label.pack(pady=(6, 6))

        self.day_label = tk.Label(
            content,
            font=("Arial", 20, "bold"),
            fg=THEME["accent"],
            bg=THEME["panel_inner"]
        )
        self.day_label.pack()

        self.date_label = tk.Label(
            content,
            font=("Arial", 18),
            fg=THEME["text"],
            bg=THEME["panel_inner"]
        )
        self.date_label.pack(pady=(0, 12))

        divider = tk.Frame(content, bg=THEME["stroke_mid"], height=1)
        divider.pack(fill=tk.X, padx=14, pady=(4, 12))

        # Calendar container (expand so grid gets full space)
        cal_container = tk.Frame(content, bg=THEME["panel_inner"])
        cal_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

        nav_row = tk.Frame(cal_container, bg=THEME["panel_inner"])
        nav_row.pack(fill=tk.X, pady=(0, 10))

        prev_button = tk.Button(
            nav_row,
            text="<",
            command=self.prev_month,
            font=("Arial", 14, "bold"),
            fg=THEME["text"],
            bg=THEME["btn_bg"],
            activebackground=THEME["btn_bg_hover"],
            activeforeground=THEME["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=THEME["stroke_mid"],
            highlightcolor=THEME["accent"],
            padx=14,
            pady=8
        )
        prev_button.pack(side=tk.LEFT)
        _on_hover(prev_button, THEME["btn_bg"], THEME["btn_bg_hover"])

        self.month_year_label = tk.Label(
            nav_row,
            font=("Arial", 16, "bold"),
            fg=THEME["text"],
            bg=THEME["panel_inner"]
        )
        self.month_year_label.pack(side=tk.LEFT, expand=True)

        next_button = tk.Button(
            nav_row,
            text=">",
            command=self.next_month,
            font=("Arial", 14, "bold"),
            fg=THEME["text"],
            bg=THEME["btn_bg"],
            activebackground=THEME["btn_bg_hover"],
            activeforeground=THEME["text"],
            bd=0,
            highlightthickness=1,
            highlightbackground=THEME["stroke_mid"],
            highlightcolor=THEME["accent"],
            padx=14,
            pady=8
        )
        next_button.pack(side=tk.RIGHT)
        _on_hover(next_button, THEME["btn_bg"], THEME["btn_bg_hover"])

        # Grid frame MUST expand so calendar is fully visible
        grid_frame = tk.Frame(cal_container, bg=THEME["panel_inner"])
        grid_frame.pack(fill=tk.BOTH, expand=True)

        for c in range(7):
            grid_frame.grid_columnconfigure(c, weight=1, uniform="cal")

        days = ["S", "M", "T", "W", "Th", "F", "S"]
        for day_idx, d in enumerate(days):
            hdr = tk.Label(
                grid_frame,
                text=d,
                font=("Arial", 11, "bold"),
                fg=THEME["muted"],
                bg=THEME["panel_inner"],
                width=4,
                pady=6
            )
            hdr.grid(row=0, column=day_idx, padx=2, pady=(0, 6), sticky="nsew")

        # Calendar cells (exactly like your original)
        self.day_grid = []
        for week_idx in range(6):
            week = []
            for day_idx in range(7):
                bg = THEME["cell_bg"] if (week_idx + day_idx) % 2 == 0 else THEME["cell_bg_alt"]
                lbl = tk.Label(
                    grid_frame,
                    text="",
                    font=("Arial", 12, "bold"),
                    fg=THEME["accent"],
                    bg=bg,
                    width=4,
                    height=2,
                    highlightthickness=1,
                    highlightbackground=THEME["stroke_mid"]
                )
                lbl.grid(row=week_idx + 1, column=day_idx, padx=2, pady=2, sticky="nsew")
                week.append(lbl)
            self.day_grid.append(week)
#-------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CombinedApp(root)
    root.mainloop()
