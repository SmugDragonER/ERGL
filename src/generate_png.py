import json
from PIL import Image, ImageDraw, ImageFont

from src.paths import ASSET_DIR, FONT_DIR, LAYOUT_PATH

# TEMPLATE = BASE_DIR / "assets" / "Leaderboard.png"
# FONT_PATH_NAME = BASE_DIR/"assets"/"fonts"/"Montserrat"/"static"/"Montserrat-Medium.ttf"
# FONT_PATH_REST = BASE_DIR/"assets"/"fonts"/"Montserrat"/"static"/"Montserrat-Bold.ttf"
# FONT_SIZE = 35
# FIRST_ROW_Y = 334
# ROW_SPACEING = 84
# RANK_X = 56
# NAME_X = 155
# PHASE_1_TK_X = 570
# PHASE_2_TK_X = 770
# TOTAL_PTS_X = 940
# COLOR_WHITE = (255,255,255)
# COLOR_RED = "#fd6160"
# COLOR_GOLD = "#ffd084"

with open(LAYOUT_PATH, encoding="utf-8") as f:
    layout = json.load(f)

TEMPLATE = ASSET_DIR / layout["template"]

FONT_PATH_NAME = FONT_DIR / "Montserrat-Medium.ttf"
FONT_PATH_REST = FONT_DIR / "Montserrat-Bold.ttf"

FIRST_ROW_Y = layout["first_row_y"]
ROW_SPACEING = layout["row_spacing"]
RANK_X = layout["columns"]["rank"]["x"]
NAME_X = layout["columns"]["name"]["x"]
PHASE_1_TK_X = layout["columns"]["p1_tk"]["x"]
PHASE_2_TK_X = layout["columns"]["p2_tk"]["x"]
TOTAL_PTS_X = layout["columns"]["points"]["x"]


# Team names shrink when they are too wide for the name column
NAME_FONT_SIZE = layout["columns"]["name"]["size"]
NAME_MIN_SIZE = layout["columns"]["name"]["min_size"]
NAME_MAX_WIDTH = layout["columns"]["name"]["max_width"]


    
def get_y(i):
    return FIRST_ROW_Y + i * ROW_SPACEING

def fit_font(draw, text, max_width):
    """AI-GENERATED: Return the biggest name font (down to NAME_MIN_SIZE) in which text fits into max_width."""
    size = NAME_FONT_SIZE
    font = ImageFont.truetype(FONT_PATH_NAME, size)
    while draw.textlength(text, font=font) > max_width and size > NAME_MIN_SIZE:
        size -= 1
        font = ImageFont.truetype(FONT_PATH_NAME, size)
    return font

def draw_row(draw, i, standing):
    name = str(standing.team.team_name)
    font_name = fit_font(draw, name, NAME_MAX_WIDTH)

    values = {
            "rank":   f"#{standing.rank}",
            "name":   name,
            "p1_tk":  str(standing.p1_tk),
            "p2_tk":  str(standing.p2_tk),
            "points": f"{standing.points:g}",
    }

    for col_name, col in layout["columns"].items():
        color = col["color"]
        if col_name == "name":
            font = font_name
            if standing.checkpoint:
                color = layout["checkpoint_color"]
        else:
            font = ImageFont.truetype(FONT_DIR / col["font"], col["size"])
        
        draw.text((col["x"],get_y(i)), values[col_name], font=font, fill=color, anchor=col["anchor"])

def create_png(standings, output_path):
    img = Image.open(TEMPLATE)
    draw = ImageDraw.Draw(img)
    for i, team in enumerate(standings):
        draw_row(draw, i, team)
    img.save(output_path)
