import discord
from discord.ext import commands
from datetime import timedelta # This was missing in your code

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a user from the library."""
        await member.kick(reason=reason)
        await ctx.send(f'🦵 {member.mention} has been kicked! Reason: {reason}')

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 You lack the authority to kick mortals.")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, time: str, *, reason="No reason provided"):
        """Timeouts a user (Format: 10m, 1h)."""
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
        await ctx.send(f"🤐 {member.mention} has been silenced for **{full_text}**! Reason: {reason}")

    @timeout.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 You lack the authority to silence others.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ Usage: `~timeout @User [Time] [Reason]`")

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason="Appeal accepted"):
        """Removes a timeout."""
        await member.timeout(None, reason=reason)
        await ctx.send(f"🔊 {member.mention} has been unmuted.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))