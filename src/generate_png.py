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




# Team names shrink when they are too wide for the name column
# NAME_FONT_SIZE = layout["columns"]["name"]["size"]
# NAME_MIN_SIZE = layout["columns"]["name"]["min_size"]
# NAME_MAX_WIDTH = layout["columns"]["name"]["max_width"]

def load_layout():
    with open(LAYOUT_PATH, encoding="utf-8") as f:
        layout = json.load(f)
        return layout
    
def get_y(i, layout):
    return layout["first_row_y"] + i * layout["row_spacing"]

def fit_font(draw, text, namecolumn):
    """AI-GENERATED: Return the biggest name font (down to NAME_MIN_SIZE) in which text fits into max_width."""
    size = namecolumn["size"]

    font = ImageFont.truetype(FONT_DIR / namecolumn["font"], namecolumn["size"])
    while draw.textlength(text, font=font) > namecolumn["max_width"] and size > namecolumn["min_size"]:
        size -= 1
        font = ImageFont.truetype(FONT_DIR / namecolumn["font"], size)
    return font

def draw_row(draw, i, standing, layout):
    name = str(standing.team.team_name)
    font_name = fit_font(draw, name, layout["columns"]["name"])

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
        
        draw.text((col["x"],get_y(i, layout)), values[col_name], font=font, fill=color, anchor=col["anchor"])

def create_png(standings, output_path):
    
    img = render_png(standings)
    img.save(output_path)

def render_png(standings):
    layout = load_layout()
    img = Image.open(ASSET_DIR /layout["template"])
    draw = ImageDraw.Draw(img)
    for i, team in enumerate(standings):
        draw_row(draw, i, team, layout)
    return img