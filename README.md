# ERGL – Tournament Leaderboard Tool

Turns the CSV files that the game exports after each match into a finished leaderboard image.

- Import all game CSVs of a tournament with one click
- Overall standings across all games (points, Phase 1 TK, Phase 2+ TK)
- Headboom penalties per team and game
- Checkpoint teams highlighted in red
- Character bans for the next game
- Exports the standings onto the leaderboard template as a PNG
- Small in-game leaderboard (mini PNG) for streaming, e.g. as an OBS image source
- Layouts (positions, fonts, sizes, colors) are customizable via JSON, with a live preview

A free community tool for small Eternal Return tournaments. Contributions are welcome!

---

## Download (Windows)

1. Go to the **[Releases page](https://github.com/SmugDragonER/ERGL/releases)** and download the latest `EU_DOJO.zip`.
2. Unzip it into **its own folder**, for example `Documents\ERGL\`.
3. Double-click `EU_DOJO.exe`.

No Python or other installation needed.

> **Windows warning "Windows protected your PC"?**
> The program is not signed, so Windows does not know it yet.
> Click **More info → Run anyway**. Some virus scanners also flag tools like this by mistake.

> **Your data** is saved in `tournament_db.json` **next to the .exe**.
> Keep this file to keep your tournament data. When you update to a new version, copy it into the new folder.

---

## How to use

1. **Tournament**: enter a name, e.g. `EU_DOJO_NR_1`. Each name is its own separate tournament.
2. **Choose folder…**: select the folder with the game's CSV files.
3. **Import CSVs**: reads every CSV in the folder. Games that are already saved are skipped, so you can simply re-import the whole folder after every new game.
4. Check the tabs:
   - **Standings**: the overall ranking. Checkpoint teams are red.
   - **Headbooms**: choose a game, then double-click a team to enter its headbooms for that game.
   - **Bans**: the characters that are banned for the next game.
5. **Create PNG**: choose where to save the image. Tick *Open image afterwards* to see it right away.

### Rules used

| Rule | Value |
|---|---|
| Ranking | Total points, ties broken by most kills (Phase 1 TK + Phase 2+ TK), then coinflip |
| Headboom penalty | −5 points per headboom, in the game where it happened |
| Checkpoint | Before game 5: top 2 · game 6: top 3 · game 7: top 5 · game 8: top 7 · game 9: top 8 |
| Character bans | A character picked **3 times in one game** (all teams together) is banned for the next game. Every extra pick adds one more game (3 + n picks → 1 + n games). Bans run out game by game. |

The order of the games is taken from the `gameId` in the CSVs.

---

## For developers

### Run from source

Requires Python 3.10+.

```bash
pip install -r requirements.txt
python gui.py
```

### Tests

Run from the project root:

```bash
python -m unittest discover -s tests -v
```

### Build the .exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name EU_DOJO gui.py
```

The result is `dist/EU_DOJO.exe`. The `assets/` folder is **not** packed into the .exe. It must sit next to it:

```
EU_DOJO/
├── EU_DOJO.exe
└── assets/
```

Copy `assets/` into `dist/`, zip both together and upload the zip as a GitHub Release. Do not commit `build/` or `dist/`.

### Project structure

```
gui.py              Window (tkinter), only calls the functions in main.py
main.py             Entry points: import_csv, show_standings, create_png, create_mini_png, preview_png, show_bans, set_headbooms
src/
  paths.py          All file and folder locations (works from source and as .exe)
  models.py         Team, GameEntryPerTeam, Game, TeamStanding, Leaderboard (standings, checkpoints, bans)
  services.py       Reads a CSV and builds a Game from it
  db_service.py     Saves and loads games with TinyDB (tournament_db.json)
  generate_png.py   Draws the standings onto a template, driven by a layout JSON
assets/             Templates, layout_main.json / layout_mini.json (positions, fonts, colors), fonts
tests/              Unit tests
CSV_Bible.md        Which CSV column means what
```

Data flow:

```
CSV  →  Game  →  TinyDB  →  Leaderboard  →  standings / bans  →  GUI + PNG
```

Totals, checkpoints and bans are never stored. They are calculated from the saved games every time.

### AI usage

The core logic (`models.py`, `services.py`, `db_service.py`, `generate_png.py`, `main.py`) was written by hand.
The GUI (`gui.py`), all tests in `tests/` and a few helper functions were generated with AI (Claude). They are marked as AI-generated in the files.

### Contributing

Ideas, bug reports and pull requests are welcome.

- **Found a bug or have an idea?** Open an [issue](https://github.com/SmugDragonER/ERGL/issues). For bugs, include what you did, what you expected, and the error message if there is one.
- **Want to change code?**
  1. Fork the repo and create a branch, e.g. `fix-mini-layout`.
  2. Make your change. Keep the logic in `src/` and only UI code in `gui.py`.
  3. Run the tests (`python -m unittest discover -s tests -v`) and add a test for new logic.
  4. Open a pull request and describe what it changes and why.
- Never commit real tournament data you are not allowed to share. `tournament_db.json` is your local working file.

---

## License

The code is licensed under the [MIT License](LICENSE). You can use, change and share it freely.

The [Montserrat](assets/fonts/Montserrat/OFL.txt) font is licensed under the SIL Open Font License.

## Disclaimer

ERGL is a fan-made community tool and is not affiliated with or endorsed by Nimble Neuron.
Eternal Return and all related names and assets are property of their respective owners.
