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
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from main import create_png, import_csv, show_standings

# --------------------------------------------------------------------------
# Farben (passend zum Leaderboard.png: dunkel, Gold, Rot)
# --------------------------------------------------------------------------
BG = "#14161c"          # Fensterhintergrund
CARD = "#1e212b"        # Hintergrund der "Karten"
FIELD = "#2a2e3a"       # Eingabefelder / Tabellenzeilen
FIELD_ALT = "#242833"   # jede zweite Tabellenzeile
TEXT = "#e8e8ec"
MUTED = "#8a8f9c"
GOLD = "#ffd084"
RED = "#fd6160"

DEFAULT_TOURNAMENT = "EU_DOJO_NR_1"


# --------------------------------------------------------------------------
# Button-Funktionen
# --------------------------------------------------------------------------
def set_status(text, color=MUTED):
    status_label.config(text=text, foreground=color)


def get_tournament():
    """Turniername aus dem Eingabefeld, oder None + Warnung wenn leer."""
    name = tournament.get().strip()
    if not name:
        messagebox.showwarning("Turnier fehlt", "Bitte zuerst einen Turniernamen eingeben.")
        return None
    return name


def on_choose_folder():
    folder = filedialog.askdirectory(title="Ordner mit den CSV-Dateien wählen")
    if folder:                      # leer = Nutzer hat "Abbrechen" gedrückt
        csv_folder.set(folder)
        count = len(list(Path(folder).glob("*.csv")))
        set_status(f"{count} CSV-Datei(en) im Ordner gefunden.")


def on_choose_output():
    path = filedialog.asksaveasfilename(
        title="PNG speichern unter",
        defaultextension=".png",
        filetypes=[("PNG-Bild", "*.png")],
        initialfile=f"{tournament.get().strip() or 'leaderboard'}.png",
    )
    if path:
        output_path.set(path)


def on_import():
    name = get_tournament()
    if name is None:
        return
    folder = csv_folder.get()
    if not folder:
        messagebox.showwarning("Ordner fehlt", "Bitte zuerst einen CSV-Ordner wählen.")
        return

    csv_files = sorted(Path(folder).glob("*.csv"))
    if not csv_files:
        messagebox.showinfo("Keine CSVs", "In diesem Ordner liegen keine .csv-Dateien.")
        return

    new, skipped, errors = 0, 0, []
    for csv_file in csv_files:
        try:
            if import_csv(str(csv_file), name):
                new += 1
            else:
                skipped += 1
        except Exception as e:      # eine kaputte CSV soll nicht alles abbrechen
            errors.append(f"{csv_file.name}: {e}")

    refresh_table()

    text = f"Import fertig: {new} neu, {skipped} schon gespeichert"
    if errors:
        set_status(text + f", {len(errors)} Fehler", RED)
        messagebox.showerror("Fehler beim Import", "\n".join(errors))
    else:
        set_status(text + " ✓", GOLD)


def on_create_png():
    name = get_tournament()
    if name is None:
        return
    if not output_path.get():
        on_choose_output()          # noch kein Ziel? Dann jetzt fragen
        if not output_path.get():
            return

    try:
        create_png(name, output_path.get())
    except Exception as e:
        messagebox.showerror("Fehler beim Erstellen", str(e))
        return

    set_status(f"PNG gespeichert: {output_path.get()} ✓", GOLD)
    if open_after.get():
        os.startfile(output_path.get())     # öffnet das Bild (nur Windows)


def refresh_table(event=None):
    """Tabelle leeren und mit den aktuellen Standings neu füllen."""
    table.delete(*table.get_children())
    games_label.config(text="")
    name = tournament.get().strip()
    if not name:
        return
    try:
        standings = show_standings(name)
    except Exception as e:
        set_status(f"Konnte Standings nicht laden: {e}", RED)
        return

    for i, s in enumerate(standings):
        tags = ["odd" if i % 2 else "even"]
        if s.rank <= 3:
            tags.append("top3")
        table.insert("", "end", values=(f"#{s.rank}", s.team.team_name,
                                        s.p1_tk, s.p2_tk, f"{s.points:g}"), tags=tags)
    games_label.config(text=f"{len(standings)} Teams")


# --------------------------------------------------------------------------
# Fenster
# --------------------------------------------------------------------------
root = tk.Tk()
root.title("ERGL Leaderboard")
root.geometry("760x780")
root.minsize(640, 600)
root.configure(bg=BG)

# "Pinnwände", die alle Funktionen sehen können
tournament = tk.StringVar(value=DEFAULT_TOURNAMENT)
csv_folder = tk.StringVar()
output_path = tk.StringVar()
open_after = tk.BooleanVar(value=True)

# --------------------------------------------------------------------------
# Styles (Aussehen aller ttk-Widgets an einer Stelle)
# --------------------------------------------------------------------------
style = ttk.Style()
style.theme_use("clam")     # "clam" lässt sich am besten umfärben

style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
style.configure("TFrame", background=BG)
style.configure("Card.TFrame", background=CARD)
style.configure("Card.TLabel", background=CARD, foreground=TEXT)
style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 20))
style.configure("Subtitle.TLabel", background=BG, foreground=MUTED)
style.configure("Section.TLabel", background=CARD, foreground=GOLD, font=("Segoe UI Semibold", 11))
style.configure("Status.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
style.configure("Card.TCheckbutton", background=CARD, foreground=TEXT)
style.map("Card.TCheckbutton", background=[("active", CARD)])

style.configure("TEntry", fieldbackground=FIELD, foreground=TEXT, insertcolor=TEXT,
                bordercolor=FIELD, lightcolor=FIELD, darkcolor=FIELD, padding=6)

style.configure("TButton", background=FIELD, foreground=TEXT, borderwidth=0,
                focusthickness=0, padding=(12, 7))
style.map("TButton", background=[("active", "#363b4a")])

style.configure("Accent.TButton", background=RED, foreground="#ffffff",
                font=("Segoe UI Semibold", 10), padding=(16, 9))
style.map("Accent.TButton", background=[("active", "#ff7b7a")])

style.configure("Gold.TButton", background=GOLD, foreground="#1a1a1a",
                font=("Segoe UI Semibold", 10), padding=(16, 9))
style.map("Gold.TButton", background=[("active", "#ffdda3")])

style.configure("Treeview", background=FIELD, fieldbackground=FIELD, foreground=TEXT,
                rowheight=30, borderwidth=0, font=("Segoe UI", 10),
                bordercolor=CARD, lightcolor=CARD, darkcolor=CARD)
style.configure("Vertical.TScrollbar", background=FIELD, troughcolor=CARD, bordercolor=CARD,
                lightcolor=FIELD, darkcolor=FIELD, arrowcolor=MUTED)
style.map("Vertical.TScrollbar", background=[("active", "#363b4a")])
style.configure("Treeview.Heading", background=CARD, foreground=MUTED,
                font=("Segoe UI Semibold", 9), borderwidth=0, padding=6)
style.map("Treeview", background=[("selected", "#3a3f50")])
style.map("Treeview.Heading", background=[("active", CARD)])

# --------------------------------------------------------------------------
# Kopfzeile
# --------------------------------------------------------------------------
header = ttk.Frame(root, padding=(20, 16, 20, 8))
header.pack(fill="x")
ttk.Label(header, text="ERGL Leaderboard", style="Title.TLabel").pack(anchor="w")
ttk.Label(header, text="CSVs importieren  →  Standings prüfen  →  PNG erzeugen",
          style="Subtitle.TLabel").pack(anchor="w")

# --------------------------------------------------------------------------
# Karte: Einstellungen
# --------------------------------------------------------------------------
settings = ttk.Frame(root, style="Card.TFrame", padding=16)
settings.pack(fill="x", padx=20, pady=8)
settings.columnconfigure(1, weight=1)       # mittlere Spalte wächst mit

ttk.Label(settings, text="Einstellungen", style="Section.TLabel").grid(
    row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

# Turnier
ttk.Label(settings, text="Turnier", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 12))
tournament_entry = ttk.Entry(settings, textvariable=tournament)
tournament_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)
tournament_entry.bind("<Return>", refresh_table)      # Enter -> Tabelle neu laden
tournament_entry.bind("<FocusOut>", refresh_table)

# CSV-Ordner
ttk.Label(settings, text="CSV-Ordner", style="Card.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 12))
ttk.Label(settings, textvariable=csv_folder, style="Muted.TLabel").grid(row=2, column=1, sticky="w")
ttk.Button(settings, text="Ordner wählen…", command=on_choose_folder).grid(row=2, column=2, sticky="e", pady=4)

# Output
ttk.Label(settings, text="PNG-Ziel", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 12))
ttk.Label(settings, textvariable=output_path, style="Muted.TLabel").grid(row=3, column=1, sticky="w")
ttk.Button(settings, text="Ziel wählen…", command=on_choose_output).grid(row=3, column=2, sticky="e", pady=4)

# --------------------------------------------------------------------------
# Aktions-Buttons
# --------------------------------------------------------------------------
actions = ttk.Frame(root, style="Card.TFrame", padding=16)
actions.pack(fill="x", padx=20, pady=8)

ttk.Button(actions, text="CSVs importieren", style="Accent.TButton", command=on_import).pack(side="left")
ttk.Button(actions, text="PNG erzeugen", style="Gold.TButton", command=on_create_png).pack(side="left", padx=10)
ttk.Checkbutton(actions, text="Bild danach öffnen", variable=open_after,
                style="Card.TCheckbutton").pack(side="left", padx=10)

# --------------------------------------------------------------------------
# Karte: Standings-Tabelle
# --------------------------------------------------------------------------
table_card = ttk.Frame(root, style="Card.TFrame", padding=16)
table_card.pack(fill="both", expand=True, padx=20, pady=8)

table_head = ttk.Frame(table_card, style="Card.TFrame")
table_head.pack(fill="x", pady=(0, 10))
ttk.Label(table_head, text="Standings", style="Section.TLabel").pack(side="left")
games_label = ttk.Label(table_head, text="", style="Muted.TLabel")
games_label.pack(side="right")

columns = ("rank", "name", "p1", "p2", "pts")
table = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
for col, title, width, anchor in [
    ("rank", "RANK", 60, "center"),
    ("name", "NAME", 260, "w"),
    ("p1", "PHASE 1 TK", 100, "center"),
    ("p2", "PHASE 2+ TK", 100, "center"),
    ("pts", "TOTAL PTS", 100, "center"),
]:
    table.heading(col, text=title, anchor=anchor)
    table.column(col, width=width, anchor=anchor, stretch=(col == "name"))

table.tag_configure("even", background=FIELD)
table.tag_configure("odd", background=FIELD_ALT)
table.tag_configure("top3", foreground=GOLD)

scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# --------------------------------------------------------------------------
# Statuszeile
# --------------------------------------------------------------------------
status_label = ttk.Label(root, text="Bereit.", style="Status.TLabel", padding=(20, 4, 20, 12))
status_label.pack(fill="x", before=table_card, side="bottom")   # immer sichtbar, auch bei kleinem Fenster

refresh_table()     # beim Start schon gespeicherte Standings anzeigen
root.mainloop()
