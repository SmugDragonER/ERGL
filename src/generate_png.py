from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = Path(__file__).parent.parent
TEMPLATE = PROJECT_DIR / "assets" / "Leaderboard.png"
FONT_PATH_NAME = PROJECT_DIR/"assets"/"fonts"/"Montserrat"/"static"/"Montserrat-Medium.ttf"
FONT_PATH_REST = PROJECT_DIR/"assets"/"fonts"/"Montserrat"/"static"/"Montserrat-Bold.ttf"
FONT_SIZE = 35
FIRST_ROW_Y = 334
ROW_SPACEING = 84
RANK_X = 56
NAME_X = 155
PHASE_1_TK_X = 570
PHASE_2_TK_X = 770
TOTAL_PTS_X = 940
COLOR_WHITE = (255,255,255)
COLOR_RED = "#fd6160"
COLOR_GOLD = "#ffd084"

# Team names shrink when they are too wide for the name column
NAME_FONT_SIZE = 30
NAME_MIN_SIZE = 20
NAME_MAX_WIDTH = PHASE_1_TK_X - NAME_X - 60   # 20 px gap before the next column


def get_y(i):
    return 334 + i * ROW_SPACEING

def fit_font(draw, text, max_width):
    """AI-GENERATED: Return the biggest name font (down to NAME_MIN_SIZE) in which text fits into max_width."""
    size = NAME_FONT_SIZE
    font = ImageFont.truetype(FONT_PATH_NAME, size)
    while draw.textlength(text, font=font) > max_width and size > NAME_MIN_SIZE:
        size -= 1
        font = ImageFont.truetype(FONT_PATH_NAME, size)
    return font

def draw_row(draw, i, standing, font):
    name = str(standing.team.team_name)
    font_name = fit_font(draw, name, NAME_MAX_WIDTH)
    draw.text((RANK_X,get_y(i)),"#"+str(standing.rank), font=font, fill=COLOR_RED, anchor="lm")
    if standing.checkpoint is True:
        draw.text((NAME_X,get_y(i)),name, font=font_name, fill=COLOR_RED, anchor="lm")
    else: draw.text((NAME_X,get_y(i)),name, font=font_name, fill=COLOR_WHITE, anchor="lm")
    draw.text((PHASE_1_TK_X,get_y(i)),str(standing.p1_tk), font=font, fill=COLOR_WHITE, anchor="lm")
    draw.text((PHASE_2_TK_X,get_y(i)),str(standing.p2_tk), font=font, fill=COLOR_WHITE, anchor="lm")
    draw.text((TOTAL_PTS_X,get_y(i)),f"{standing.points:g}", font=font, fill=COLOR_GOLD, anchor="lm")
    
def create_png(standings, output_path):
    font = ImageFont.truetype(FONT_PATH_REST, 35)

    img = Image.open(TEMPLATE)
    draw = ImageDraw.Draw(img)
    for i, team in enumerate(standings):
        draw_row(draw, i, team, font)
    img.save(output_path)


