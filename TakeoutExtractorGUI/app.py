# ══════════════════════════════════════════════════════════════════
#  BOOTSTRAP  —  auto-install missing packages before app starts
# ══════════════════════════════════════════════════════════════════
import sys
import subprocess
import importlib.metadata
from pathlib import Path as _Path

def _bootstrap():
    """Read requirements.txt and pip-install anything that is missing."""

    req_file = _Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        return  # nothing to do

    # Parse non-empty, non-comment lines
    raw_lines = req_file.read_text(encoding="utf-8").splitlines()
    packages = [
        ln.strip()
        for ln in raw_lines
        if ln.strip() and not ln.strip().startswith("#")
    ]
    if not packages:
        return  # requirements.txt is empty / all commented out

    # Determine which are missing
    def _is_installed(spec: str) -> bool:
        # Strip version qualifiers to get bare package name
        name = spec.split(">=")[0].split("==")[0].split("!=")[0].split("<")[0].strip()
        try:
            importlib.metadata.version(name)
            return True
        except importlib.metadata.PackageNotFoundError:
            return False

    missing = [p for p in packages if not _is_installed(p)]
    if not missing:
        return  # everything already installed

    # ── Show a small installer splash using tkinter (stdlib only)
    import tkinter as _tk
    import tkinter.ttk as _ttk
    import threading as _threading

    # Theme colours (same palette as main app)
    _BG   = "#1A0A0A"
    _PNL  = "#2B1111"
    _ACC  = "#DC143C"
    _BRD  = "#5C1A1A"
    _WHT  = "#FFFFFF"
    _GRY  = "#AAAAAA"

    splash = _tk.Tk()
    splash.title("Setting up…")
    splash.geometry("480x260")
    splash.resizable(False, False)
    splash.configure(bg=_BG)
    splash.overrideredirect(False)

    # Centre on screen
    splash.update_idletasks()
    sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
    splash.geometry(f"480x260+{(sw-480)//2}+{(sh-260)//2}")

    # ── Header
    hdr = _tk.Frame(splash, bg=_BG)
    hdr.pack(fill="x", padx=28, pady=(24, 0))
    _tk.Label(hdr, text="\U0001f352", bg=_BG,
              font=("Segoe UI Emoji", 22)).pack(side="left")
    col = _tk.Frame(hdr, bg=_BG)
    col.pack(side="left", padx=10)
    _tk.Label(col, text="Installing dependencies",
              bg=_BG, fg=_WHT,
              font=("Segoe UI", 14, "bold")).pack(anchor="w")
    _tk.Label(col, text="This only happens once",
              bg=_BG, fg="#CC6666",
              font=("Segoe UI", 10)).pack(anchor="w")

    _tk.Frame(splash, bg=_BRD, height=1).pack(fill="x", padx=28, pady=(14, 0))

    # ── Status label
    status_var = _tk.StringVar(value="Preparing…")
    _tk.Label(splash, textvariable=status_var,
              bg=_BG, fg=_GRY,
              font=("Consolas", 10)).pack(anchor="w", padx=28, pady=(14, 4))

    # ── Progress bar (ttk styled)
    style = _ttk.Style(splash)
    style.theme_use("clam")
    style.configure("Red.Horizontal.TProgressbar",
                    troughcolor=_BRD, background=_ACC,
                    bordercolor=_BRD, lightcolor=_ACC, darkcolor=_ACC)
    pb = _ttk.Progressbar(splash, style="Red.Horizontal.TProgressbar",
                          orient="horizontal", length=424,
                          mode="determinate", maximum=len(missing))
    pb.pack(padx=28)

    # ── Package list
    pkg_var = _tk.StringVar(value="")
    _tk.Label(splash, textvariable=pkg_var,
              bg=_BG, fg=_ACC,
              font=("Segoe UI", 10)).pack(anchor="w", padx=28, pady=(10, 0))

    error_store = []

    def _install_thread():
        for i, pkg in enumerate(missing):
            status_var.set(f"Installing {i+1} of {len(missing)}…")
            pkg_var.set(f"  \u2192  {pkg}")
            splash.update_idletasks()
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pkg,
                     "--quiet", "--disable-pip-version-check"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
            except subprocess.CalledProcessError as e:
                error_store.append(f"{pkg}: {e}")
            pb.step(1)
            splash.update_idletasks()

        status_var.set("Done! Launching app…" if not error_store else
                       f"Finished with {len(error_store)} error(s). Check log.")
        pkg_var.set("")
        splash.update_idletasks()
        splash.after(900, splash.destroy)

    t = _threading.Thread(target=_install_thread, daemon=True)
    t.start()
    splash.mainloop()
    t.join(timeout=5)

    if error_store:
        import tkinter.messagebox as _mb
        _root = _tk.Tk()
        _root.withdraw()
        _mb.showerror(
            "Install Error",
            "Some packages could not be installed:\n\n" + "\n".join(error_store)
        )
        _root.destroy()

_bootstrap()

# ══════════════════════════════════════════════════════════════════
#  MAIN APP IMPORTS  (all packages are guaranteed installed above)
# ══════════════════════════════════════════════════════════════════
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import zipfile
import threading
import os
import time
from pathlib import Path

# ─────────────────────────────────────────────
#  THEME CONSTANTS  (Cherry-Red / Apple-like)
# ─────────────────────────────────────────────
BG_DARK        = "#1A0A0A"   # near-black with red tint
BG_PANEL       = "#2B1111"   # deep wine panel
BG_CARD        = "#3D1515"   # card surface
ACCENT         = "#DC143C"   # crimson / cherry red
ACCENT_HOVER   = "#FF2952"   # lighter red on hover
ACCENT_DARK    = "#8B0000"   # dark red for pressed
SUCCESS        = "#4CAF50"
WARNING        = "#FF9800"
ERROR_COL      = "#FF5252"
TEXT_WHITE     = "#FFFFFF"
TEXT_MUTED     = "#B07575"   # muted pinkish-grey
TEXT_LABEL     = "#FFCCCC"   # soft pinkish label
BORDER         = "#5C1A1A"
RADIUS         = 12


class RoundedButton(tk.Canvas):
    """A canvas-based button with rounded corners and hover animation."""

    def __init__(self, parent, text, command=None, width=160, height=44,
                 bg=ACCENT, hover_bg=ACCENT_HOVER, fg=TEXT_WHITE,
                 font=("Segoe UI", 11, "bold"), radius=RADIUS, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=parent.cget("bg") if hasattr(parent, "cget") else BG_DARK,
                         highlightthickness=0, **kw)
        self._bg = bg
        self._hover_bg = hover_bg
        self._fg = fg
        self._text = text
        self._command = command
        self._radius = radius
        self._font = font
        self._width = width
        self._height = height
        self._draw(self._bg)
        self.bind("<Enter>", lambda e: self._animate(self._hover_bg))
        self.bind("<Leave>", lambda e: self._animate(self._bg))
        self.bind("<ButtonPress-1>", lambda e: self._animate(ACCENT_DARK))
        self.bind("<ButtonRelease-1>", self._on_click)

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1,
            x2, y1, x2, y1+r,
            x2, y2-r, x2, y2,
            x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r,
            x1, y1+r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self, color):
        self.delete("all")
        self._round_rect(2, 2, self._width-2, self._height-2,
                         self._radius, fill=color, outline=color)
        self.create_text(self._width//2, self._height//2,
                         text=self._text, fill=self._fg,
                         font=self._font)

    def _animate(self, color):
        self._draw(color)

    def _on_click(self, event):
        self._animate(self._hover_bg)
        if self._command:
            self._command()

    def configure_text(self, text):
        self._text = text
        self._draw(self._bg)

    def set_state(self, state):
        if state == "disabled":
            self._bg = "#5C1A1A"
            self._hover_bg = "#5C1A1A"
        else:
            self._bg = ACCENT
            self._hover_bg = ACCENT_HOVER
        self._draw(self._bg)


class PathRow(tk.Frame):
    """Labeled path selector row with a directory field and Browse button."""

    def __init__(self, parent, label, placeholder, **kw):
        super().__init__(parent, bg=BG_PANEL, **kw)
        if label:
            tk.Label(self, text=label, bg=BG_PANEL, fg=TEXT_LABEL,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 4))

        row = tk.Frame(self, bg=BG_PANEL)
        row.pack(fill="x")

        self.var = tk.StringVar()
        self.entry = tk.Entry(row, textvariable=self.var, bg=BG_CARD,
                              fg="#888888", insertbackground=TEXT_WHITE,
                              relief="flat", font=("Consolas", 11),
                              bd=0, highlightthickness=2,
                              highlightbackground=BORDER,
                              highlightcolor=ACCENT)
        self.entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))
        self.entry.insert(0, placeholder)
        self._placeholder = placeholder
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)

        self.btn = RoundedButton(row, text="Browse  \U0001f4c1", command=self._browse,
                                 width=130, height=40,
                                 bg=BG_CARD, hover_bg=ACCENT)
        self.btn.pack(side="left")

    def _clear_placeholder(self, _):
        if self.entry.get() == self._placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg=TEXT_WHITE)

    def _restore_placeholder(self, _):
        if not self.entry.get().strip():
            self.entry.insert(0, self._placeholder)
            self.entry.config(fg="#888888")

    def _browse(self):
        path = filedialog.askdirectory(title="Select Folder")
        if path:
            self.var.set(path)
            self.entry.config(fg=TEXT_WHITE)

    def get(self):
        val = self.var.get().strip()
        return val if val != self._placeholder else ""


class FileListFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_PANEL, **kw)
        hdr = tk.Frame(self, bg=BG_PANEL)
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text="\U0001f4e6  Discovered ZIP Files", bg=BG_PANEL,
                 fg=TEXT_LABEL, font=("Segoe UI", 11, "bold")).pack(side="left")
        self.count_lbl = tk.Label(hdr, text="", bg=BG_PANEL,
                                  fg=ACCENT, font=("Segoe UI", 11, "bold"))
        self.count_lbl.pack(side="right")

        container = tk.Frame(self, bg=BG_CARD, bd=0,
                             highlightthickness=1, highlightbackground=BORDER)
        container.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical",
                                 bg=BG_PANEL, troughcolor=BG_DARK,
                                 activebackground=ACCENT)
        self.listbox = tk.Listbox(container, bg=BG_CARD, fg=TEXT_WHITE,
                                  selectbackground=ACCENT,
                                  selectforeground=TEXT_WHITE,
                                  relief="flat", bd=0,
                                  font=("Consolas", 10),
                                  activestyle="none",
                                  yscrollcommand=scrollbar.set,
                                  highlightthickness=0)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(fill="both", expand=True, padx=4, pady=4)

    def populate(self, files):
        self.listbox.delete(0, "end")
        for f in files:
            self.listbox.insert("end", f"  {f}")
        n = len(files)
        self.count_lbl.config(text=f"{n} file{'s' if n != 1 else ''} found")


class LogFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_PANEL, **kw)
        tk.Label(self, text="\U0001f4cb  Extraction Log", bg=BG_PANEL,
                 fg=TEXT_LABEL, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))

        container = tk.Frame(self, bg=BG_CARD, highlightthickness=1,
                             highlightbackground=BORDER)
        container.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical",
                                 bg=BG_PANEL, troughcolor=BG_DARK,
                                 activebackground=ACCENT)
        self.text = tk.Text(container, bg=BG_CARD, fg=TEXT_WHITE,
                            relief="flat", bd=0,
                            font=("Consolas", 10),
                            state="disabled", wrap="word",
                            yscrollcommand=scrollbar.set,
                            highlightthickness=0,
                            insertbackground=TEXT_WHITE)
        scrollbar.config(command=self.text.yview)
        scrollbar.pack(side="right", fill="y")
        self.text.pack(fill="both", expand=True, padx=6, pady=6)

        self.text.tag_config("success", foreground=SUCCESS)
        self.text.tag_config("error",   foreground=ERROR_COL)
        self.text.tag_config("warn",    foreground=WARNING)
        self.text.tag_config("info",    foreground="#AAAAAA")
        self.text.tag_config("accent",  foreground=ACCENT)
        self.text.tag_config("header",  foreground=ACCENT,
                             font=("Segoe UI", 11, "bold"))

    def log(self, msg, tag="info"):
        self.text.config(state="normal")
        self.text.insert("end", msg + "\n", tag)
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")


class ProgressBar(tk.Canvas):
    def __init__(self, parent, width=400, height=12, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=BG_PANEL, highlightthickness=0, **kw)
        self._width = width
        self._height = height
        self._draw(0)

    def _pill(self, x1, y1, x2, y2, r, **kw):
        w = max(x2 - x1, 1)
        r = min(r, w // 2, (y2 - y1) // 2)
        if r < 1:
            return self.create_rectangle(x1, y1, x2, y2, **kw)
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
                  x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
                  x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(points, smooth=True, **kw)

    def _draw(self, pct):
        self.delete("all")
        self._pill(0, 0, self._width, self._height, self._height // 2,
                   fill=BORDER, outline=BORDER)
        filled = int(self._width * pct / 100)
        if filled > 0:
            self._pill(0, 0, filled, self._height, self._height // 2,
                       fill=ACCENT, outline=ACCENT)

    def set(self, pct):
        self._draw(max(0, min(100, pct)))


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class TakeoutExtractorApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Google Takeout Extractor")
        self.geometry("820x820")
        self.minsize(700, 680)
        self.resizable(True, True)
        self.config(bg=BG_DARK)
        self._center()
        self._zip_files = []
        self._running = False
        self._stop_flag = False
        self._build_ui()

    def _center(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = 820, 820
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self, bg=BG_DARK)
        title_frame.pack(fill="x", padx=32, pady=(28, 0))

        tk.Label(title_frame, text="\U0001f352", bg=BG_DARK,
                 font=("Segoe UI Emoji", 28)).pack(side="left")
        title_col = tk.Frame(title_frame, bg=BG_DARK)
        title_col.pack(side="left", padx=(12, 0))
        tk.Label(title_col, text="Takeout Extractor",
                 bg=BG_DARK, fg=TEXT_WHITE,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(title_col, text="Merge your Google Takeout ZIP files effortlessly",
                 bg=BG_DARK, fg="#CC6666",
                 font=("Segoe UI", 10)).pack(anchor="w")

        # Divider
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=32, pady=(16, 0))

        # Scrollable main area using canvas
        canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        vsb = tk.Scrollbar(self, orient="vertical", command=canvas.yview,
                           bg=BG_DARK, troughcolor=BG_DARK, activebackground=ACCENT)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.main_frame = tk.Frame(canvas, bg=BG_DARK)
        self._canvas_window = canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(self._canvas_window, width=event.width)

        self.main_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", _on_configure)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        outer = self.main_frame
        pad_frame = tk.Frame(outer, bg=BG_DARK)
        pad_frame.pack(fill="both", expand=True, padx=32, pady=16)

        # SOURCE card
        src_inner = self._card(pad_frame, "\U0001f4c2  Source Folder")
        self.src_row = PathRow(src_inner, label="",
                               placeholder="Select folder containing takeout-*.zip files")
        self.src_row.pack(fill="x")

        scan_row = tk.Frame(src_inner, bg=BG_PANEL)
        scan_row.pack(fill="x", pady=(10, 0))
        self.scan_btn = RoundedButton(scan_row, text="\U0001f50d  Scan for ZIPs",
                                      command=self._scan,
                                      width=170, height=40,
                                      bg=BG_CARD, hover_bg=ACCENT)
        self.scan_btn.pack(side="left")
        self.scan_status = tk.Label(scan_row, text="", bg=BG_PANEL,
                                    fg="#888888", font=("Segoe UI", 10))
        self.scan_status.pack(side="left", padx=14)

        # File list card
        list_inner = self._card(pad_frame, "\U0001f4e6  Discovered ZIP Files")
        self.file_list = FileListFrame(list_inner)
        self.file_list.pack(fill="both", expand=True)

        # DESTINATION card
        dst_inner = self._card(pad_frame, "\U0001f4c1  Destination Folder")
        self.dst_row = PathRow(dst_inner, label="",
                               placeholder="Select where to extract all files")
        self.dst_row.pack(fill="x")

        # PROGRESS card
        prog_inner = self._card(pad_frame, "\u26a1  Progress")
        self.prog_label = tk.Label(prog_inner, text="Ready",
                                   bg=BG_PANEL, fg="#888888",
                                   font=("Segoe UI", 10))
        self.prog_label.pack(anchor="w", pady=(0, 8))
        self.progress = ProgressBar(prog_inner, height=14)
        self.progress.pack(fill="x")

        pct_row = tk.Frame(prog_inner, bg=BG_PANEL)
        pct_row.pack(fill="x", pady=(6, 0))
        self.eta_label = tk.Label(pct_row, text="",
                                  bg=BG_PANEL, fg="#888888",
                                  font=("Segoe UI", 10))
        self.eta_label.pack(side="left")
        self.pct_label = tk.Label(pct_row, text="0%",
                                  bg=BG_PANEL, fg=ACCENT,
                                  font=("Segoe UI", 10, "bold"))
        self.pct_label.pack(side="right")

        # LOG card
        log_inner = self._card(pad_frame, "")
        self.log_frame = LogFrame(log_inner)
        self.log_frame.pack(fill="both", expand=True)

        # Action buttons (outside scroll area)
        btn_row = tk.Frame(self, bg=BG_DARK)
        btn_row.pack(fill="x", padx=32, pady=(8, 20))

        self.clear_btn = RoundedButton(btn_row, text="\U0001f5d1  Clear Log",
                                       command=self._clear_log,
                                       width=140, height=44,
                                       bg=BG_CARD, hover_bg="#5C1A1A")
        self.clear_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = RoundedButton(btn_row, text="\u23f9  Stop",
                                      command=self._stop_extraction,
                                      width=110, height=44,
                                      bg="#5C1A1A", hover_bg=ERROR_COL)
        self.stop_btn.pack(side="right", padx=(10, 0))

        self.extract_btn = RoundedButton(btn_row, text="\u26a1  Extract All",
                                         command=self._start_extraction,
                                         width=160, height=44)
        self.extract_btn.pack(side="right")

    def _card(self, parent, title):
        outer = tk.Frame(parent, bg=BG_PANEL, bd=0,
                         highlightthickness=1, highlightbackground=BORDER)
        outer.pack(fill="x", pady=(0, 14))
        inner = tk.Frame(outer, bg=BG_PANEL)
        inner.pack(fill="both", expand=True, padx=18, pady=14)
        if title:
            tk.Label(inner, text=title, bg=BG_PANEL, fg=TEXT_WHITE,
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        return inner

    # ── SCAN ──────────────────────────────────
    def _scan(self):
        src = self.src_row.get()
        if not src:
            messagebox.showwarning("No Source Folder",
                                   "Please select a source folder first.")
            return
        path = Path(src)
        if not path.is_dir():
            messagebox.showerror("Invalid Folder",
                                 f"The folder does not exist:\n{src}")
            return

        zips = sorted(path.glob("takeout-*.zip"))
        self._zip_files = zips
        names = [z.name for z in zips]
        self.file_list.populate(names)

        if zips:
            self.scan_status.config(text=f"\u2713 {len(zips)} file(s) ready", fg=SUCCESS)
            self.log_frame.log(
                f"[Scan] Found {len(zips)} ZIP file(s) in:\n  {src}", "accent")
        else:
            self.scan_status.config(text="No takeout-*.zip found", fg=WARNING)
            self.log_frame.log(
                "[Scan] No takeout-*.zip files found in the selected folder.", "warn")

    # ── EXTRACTION ────────────────────────────
    def _start_extraction(self):
        if self._running:
            messagebox.showinfo("Already Running", "Extraction is already in progress.")
            return
        if not self._zip_files:
            messagebox.showwarning("No ZIPs",
                                   "Please scan a source folder first to discover ZIP files.")
            return
        dst = self.dst_row.get()
        if not dst:
            messagebox.showwarning("No Destination",
                                   "Please select a destination folder.")
            return
        dst_path = Path(dst)
        try:
            dst_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            messagebox.showerror("Permission Error",
                                 f"Cannot create folder — permission denied:\n{dst}")
            return
        except Exception as e:
            messagebox.showerror("Destination Error",
                                 f"Cannot create destination folder:\n{e}")
            return

        self._running = True
        self._stop_flag = False
        self.extract_btn.set_state("disabled")
        self.log_frame.clear()
        self.progress.set(0)
        self.pct_label.config(text="0%")
        self.eta_label.config(text="")
        self.prog_label.config(text="Starting\u2026", fg=ACCENT)

        thread = threading.Thread(
            target=self._extract_worker,
            args=(list(self._zip_files), dst_path),
            daemon=True
        )
        thread.start()

    def _stop_extraction(self):
        if self._running:
            self._stop_flag = True
            self.prog_label.config(text="Stopping\u2026", fg=WARNING)
            self.log_frame.log("[Control] Stop requested by user.", "warn")

    def _extract_worker(self, zips, dst):
        total = len(zips)
        start_time = time.time()
        errors = 0

        self._log_ui(
            f"\u2501\u2501\u2501  Extraction Started  \u2501\u2501\u2501\n"
            f"  Source ZIPs : {total}\n"
            f"  Destination : {dst}\n", "header")

        for idx, zip_path in enumerate(zips, start=1):
            if self._stop_flag:
                self._log_ui(
                    f"\n[Stopped] Halted after {idx-1}/{total} files.", "warn")
                break

            pct = int((idx - 1) / total * 100)
            elapsed = time.time() - start_time
            rate = (idx - 1) / elapsed if elapsed > 0 and idx > 1 else 0
            remaining = (total - (idx - 1)) / rate if rate > 0 else 0
            eta_str = self._fmt_time(remaining) if idx > 1 else "Estimating\u2026"

            self._update_progress_ui(pct, idx, total, zip_path.name, eta_str)

            try:
                if not zipfile.is_zipfile(zip_path):
                    raise zipfile.BadZipFile("Not a valid ZIP file")
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(dst)
                self._log_ui(f"  \u2713  [{idx}/{total}]  {zip_path.name}", "success")

            except zipfile.BadZipFile:
                errors += 1
                self._log_ui(
                    f"  \u2717  [{idx}/{total}]  {zip_path.name}\n"
                    f"        \u21b3 Corrupted or incomplete ZIP.", "error")

            except PermissionError as e:
                errors += 1
                self._log_ui(
                    f"  \u2717  [{idx}/{total}]  {zip_path.name}\n"
                    f"        \u21b3 Permission denied: {e}", "error")

            except OSError as e:
                errors += 1
                self._log_ui(
                    f"  \u2717  [{idx}/{total}]  {zip_path.name}\n"
                    f"        \u21b3 OS Error: {e}", "error")

            except Exception as e:
                errors += 1
                self._log_ui(
                    f"  \u2717  [{idx}/{total}]  {zip_path.name}\n"
                    f"        \u21b3 Unexpected error: {e}", "error")

        elapsed_total = time.time() - start_time
        successful = total - errors
        stopped = self._stop_flag

        if not stopped:
            self._update_progress_ui(100, total, total, "Done!", "Complete")

        self._log_ui(
            f"\n\u2501\u2501\u2501  Summary  \u2501\u2501\u2501\n"
            f"  Total     : {total}\n"
            f"  Success   : {successful}\n"
            f"  Errors    : {errors}\n"
            f"  Time      : {self._fmt_time(elapsed_total)}\n"
            f"  Location  : {dst}\n"
            + ("\u2501\u2501\u2501  Complete \u2713  \u2501\u2501\u2501"
               if not stopped else "\u2501\u2501\u2501  Stopped \u26a0  \u2501\u2501\u2501"),
            "header" if not stopped else "warn"
        )

        self._running = False
        self.after(0, self.extract_btn.set_state, "normal")
        status_text = "Extraction complete \u2713" if not stopped else "Stopped by user"
        status_fg = SUCCESS if not stopped else WARNING
        self.after(0, lambda: self.prog_label.config(text=status_text, fg=status_fg))

        if not stopped and errors == 0:
            self.after(200, lambda: messagebox.showinfo(
                "Done!", f"All {total} ZIP files extracted successfully!\n\nLocation:\n{dst}"))
        elif not stopped and errors > 0:
            self.after(200, lambda: messagebox.showwarning(
                "Done with Errors",
                f"Extraction complete.\n\n"
                f"Success: {successful}/{total}\nErrors: {errors}\n\n"
                f"Check the log for details."))

    def _log_ui(self, msg, tag="info"):
        self.after(0, self.log_frame.log, msg, tag)

    def _update_progress_ui(self, pct, idx, total, filename, eta):
        def _do():
            self.progress.set(pct)
            self.pct_label.config(text=f"{pct}%")
            display_name = (filename[:58] + "\u2026") if len(filename) > 58 else filename
            self.prog_label.config(text=f"[{idx}/{total}]  {display_name}", fg=TEXT_WHITE)
            if eta:
                self.eta_label.config(text=f"ETA: {eta}")
        self.after(0, _do)

    @staticmethod
    def _fmt_time(seconds):
        s = int(seconds)
        if s < 60:
            return f"{s}s"
        m, s = divmod(s, 60)
        if m < 60:
            return f"{m}m {s}s"
        h, m = divmod(m, 60)
        return f"{h}h {m}m"

    def _clear_log(self):
        self.log_frame.clear()
        self.progress.set(0)
        self.pct_label.config(text="0%")
        self.eta_label.config(text="")
        self.prog_label.config(text="Ready", fg="#888888")


if __name__ == "__main__":
    app = TakeoutExtractorApp()
    app.mainloop()
