from keep_alive import keep_alive  # Import the web server
import discord
from discord.ext import commands
from datetime import timedelta
import logging
from dotenv import load_dotenv
import os

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
        await message.channel.send(f"{message.author.mention} Hello!!")

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