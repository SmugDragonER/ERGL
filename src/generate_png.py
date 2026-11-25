import json
from PIL import Image, ImageDraw, ImageFont

from src.paths import ASSET_DIR, FONT_DIR


def load_layout(path):
    with open(path, encoding="utf-8") as f:
        layout = json.load(f)
        return layout
    
def get_y(i, layout):
    return layout["first_row_y"] + i * layout["row_spacing"]

def fit_font(draw, text, namecolumn):
    """AI-GENERATED: Return the biggest font (from namecolumn["size"] down to namecolumn["min_size"])
    in which text fits into namecolumn["max_width"]."""
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
            "rank":   f"{standing.rank}",
            "name":   name,
            "p1_tk":  str(standing.p1_tk),
            "p2_tk":  str(standing.p2_tk),
            "points": f"{standing.points:.1f}",
    }

    for col_name, col in layout["columns"].items():
        color = col["color"]
        if col_name == "name":
            font = font_name
            if standing.checkpoint:
                color = layout["checkpoint_color"]
        else:
            font = ImageFont.truetype(FONT_DIR / col["font"], col["size"])

        text = col.get("prefix", "") + values[col_name]
        draw.text((col["x"],get_y(i, layout)), text, font=font, fill=color, anchor=col["anchor"])

def create_png(standings, output_path, layout_path):
    
    img = render_png(standings,layout_path)
    img.save(output_path)

def render_png(standings, layout_path):
    layout = load_layout(layout_path)
    img = Image.open(ASSET_DIR /layout["template"])
    draw = ImageDraw.Draw(img)
    for i, team in enumerate(standings):
        draw_row(draw, i, team, layout)
    return img