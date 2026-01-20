import discord
from discord.ext import commands
import os
import logging
from keep_alive import keep_alive
from dotenv import load_dotenv  # <--- This is the magic bridge

# --- 1. SETUP & AUTHENTICATION ---
# This line tries to load .env. 
# On your PC: It finds the file and loads your keys.
# On Render: It finds nothing, skips it, and uses the Environment Variables you set on the website.
load_dotenv()

TOKEN = os.environ.get('DISCORD_TOKEN')

# Setup Logging (Helps debug)
handler = logging.StreamHandler()
logging.basicConfig(level=logging.INFO, handlers=[handler])

# Setup Intents
intent = discord.Intents.default()
intent.message_content = True
intent.members = True

# --- 2. CUSTOM HELP COMMAND ---
class WanShiTongHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="📜 The Spirit Library Index", color=discord.Color.dark_gold())
        for cog, cmds in mapping.items():
            if not cmds: continue
            cog_name = cog.qualified_name if cog else "Unsorted Scrolls"
            filtered = await self.filter_commands(cmds, sort=True)
            if filtered:
                cmd_list = [f"`~{c.name}`" for c in filtered]
                embed.add_field(name=f"**{cog_name}**", value=" ".join(cmd_list), inline=False)
        embed.set_footer(text="Type ~help <command> for specific knowledge.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=f"📖 Knowledge: ~{command.name}", description=command.help, color=discord.Color.dark_gold())
        await self.get_destination().send(embed=embed)

# --- 3. THE BOT CLASS ---
class WanShiTongBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='~', intents=intent, help_command=WanShiTongHelp())

    async def setup_hook(self):
        # List of Cogs to load
        # Ensure these files exist in your "cogs" folder!
        cogs_list = ['cogs.ship', 'cogs.games', 'cogs.admin', 'cogs.events', 'cogs.moderation']
        
        for cog in cogs_list:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded Scroll: {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")

    async def on_ready(self):
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="over the Spirit Library"),
            status=discord.Status.dnd
        )
        print(f'🦉 Wan Shi Tong is observing mortals as {self.user}')

    async def on_message(self, message):
        if message.author == self.user: return
        await self.process_commands(message)

# --- 4. STARTUP ---
bot = WanShiTongBot()
keep_alive()  # Start web server for Render

if not TOKEN:
    print("❌ CRITICAL ERROR: DISCORD_TOKEN is missing.")
    print("   - Local: Check your .env file.")
    print("   - Render: Check your Environment Variables.")
else:
    bot.run(TOKEN)