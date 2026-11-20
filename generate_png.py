from PIL import Image, ImageDraw, ImageFont
from db_service import load_leaderboard

def create_standings_png(
    tournament_id: str, 
    bg_path: str = None, 
    output_path: str = "standings_card.png"
) -> None:
    # 1. Load data from TinyDB
    leaderboard = load_leaderboard(tournament_id)
    standings = leaderboard.overall_standings()

    # 2. Setup Base Canvas (Load custom PNG template or create new dark canvas)
    if bg_path:
        img = Image.open(bg_path).convert("RGBA")
    else:
        # Create an 800x600 dark canvas if no custom PNG template is provided
        img = Image.new("RGBA", (800, 600), color=(20, 20, 30, 255))

    draw = ImageDraw.Draw(img)

    # 3. Load Fonts (Use default if custom TTF font isn't available)
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        header_font = ImageFont.truetype("arial.ttf", 22)
        row_font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        title_font = header_font = row_font = ImageFont.load_default()

    # 4. Draw Header
    draw.text((50, 40), f"STANDINGS: {tournament_id.upper()}", fill=(255, 255, 255), font=title_font)
    
    # Table Column Headers
    draw.text((50, 110), "#", fill=(180, 180, 180), font=header_font)
    draw.text((100, 110), "TEAM", fill=(180, 180, 180), font=header_font)
    draw.text((550, 110), "SCORE", fill=(180, 180, 180), font=header_font)
    draw.text((680, 110), "CHARS", fill=(180, 180, 180), font=header_font)

    # Separator Line
    draw.line([(50, 140), (750, 140)], fill=(80, 80, 100), width=2)

    # 5. Draw Team Rows
    y_offset = 160
    for rank, (team, score, chars) in enumerate(standings, start=1):
        # Format text colors (Gold for 1st place, white for others)
        text_color = (255, 215, 0) if rank == 1 else (255, 255, 255)

        draw.text((50, y_offset), str(rank), fill=text_color, font=row_font)
        draw.text((100, y_offset), team.team_name, fill=text_color, font=row_font)
        draw.text((550, y_offset), f"{score:.1f}", fill=text_color, font=row_font)
        draw.text((680, y_offset), str(chars), fill=text_color, font=row_font)

        y_offset += 35
        if y_offset > img.height - 50:  # Prevent drawing outside image bounds
            break

    # 6. Export Image
    img.save(output_path)
    print(f"Successfully generated graphics card: {output_path}")

if __name__ == "__main__":
    # Test with custom PNG background (pass path to custom template PNG if you have one)
    create_standings_png(
        tournament_id="ERGL_Season_1", 
        bg_path=r"D:\ERGL\assets\template.png", # Optional background PNG
        output_path="test_leaderboard.png"
    )