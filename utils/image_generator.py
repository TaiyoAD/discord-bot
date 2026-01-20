import os
import requests
import io
from PIL import Image, ImageDraw, ImageFont

# --- 1. ASSET CHECKER ---
def check_font():
    """Ensures the western font exists. Run this on import."""
    if not os.path.exists('font_bounty.ttf'):
        print("🤠 Font missing in utils. Downloading 'Rye'...")
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/rye/Rye-Regular.ttf"
            r = requests.get(url, allow_redirects=True)
            with open('font_bounty.ttf', 'wb') as f:
                f.write(r.content)
            print("✅ Font installed.")
        except Exception as e:
            print(f"❌ Failed to download font: {e}")

# Run check immediately when this file is imported
check_font()

# --- 2. HELPER FUNCTIONS ---
def get_centered_x(draw, text, font, box_width):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    return (box_width - text_width) / 2

def draw_poster_on_bg(background, bg_draw, x_offset, avatar_bytes, user_name, font_wanted, font_name):
    # Poster Settings
    p_w, p_h = 350, 450
    p_bg_color = "#F5EDC9" # Beige paper
    
    # Draw Poster Paper
    bg_draw.rectangle([x_offset, 50, x_offset + p_w, 50 + p_h], fill=p_bg_color)
    bg_draw.rectangle([x_offset + 10, 60, x_offset + p_w - 10, 50 + p_h - 10], outline="#4a3c31", width=3)
    
    # Text: WANTED
    w_text = "WANTED"
    w_x = x_offset + get_centered_x(bg_draw, w_text, font_wanted, p_w)
    bg_draw.text((w_x, 80), w_text, font=font_wanted, fill="black")

    # Avatar
    try:
        av_size = 200
        av = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((av_size, av_size))
        av_x = x_offset + (p_w - av_size) // 2
        background.paste(av, (int(av_x), 160), av)
    except Exception as e:
        print(f"Avatar error: {e}")

    # Text: NAME
    if len(user_name) > 10: user_name = user_name[:10] + "..."
    n_x = x_offset + get_centered_x(bg_draw, user_name, font_name, p_w)
    bg_draw.text((n_x, 380), user_name, font=font_name, fill="#3b2413")

# --- 3. MAIN GENERATOR ---
def create_wanted_poster(avatar1_bytes, avatar2_bytes, name1, name2, match_percentage):
    # Canvas
    width, height = 900, 600
    background = Image.new("RGBA", (width, height), "#3b2413") 
    draw = ImageDraw.Draw(background)
    
    # Wood Planks
    for y in range(0, height, 50):
        draw.line([(0, y), (width, y)], fill="#2e1b0e", width=2)

    # Fonts
    try:
        font_wanted = ImageFont.truetype("font_bounty.ttf", 50)
        font_name = ImageFont.truetype("font_bounty.ttf", 30)
        font_bounty = ImageFont.truetype("font_bounty.ttf", 60)
    except:
        font_wanted = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_bounty = ImageFont.load_default()

    # Draw Posters
    draw_poster_on_bg(background, draw, 50, avatar1_bytes, name1, font_wanted, font_name)
    draw_poster_on_bg(background, draw, 500, avatar2_bytes, name2, font_wanted, font_name)

    # Bounty Banner
    banner_y = 520
    draw.rectangle([50, banner_y, 850, banner_y + 70], fill="#F5EDC9")
    draw.rectangle([50, banner_y, 850, banner_y + 70], outline="#4a3c31", width=4)

    # Bounty Text
    bounty_text = f"BOUNTY: {match_percentage}%"
    b_x = 50 + get_centered_x(draw, bounty_text, font_bounty, 800)
    draw.text((b_x, banner_y - 5), bounty_text, font=font_bounty, fill="#5c0a0a")

    return background