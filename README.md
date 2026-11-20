# Leaderboard Renderer

This small Python utility reads a CSV file with names and scores, and renders a leaderboard onto a PNG background.
(Ai was used to generate some functions in services.py and to create the test_extract)
Usage
-----

Install dependencies:

```bash
pip install -r requirements.txt
```

Run with the sample CSV (generates a default background if none provided):

```bash
python main.py sample.csv --out leaderboard.png --title "Top Players" --top 5
```

Options
-------
- `csv` : path to CSV file (required). The CSV must have a header; columns commonly named `name` and `score`.
- `--background` / `-b` : optional background PNG. If omitted the script generates `default_bg.png`.
- `--out` / `-o` : output PNG path (default `leaderboard.png`).
- `--title` / `-t` : title text to show on the image.
- `--top` : how many top rows to display.
- `--font` : path to a TTF font file to use for nicer typography.

Notes
-----
- The script uses Pillow to draw text. If you provide a `.ttf` font with `--font` the title and entries will be rendered with it; otherwise the PIL default font is used.

### Domain model

See [MODEL_STRUCTURE.md](MODEL_STRUCTURE.md) for a class diagram and the data
flow between the domain models, CSV/JSON inputs, persistence, and PNG output.

### TODO:
- make it easy for users to use
- add a json file for people to customize (e.g. PNG path, CSV location, )