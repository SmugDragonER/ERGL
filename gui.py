"""
###########################################################################
#                                                                         #
#   AI-GENERATED GUI                                                      #
#   Written by an AI assistant (Claude) on request.                       #
#   It only calls the hand-written functions from main.py.                #
#                                                                         #
###########################################################################

Start from the project root:
    python gui.py
"""
import os
import subprocess
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from PIL import Image, ImageTk

from main import (create_mini_png, create_png, delete_tournament, import_csv, list_tournaments, load_games,
                  preview_png, set_headbooms, show_bans, show_standings)
from src.models import HEADBOOM_PENALTY
from src.paths import MAIN_LAYOUT_PATH, MINI_LAYOUT_PATH

# Available layouts (name shown in the preview -> file)
LAYOUTS = {
    "Main leaderboard": MAIN_LAYOUT_PATH,
    "Mini leaderboard": MINI_LAYOUT_PATH,
}

# --------------------------------------------------------------------------
# Colors (matching Leaderboard.png: dark, gold, red)
# --------------------------------------------------------------------------
BG = "#14161c"          # window background
CARD = "#1e212b"        # background of the "cards"
FIELD = "#2a2e3a"       # input fields / table rows
FIELD_ALT = "#242833"   # every second table row
HOVER = "#363b4a"
TEXT = "#e8e8ec"
MUTED = "#8a8f9c"
GOLD = "#ffd084"
RED = "#fd6160"

DEFAULT_TOURNAMENT = "EU_DOJO_NR_1"
PREVIEW_SIZE = (960, 540)      # preview = half of 1920x1080


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
def set_status(text, color=MUTED):
    status_label.config(text=text, foreground=color)


def get_tournament(warn=True):
    """Tournament name from the input field, or None (+ warning) if empty."""
    name = tournament.get().strip()
    if not name and warn:
        messagebox.showwarning("Tournament missing", "Please enter a tournament name first.")
    return name or None


def make_table(parent, columns):
    """Builds a table (Treeview) with a scrollbar.
    columns = list of (id, heading, width, anchor)."""
    frame = ttk.Frame(parent, style="Card.TFrame")
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show="headings", selectmode="browse")
    for col, title, width, anchor in columns:
        tree.heading(col, text=title, anchor=anchor)
        tree.column(col, width=width, anchor=anchor, stretch=(anchor == "w"))

    tree.tag_configure("even", background=FIELD)
    tree.tag_configure("odd", background=FIELD_ALT)
    tree.tag_configure("top3", foreground=GOLD)
    tree.tag_configure("checkpoint", foreground=RED)
    tree.tag_configure("penalty", foreground=RED)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return tree


def clear(tree):
    tree.delete(*tree.get_children())


# --------------------------------------------------------------------------
# Button functions
# --------------------------------------------------------------------------
def on_choose_folder():
    folder = filedialog.askdirectory(title="Choose the folder with the CSV files")
    if folder:                      # empty = user clicked "Cancel"
        csv_folder.set(folder)
        count = len(list(Path(folder).glob("*.csv")))
        set_status(f"Found {count} CSV file(s) in the folder.")


def on_choose_output():
    path = filedialog.asksaveasfilename(
        title="Save PNG as",
        defaultextension=".png",
        filetypes=[("PNG image", "*.png")],
        initialfile=f"{tournament.get().strip() or 'leaderboard'}.png",
    )
    if path:
        output_path.set(path)


def on_choose_mini_output():
    path = filedialog.asksaveasfilename(
        title="Save mini PNG as",
        defaultextension=".png",
        filetypes=[("PNG image", "*.png")],
        initialfile=f"{tournament.get().strip() or 'leaderboard'}_mini.png",
    )
    if path:
        mini_output_path.set(path)


def default_mini_path(main_path):
    """leaderboard.png -> leaderboard_mini.png (in the same folder)."""
    p = Path(main_path)
    return str(p.with_name(f"{p.stem}_mini{p.suffix}"))


def on_import():
    name = get_tournament()
    if name is None:
        return
    folder = csv_folder.get()
    if not folder:
        messagebox.showwarning("Folder missing", "Please choose a CSV folder first.")
        return

    csv_files = sorted(Path(folder).glob("*.csv"))
    if not csv_files:
        messagebox.showinfo("No CSVs", "There are no .csv files in this folder.")
        return

    new, skipped, errors = 0, 0, []
    for csv_file in csv_files:
        try:
            if import_csv(str(csv_file), name):
                new += 1
            else:
                skipped += 1
        except Exception as e:      # one broken CSV should not stop the whole import
            errors.append(f"{csv_file.name}: {e}")

    refresh_all()

    text = f"Import done: {new} new, {skipped} already saved"
    if errors:
        set_status(text + f", {len(errors)} error(s)", RED)
        messagebox.showerror("Import failed", "\n".join(errors))
    else:
        set_status(text + " ✓", GOLD)


def on_delete_tournament():
    name = get_tournament()
    if name is None:
        return
    if name not in list_tournaments():
        messagebox.showinfo("Not saved", f"There is no saved tournament called {name}.")
        return
    if not messagebox.askyesno(
            "Delete tournament",
            f"Delete tournament {name} and all its games?\n\n"
            "Manually entered headbooms are lost too. This cannot be undone.",
            icon="warning"):
        return

    try:
        delete_tournament(name)
    except Exception as e:
        messagebox.showerror("Could not delete", str(e))
        return

    remaining = list_tournaments()
    tournament.set(remaining[-1] if remaining else "")    # switch to another tournament (or empty)
    refresh_all()
    set_status(f"Tournament {name} deleted ✓", GOLD)


def on_create_png():
    name = get_tournament()
    if name is None:
        return
    if not output_path.get():
        on_choose_output()          # no target yet? Ask now
        if not output_path.get():
            return

    if not mini_output_path.get():  # no mini target? -> put it next to the main image
        mini_output_path.set(default_mini_path(output_path.get()))

    try:
        create_png(name, output_path.get())
        create_mini_png(name, mini_output_path.get())
    except Exception as e:
        messagebox.showerror("Could not create PNG", str(e))
        return

    set_status(f"Saved: {Path(output_path.get()).name} + {Path(mini_output_path.get()).name} ✓", GOLD)
    if open_after.get():
        os.startfile(output_path.get())     # opens the image (Windows only)


# --------------------------------------------------------------------------
# Preview window
# --------------------------------------------------------------------------
preview = {"window": None, "label": None, "info": None, "hint": None, "mtime": None}


def preview_is_open():
    return preview["window"] is not None and preview["window"].winfo_exists()


def selected_layout():
    """Path of the layout selected in the preview."""
    return LAYOUTS[preview_board.get()]


def layout_mtime():
    """Last modification time of the selected layout (or None if it is missing)."""
    try:
        return selected_layout().stat().st_mtime
    except OSError:
        return None


def fit_preview(img):
    """Scale the image so it fits into PREVIEW_SIZE.
    Big images are scaled down smoothly, small ones (mini board) are scaled up pixel-perfect."""
    scale = min(PREVIEW_SIZE[0] / img.width, PREVIEW_SIZE[1] / img.height)
    if scale >= 1:
        scale = int(scale)              # whole number -> every pixel becomes a clean square
        resample = Image.NEAREST
    else:
        resample = Image.LANCZOS
    size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
    return img.resize(size, resample), scale


def render_preview():
    """Redraw the image (without saving) and show it in the preview window."""
    if not preview_is_open():
        return
    name = get_tournament(warn=False)
    if name is None:
        preview["info"].config(text="Enter a tournament name first.", foreground=RED)
        return
    try:
        img = preview_png(name, selected_layout())
    except Exception as e:      # e.g. a typo in the layout file -> show it instead of crashing
        preview["info"].config(text=f"Error: {e}", foreground=RED)
        return

    original_size = img.size
    img, scale = fit_preview(img)
    photo = ImageTk.PhotoImage(img, master=preview["window"])
    preview["label"].config(image=photo)
    preview["label"].image = photo              # keep a reference, otherwise the image stays empty!
    preview["info"].config(
        text=f"{original_size[0]}×{original_size[1]} px, shown at {scale:g}×  ·  "
             f"updated {time.strftime('%H:%M:%S')}",
        foreground=MUTED)


def on_switch_board(event=None):
    """Another layout was selected in the preview -> watch that one and redraw."""
    preview["mtime"] = layout_mtime()
    preview["hint"].config(text=f"Updates automatically when you save {selected_layout().name}.")
    render_preview()


def watch_layout():
    """Check every second whether the selected layout file was saved -> then redraw."""
    if not preview_is_open():
        return
    mtime = layout_mtime()
    if mtime != preview["mtime"]:
        preview["mtime"] = mtime
        render_preview()
    root.after(1000, watch_layout)


def close_preview():
    preview["window"].destroy()
    preview["window"] = None


def on_preview():
    if preview_is_open():                       # already open? Bring to front + redraw
        preview["window"].lift()
        render_preview()
        return

    win = tk.Toplevel(root)
    win.title("Leaderboard Preview")
    win.transient(root)         # always stays above the main window
    win.configure(bg=BG)
    win.resizable(False, False)
    win.protocol("WM_DELETE_WINDOW", close_preview)

    bar = ttk.Frame(win, padding=(16, 12, 16, 8))
    bar.pack(fill="x")
    board_combo = ttk.Combobox(bar, textvariable=preview_board, values=list(LAYOUTS),
                               state="readonly", width=18)
    board_combo.pack(side="left")
    board_combo.bind("<<ComboboxSelected>>", on_switch_board)
    ttk.Button(bar, text="Refresh", command=render_preview).pack(side="left", padx=(8, 0))
    ttk.Button(bar, text="Edit layout…", command=on_edit_layout).pack(side="left", padx=8)

    hint = ttk.Label(win, text=f"Updates automatically when you save {selected_layout().name}.",
                     style="Status.TLabel", padding=(16, 0, 16, 2))
    hint.pack(anchor="w")
    info = ttk.Label(win, text="", style="Status.TLabel", padding=(16, 0, 16, 8))
    info.pack(anchor="w")

    label = tk.Label(win, bg=BG, bd=0)
    label.pack(padx=16, pady=(0, 16))

    preview.update(window=win, label=label, info=info, hint=hint, mtime=layout_mtime())
    render_preview()
    win.lift()                  # bring the preview in front of the main window
    win.focus_force()
    root.after(1000, watch_layout)


def on_edit_layout():
    """Open the layout selected in the preview in the default editor (fallback: Notepad)."""
    path = selected_layout()
    try:
        os.startfile(path)
    except OSError:
        subprocess.Popen(["notepad", str(path)])


def on_edit_headbooms(event=None):
    """Double-click / button: set headbooms for the selected team in the selected game."""
    selected = headboom_table.selection()
    game = games_by_label.get(game_choice.get())
    if not selected or game is None:
        messagebox.showinfo("Nothing selected", "Please select a game and a team first.")
        return

    team_name = selected[0]         # the row ID is the team name (see refresh_headboom_table)
    current = headboom_table.set(team_name, "hb")
    value = simpledialog.askinteger(
        "Headbooms",
        f"Headbooms for {team_name}\nin game {game.game_id}:\n\n(-{HEADBOOM_PENALTY:g} points each)",
        initialvalue=int(current), minvalue=0, parent=root,
    )
    if value is None:               # Cancel
        return

    try:
        set_headbooms(get_tournament(), game.game_id, team_name, value)
    except Exception as e:
        messagebox.showerror("Could not save", str(e))
        return

    refresh_all()
    headboom_table.selection_set(team_name)
    set_status(f"{team_name}: {value} headboom(s) in game {game.game_id} saved ✓", GOLD)


# --------------------------------------------------------------------------
# Refill the tables
# --------------------------------------------------------------------------
games_by_label = {}     # "Game 1  ·  ID 63716452" -> Game object


def refresh_all(event=None):
    refresh_tournament_list()
    refresh_standings()
    refresh_games()
    refresh_bans()
    render_preview()        # does nothing if the preview is not open


def refresh_tournament_list():
    """Fill the tournament dropdown with all tournaments saved in the DB."""
    try:
        tournament_combo["values"] = list_tournaments()
    except Exception as e:
        set_status(f"Could not load tournaments: {e}", RED)


def refresh_standings():
    clear(standings_table)
    standings_info.config(text="")
    name = get_tournament(warn=False)
    if name is None:
        return
    try:
        standings = show_standings(name)
    except Exception as e:
        set_status(f"Could not load standings: {e}", RED)
        return

    for i, s in enumerate(standings):
        tags = ["odd" if i % 2 else "even"]
        if s.checkpoint:                # checkpoint teams are shown in red
            tags.append("checkpoint")
        standings_table.insert("", "end", values=(f"#{s.rank}", s.team.team_name,
                                                  s.p1_tk, s.p2_tk, f"{s.points:g}"), tags=tags)
    checkpoints = sum(1 for s in standings if s.checkpoint)
    standings_info.config(text=f"{len(standings)} teams  ·  {checkpoints} on checkpoint (red)")


def refresh_games():
    """Refill the game selection (combobox), keep the selected game if possible."""
    games_by_label.clear()
    name = get_tournament(warn=False)
    games = load_games(name) if name else []
    for number, game in enumerate(games, start=1):
        games_by_label[f"Game {number}  ·  ID {game.game_id}"] = game

    labels = list(games_by_label)
    game_combo["values"] = labels
    if game_choice.get() not in games_by_label:
        game_choice.set(labels[-1] if labels else "")     # preselect the newest game
    refresh_headboom_table()


def refresh_headboom_table(event=None):
    clear(headboom_table)
    game = games_by_label.get(game_choice.get())
    if game is None:
        return
    # sorted by placement so rows don't jump around while editing
    for i, e in enumerate(sorted(game.entries, key=lambda e: e.placement)):
        tags = ["odd" if i % 2 else "even"]
        if e.headbooms:
            tags.append("penalty")
        headboom_table.insert("", "end", iid=e.team.team_name, tags=tags, values=(
            e.placement, e.team.team_name, f"{e.csv_points:g}", e.headbooms, f"{e.total_score:g}"))


def refresh_bans():
    clear(bans_table)
    name = get_tournament(warn=False)
    bans = show_bans(name) if name else {}

    # longest ban first, then alphabetical
    for i, (character, games_left) in enumerate(sorted(bans.items(), key=lambda b: (-b[1], b[0]))):
        tags = ["odd" if i % 2 else "even"]
        text = "next game" if games_left == 1 else f"next {games_left} games"
        bans_table.insert("", "end", values=(character, text), tags=tags)

    bans_info.config(text=f"{len(bans)} banned for the next game" if bans else "No bans – all characters are free.")
    notebook.tab(bans_tab, text=f"  Bans ({len(bans)})  ")


# --------------------------------------------------------------------------
# Window
# --------------------------------------------------------------------------
root = tk.Tk()
root.title("EU DOJO Leaderboard")
root.geometry("780x800")
root.minsize(660, 640)
root.configure(bg=BG)

# shared variables ("pinboards") that every function can see
tournament = tk.StringVar(value=DEFAULT_TOURNAMENT)
csv_folder = tk.StringVar()
output_path = tk.StringVar()
open_after = tk.BooleanVar(value=True)
game_choice = tk.StringVar()
mini_output_path = tk.StringVar()
preview_board = tk.StringVar(value="Main leaderboard")   # which layout the preview shows

# --------------------------------------------------------------------------
# Styles (look of all ttk widgets in one place)
# --------------------------------------------------------------------------
style = ttk.Style()
style.theme_use("clam")     # "clam" is the easiest theme to recolor

style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
style.configure("TFrame", background=BG)
style.configure("Card.TFrame", background=CARD)
style.configure("Card.TLabel", background=CARD, foreground=TEXT)
style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 20))
style.configure("Subtitle.TLabel", background=BG, foreground=MUTED)
style.configure("Section.TLabel", background=CARD, foreground=GOLD, font=("Segoe UI Semibold", 11))
style.configure("Status.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
style.configure("Card.TCheckbutton", background=CARD, foreground=TEXT,
                indicatorbackground=FIELD, indicatorforeground=GOLD, upperbordercolor=FIELD,
                lowerbordercolor=FIELD)
style.map("Card.TCheckbutton", background=[("active", CARD)],
          indicatorbackground=[("selected", FIELD), ("active", HOVER)])

style.configure("TEntry", fieldbackground=FIELD, foreground=TEXT, insertcolor=TEXT,
                bordercolor=FIELD, lightcolor=FIELD, darkcolor=FIELD, padding=6)

style.configure("TCombobox", fieldbackground=FIELD, background=FIELD, foreground=TEXT,
                insertcolor=TEXT, arrowcolor=MUTED, bordercolor=FIELD, lightcolor=FIELD, darkcolor=FIELD, padding=6)
style.map("TCombobox", fieldbackground=[("readonly", FIELD)], foreground=[("readonly", TEXT)],
          selectbackground=[("readonly", FIELD)], selectforeground=[("readonly", TEXT)],
          background=[("active", HOVER)])
root.option_add("*TCombobox*Listbox.background", FIELD)      # the dropdown list
root.option_add("*TCombobox*Listbox.foreground", TEXT)
root.option_add("*TCombobox*Listbox.selectBackground", HOVER)
root.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))

style.configure("TButton", background=FIELD, foreground=TEXT, borderwidth=0,
                focusthickness=0, padding=(12, 7))
style.map("TButton", background=[("active", HOVER)])

style.configure("Accent.TButton", background=RED, foreground="#ffffff",
                font=("Segoe UI Semibold", 10), padding=(16, 9))
style.map("Accent.TButton", background=[("active", "#ff7b7a")])

style.configure("Gold.TButton", background=GOLD, foreground="#1a1a1a",
                font=("Segoe UI Semibold", 10), padding=(16, 9))
style.map("Gold.TButton", background=[("active", "#ffdda3")])

style.configure("Treeview", background=FIELD, fieldbackground=FIELD, foreground=TEXT,
                rowheight=30, borderwidth=0, font=("Segoe UI", 10),
                bordercolor=CARD, lightcolor=CARD, darkcolor=CARD)
style.configure("Treeview.Heading", background=CARD, foreground=MUTED,
                font=("Segoe UI Semibold", 9), borderwidth=0, padding=6)
style.map("Treeview", background=[("selected", "#3a3f50")])
style.map("Treeview.Heading", background=[("active", CARD)])

style.configure("Vertical.TScrollbar", background=FIELD, troughcolor=CARD, bordercolor=CARD,
                lightcolor=FIELD, darkcolor=FIELD, arrowcolor=MUTED)
style.map("Vertical.TScrollbar", background=[("active", HOVER)])

style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 0, 0, 0),
                bordercolor=CARD, lightcolor=CARD, darkcolor=CARD)
style.configure("TNotebook.Tab", background=BG, foreground=MUTED, borderwidth=0,
                padding=(14, 8), font=("Segoe UI Semibold", 10),
                bordercolor=BG, lightcolor=BG)
style.map("TNotebook.Tab", background=[("selected", CARD), ("active", CARD)],
          foreground=[("selected", GOLD)], lightcolor=[("selected", CARD)])

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
header = ttk.Frame(root, padding=(20, 16, 20, 8))
header.pack(fill="x")
ttk.Label(header, text="EU DOJO Leaderboard", style="Title.TLabel").pack(anchor="w")
ttk.Label(header, text="A Tool created by SmugDragon to assist with Tournaments",
          style="Subtitle.TLabel").pack(anchor="w")

# --------------------------------------------------------------------------
# Card: settings
# --------------------------------------------------------------------------
settings = ttk.Frame(root, style="Card.TFrame", padding=16)
settings.pack(fill="x", padx=20, pady=8)
settings.columnconfigure(1, weight=1)       # middle column grows with the window

ttk.Label(settings, text="Settings", style="Section.TLabel").grid(
    row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

# Tournament
ttk.Label(settings, text="Tournament", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 12))
# Editable dropdown: pick a saved tournament OR type a new name
tournament_combo = ttk.Combobox(settings, textvariable=tournament)
tournament_combo.grid(row=1, column=1, sticky="ew", pady=4, padx=(0, 8))
tournament_combo.bind("<<ComboboxSelected>>", refresh_all)     # picked from the list
tournament_combo.bind("<Return>", refresh_all)                 # Enter -> reload everything
tournament_combo.bind("<FocusOut>", refresh_all)
ttk.Button(settings, text="Delete…", command=on_delete_tournament).grid(row=1, column=2, sticky="e", pady=4)

# CSV folder
ttk.Label(settings, text="CSV folder", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 12))
ttk.Label(settings, textvariable=csv_folder, style="Muted.TLabel").grid(row=2, column=1, sticky="w")
ttk.Button(settings, text="Choose folder…", command=on_choose_folder).grid(row=2, column=2, sticky="e", pady=4)

# Output
ttk.Label(settings, text="PNG output", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 12))
ttk.Label(settings, textvariable=output_path, style="Muted.TLabel").grid(row=3, column=1, sticky="w")
ttk.Button(settings, text="Choose file…", command=on_choose_output).grid(row=3, column=2, sticky="e", pady=4)

# Mini output (empty = automatically "<name>_mini.png" next to the main image)
ttk.Label(settings, text="Mini PNG output", style="Card.TLabel").grid(row=4, column=0, sticky="w", padx=(0, 12))
ttk.Label(settings, textvariable=mini_output_path, style="Muted.TLabel").grid(row=4, column=1, sticky="w")
ttk.Button(settings, text="Choose file…", command=on_choose_mini_output).grid(row=4, column=2, sticky="e", pady=4)

# --------------------------------------------------------------------------
# Action buttons
# --------------------------------------------------------------------------
actions = ttk.Frame(root, style="Card.TFrame", padding=16)
actions.pack(fill="x", padx=20, pady=8)

ttk.Button(actions, text="Import CSVs", style="Accent.TButton", command=on_import).pack(side="left")
ttk.Button(actions, text="Create PNG", style="Gold.TButton", command=on_create_png).pack(side="left", padx=10)
ttk.Checkbutton(actions, text="Open image afterwards", variable=open_after,
                style="Card.TCheckbutton").pack(side="left", padx=10)
ttk.Button(actions, text="Edit layout…", command=on_edit_layout).pack(side="right")
ttk.Button(actions, text="Preview", command=on_preview).pack(side="right", padx=10)

# --------------------------------------------------------------------------
# Status bar (packed before the tabs so it always stays visible)
# --------------------------------------------------------------------------
status_label = ttk.Label(root, text="Ready.", style="Status.TLabel", padding=(20, 4, 20, 12))
status_label.pack(fill="x", side="bottom")

# --------------------------------------------------------------------------
# Tabs: Standings | Headbooms | Bans
# --------------------------------------------------------------------------
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=(8, 8))

# --- Tab 1: Standings -----------------------------------------------------
standings_tab = ttk.Frame(notebook, style="Card.TFrame", padding=16)
notebook.add(standings_tab, text="  Standings  ")

standings_info = ttk.Label(standings_tab, text="", style="Muted.TLabel")
standings_info.pack(anchor="e", pady=(0, 8))
standings_table = make_table(standings_tab, [
    ("rank", "RANK", 60, "center"),
    ("name", "NAME", 260, "w"),
    ("p1", "PHASE 1 TK", 100, "center"),
    ("p2", "PHASE 2+ TK", 100, "center"),
    ("pts", "TOTAL PTS", 100, "center"),
])

# --- Tab 2: Headbooms -----------------------------------------------------
headboom_tab = ttk.Frame(notebook, style="Card.TFrame", padding=16)
notebook.add(headboom_tab, text="  Headbooms  ")

game_row = ttk.Frame(headboom_tab, style="Card.TFrame")
game_row.pack(fill="x", pady=(0, 10))
ttk.Label(game_row, text="Game", style="Card.TLabel").pack(side="left", padx=(0, 12))
game_combo = ttk.Combobox(game_row, textvariable=game_choice, state="readonly", width=32)
game_combo.pack(side="left")
game_combo.bind("<<ComboboxSelected>>", refresh_headboom_table)
ttk.Button(game_row, text="Set headbooms…", command=on_edit_headbooms).pack(side="right")

ttk.Label(headboom_tab, text=f"Double-click a team to enter headbooms "
                             f"(-{HEADBOOM_PENALTY:g} points each, in this game only).",
          style="Muted.TLabel").pack(anchor="w", pady=(0, 8))

headboom_table = make_table(headboom_tab, [
    ("place", "PLACE", 60, "center"),
    ("name", "TEAM", 260, "w"),
    ("csv", "CSV PTS", 90, "center"),
    ("hb", "HEADBOOMS", 100, "center"),
    ("total", "FINAL PTS", 120, "center"),
])
headboom_table.bind("<Double-1>", on_edit_headbooms)

# --- Tab 3: Bans ----------------------------------------------------------
bans_tab = ttk.Frame(notebook, style="Card.TFrame", padding=16)
notebook.add(bans_tab, text="  Bans  ")

bans_info = ttk.Label(bans_tab, text="", style="Muted.TLabel")
bans_info.pack(anchor="w", pady=(0, 4))
ttk.Label(bans_tab, text="Rule: 3 picks in one game → banned for 1 game, every extra pick +1 game.",
          style="Muted.TLabel").pack(anchor="w", pady=(0, 8))
bans_table = make_table(bans_tab, [
    ("char", "CHARACTER", 260, "w"),
    ("left", "BANNED FOR", 200, "center"),
])

refresh_all()     # show already saved data on startup
root.mainloop()
