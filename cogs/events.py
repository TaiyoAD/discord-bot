import discord
from discord.ext import commands

# --- CONFIGURATION (REPLACE THESE WITH YOUR REAL IDS) ---
# Enable "Developer Mode" in Discord Settings -> Advanced to copy IDs
WELCOME_CHANNEL_ID = 1454853963047239894 
AUTO_ROLE_ID = 1454860376448700416

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 1. ON READY (Startup Check) ---
    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Events Scroll Loaded (Welcomer & Error Handler online).")

    # --- 2. WELCOME & AUTO-ROLE ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # A. Get Channel & Role
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        role = member.guild.get_role(AUTO_ROLE_ID)

        # B. Send Welcome Message
        if channel:
            embed = discord.Embed(
                title="Welcome to the Spirit Library!",
                description=f"Greetings {member.mention}. You have entered **{member.guild.name}**.\n*Please read the rules before proceeding.*",
                color=discord.Color.gold()
            )
            # You can change this GIF to whatever you want
            embed.set_image(url="https://media.tenor.com/bngfxunO5IAAAAAC/avatar-the-last-airbender-wan-shi-tong.gif")
            
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)
                
            await channel.send(embed=embed)
        else:
            print(f"⚠️ WARNING: Could not find Welcome Channel (ID: {WELCOME_CHANNEL_ID})")

        # C. Give Auto-Role
        if role:
            try:
                await member.add_roles(role)
                print(f"✅ Role '{role.name}' given to {member.name}")
            except discord.Forbidden:
                print(f"❌ ERROR: I do not have permission to give the '{role.name}' role. (Move my role higher!)")
        else:
            print(f"⚠️ WARNING: Could not find Auto-Role (ID: {AUTO_ROLE_ID})")

    # --- 3. GLOBAL ERROR HANDLING ---
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore "Command Not Found" spam
        if isinstance(error, commands.CommandNotFound):
            return

        # Handle missing arguments (e.g. ~ship @user -> misses second user)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"📜 **Incomplete.** You missed a required argument: `{error.param.name}`")

        # Handle Permission errors
        elif isinstance(error, commands.CheckFailure):
            # Pass silently, or warn them
            pass 

        # Print other errors to console for debugging
        else:
            print(f"⚠️ Error: {error}")

async def setup(bot):
    await bot.add_cog(Events(bot))