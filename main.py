from keep_alive import keep_alive  # Import the web server
import discord
from discord.ext import commands
from datetime import timedelta
import logging
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import os
import random
import requests
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw # <--- This fixes your "Image not defined" error
from keep_alive import keep_alive
from PIL import Image, ImageOps, ImageFilter

# Load variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Setup Permissions
intent = discord.Intents.default()
intent.message_content = True
intent.members = True

bot = commands.Bot(command_prefix='~', intents=intent)

@bot.command()
async def ship(ctx, user1: discord.Member, user2: discord.Member = None):
    if user2 is None:
        first_user = ctx.author
        second_user = user1
    else:
        first_user = user1
        second_user = user2

    # --- 1. CALCULATE SCORE & COLORS ---
    love_score = random.randint(0, 100)

    # Logic:
    # 91-100: Love (Has Icon)
    # 70-90: Spicy (No Icon)
    # 50-69: Spark (No Icon)
    # 21-49: Friendzone (No Icon)
    # 0-20: Toxic (No Icon)

    if love_score == 100:
        comment = "💍 SOULMATES! Get married NOW!"
        overlay_color = (255, 215, 0, 100) # Gold
        emoji = "🌟"
    elif love_score > 90:
        comment = "😘 True Love! It's destiny."
        overlay_color = (255, 105, 180, 100) # Pink
        emoji = "💖"
    elif love_score >= 70:
        comment = "🔥 Spicy! Get a room you two."
        overlay_color = (255, 0, 0, 100) # Red
        emoji = "🔥"
    elif love_score >= 50:
        comment = "😉 I sense a spark... maybe more than friends?"
        overlay_color = (255, 100, 100, 100) # Light Red
        emoji = "😉"
    elif love_score >= 21: # (21 to 49)
        comment = "🤝 Just friends. Friendzone forever."
        overlay_color = (0, 191, 255, 100) # Cyan/Blue
        emoji = "🤝"
    else: # (0 to 20)
        comment = "💀 RUN AWAY! It's a toxic disaster!"
        overlay_color = (50, 50, 50, 150) # Dark Grey/Black
        emoji = "💀"

    loading_msg = await ctx.send(f"{emoji} Matchmaking **{first_user.name}** & **{second_user.name}**...")

    try:
        # --- 2. SETUP CANVAS ---
        CANVAS_WIDTH = 1000
        CANVAS_HEIGHT = 500
        AVATAR_SIZE = 500 
        headers = {'User-Agent': 'Mozilla/5.0'}

        # --- 3. GET AVATARS ---
        avatar1_bytes = await first_user.display_avatar.replace(format="png").read()
        avatar2_bytes = await second_user.display_avatar.replace(format="png").read()

        img1_raw = Image.open(BytesIO(avatar1_bytes)).convert("RGBA")
        img2_raw = Image.open(BytesIO(avatar2_bytes)).convert("RGBA")

        # --- 4. CREATE LAYERS ---
        # Clear Layer (Sharp)
        img1_clear = ImageOps.fit(img1_raw, (AVATAR_SIZE, AVATAR_SIZE), centering=(0.5, 0.5))
        img2_clear = ImageOps.fit(img2_raw, (AVATAR_SIZE, AVATAR_SIZE), centering=(0.5, 0.5))
        
        clear_layer = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT))
        clear_layer.paste(img1_clear, (0, 0))
        clear_layer.paste(img2_clear, (AVATAR_SIZE, 0))

        # Blurred Background with Color Overlay
        blurred_layer = clear_layer.filter(ImageFilter.GaussianBlur(radius=20))
        color_layer = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), overlay_color)
        bg_layer = Image.alpha_composite(blurred_layer, color_layer)

        # Heart Mask
        mask_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Heart_coraz%C3%B3n.svg/500px-Heart_coraz%C3%B3n.svg.png"
        mask_resp = requests.get(mask_url, headers=headers)
        heart_shape = Image.open(BytesIO(mask_resp.content)).convert("L")
        heart_shape = heart_shape.resize((1000, 500))
        
        final_mask = Image.new("L", (CANVAS_WIDTH, CANVAS_HEIGHT), 0)
        final_mask.paste(heart_shape, (0, 0))

        # Merge Layers
        final_image = Image.composite(clear_layer, bg_layer, final_mask)

        # --- 5. ADD TINY HEART (ONLY IF SCORE > 90) ---
        if love_score > 90:
            tiny_heart_url = "https://cdn-icons-png.flaticon.com/512/210/210545.png"
            tiny_resp = requests.get(tiny_heart_url, headers=headers)
            tiny_heart = Image.open(BytesIO(tiny_resp.content)).convert("RGBA")
            tiny_heart = tiny_heart.resize((100, 100))
            
            center_x = (CANVAS_WIDTH - 100) // 2
            center_y = (CANVAS_HEIGHT - 100) // 2
            final_image.paste(tiny_heart, (center_x, center_y), tiny_heart)

        # --- 6. SAVE & SEND ---
        final_buffer = BytesIO()
        final_image.save(final_buffer, "PNG")
        final_buffer.seek(0)

        await ctx.send(
            f"💘 **Match Result:**\n"
            f"**{first_user.name}** {emoji} **{second_user.name}** = **{love_score}%**\n"
            f"_{comment}_", 
            file=discord.File(final_buffer, "ship_result.png")
        )
        await loading_msg.delete()

    except Exception as e:
        print(f"ERROR: {e}")
        await ctx.send(f"⚠️ Error: {e}")
        
@bot.event
async def on_ready():
    print(f'We are ready {bot.user.name}')

# --- MERGED ON_MESSAGE EVENT (Fixes Bug #1) ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 1. Check for Bad Words
    if 'nigga' in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - nah bro not that!")
        return  # Stop here so it doesn't try to process commands

    # 2. Check for Hello
    if 'hello' in message.content.lower():
        await message.channel.send(f"{message.author.mention} Hello!!, How are u ?")

    # 3. Process other commands (~kick, ~timeout, etc.)
    await bot.process_commands(message)

# --- COMMANDS ---
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'🦵 {member.mention} has been kicked! Reason: {reason}')

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have permission to kick people!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ You missed a step! Usage: `~kick @User [Reason]`")
    else:
        await ctx.send("Something went wrong.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, time: str, *, reason="No reason provided"):
    unit = time[-1].lower()
    try:
        number = int(time[:-1])
    except ValueError:
        await ctx.send("⚠️ Invalid format! Use `10m`, `1h`, etc.")
        return

    if unit == 's':
        duration = timedelta(seconds=number)
        full_text = f"{number} seconds"
    elif unit == 'm':
        duration = timedelta(minutes=number)
        full_text = f"{number} minutes"
    elif unit == 'h':
        duration = timedelta(hours=number)
        full_text = f"{number} hours"
    elif unit == 'd':
        duration = timedelta(days=number)
        full_text = f"{number} days"
    else:
        await ctx.send("⚠️ Invalid unit! Use s, m, h, or d.")
        return

    await member.timeout(duration, reason=reason)
    await ctx.send(f"🤐 {member.mention} has been timed out for **{full_text}**! Reason: {reason}")

@timeout.error
async def timeout_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have permission to timeout members!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Usage: `~timeout @User [Time] [Reason]`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ I couldn't find that member.")
    else:
        await ctx.send("⚠️ Something went wrong.")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member, *, reason="Appeal accepted"):
    await member.timeout(None, reason=reason)
    await ctx.send(f"🔊 {member.mention} has been unmuted.")

@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 No permission!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Usage: `~unmute @User`")
    else:
        await ctx.send("Something went wrong.")

@bot.event
async def on_member_join(member):
    # Channel ID for Welcome
    channel = bot.get_channel(1454853963047239894) 
    
    # Role ID for Auto-Role
    role_id = 1454860376448700416
    role = member.guild.get_role(role_id)

    # 1. Send Welcome Message
    if channel:
        embed = discord.Embed(
            title="Welcome to the Server!",
            description=f"Hey {member.mention}, welcome to **{member.guild.name}**! Please check out the rules.",
            color=discord.Color.yellow()
        )
        embed.set_image(url="https://c.tenor.com/-bngfxunO5IAAAAd/tenor.gif")
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        await channel.send(embed=embed)

    # 2. Give the Role (Fixes Bug #3)
    if role:
        await member.add_roles(role)



# --- START THE WEB SERVER (Fixes Bug #2) ---
keep_alive()

# --- START THE BOT ---
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)