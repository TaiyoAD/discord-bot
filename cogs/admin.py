import discord
from discord.ext import commands
import sqlite3

# REPLACE WITH YOUR ID
GOD_USER_ID = 787345609849700364

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("levels.db")
        self.cursor = self.conn.cursor()

    # --- SECURITY CHECK ---
    def cog_check(self, ctx):
        if ctx.author.id != GOD_USER_ID:
            raise commands.CheckFailure("You are not the Master of the Library.")
        return True

    # --- HEALTH (HP) MANAGEMENT ---

    @commands.command(aliases=['sethp'])
    async def admin_hp(self, ctx, member: discord.Member, amount: int):
        """Heal or Hurt a user instantly."""
        if amount > 1000: amount = 1000
        
        self.cursor.execute("UPDATE game_stats SET hp = ? WHERE user_id = ?", (amount, member.id))
        self.conn.commit()
        await ctx.send(f"❤️ **Life Force Adjusted.** {member.mention} now has **{amount}/1000 HP**.")

    @commands.command()
    async def smite(self, ctx, member: discord.Member):
        """Instantly kill a user (Set HP to 0)."""
        self.cursor.execute("UPDATE game_stats SET hp = 0 WHERE user_id = ?", (member.id,))
        self.conn.commit()
        await ctx.send(f"⚡ **JUDGMENT.** {member.mention} has been crushed. (HP set to 0).")

    # --- INVENTORY MANAGEMENT ---

    @commands.command(aliases=['give'])
    async def admin_give(self, ctx, member: discord.Member, *, item_name: str):
        """Force give an item to a user."""
        self.cursor.execute("SELECT count FROM inventory WHERE user_id = ? AND item_name = ?", (member.id, item_name))
        result = self.cursor.fetchone()
        
        if result:
            new_count = result[0] + 1
            self.cursor.execute("UPDATE inventory SET count = ? WHERE user_id = ? AND item_name = ?", (new_count, member.id, item_name))
        else:
            self.cursor.execute("INSERT INTO inventory (user_id, item_name, count) VALUES (?, ?, ?)", (member.id, item_name, 1))
        
        self.conn.commit()
        await ctx.send(f"🎁 **Gift from the Spirit.** Given **1x {item_name}** to {member.mention}.")

    @commands.command(aliases=['wipe'])
    async def admin_wipe(self, ctx, member: discord.Member):
        """Delete a user's entire inventory."""
        self.cursor.execute("DELETE FROM inventory WHERE user_id = ?", (member.id,))
        self.conn.commit()
        await ctx.send(f"🗑️ **Confiscated.** {member.mention}'s inventory has been erased.")

    # --- ERROR HANDLING ---
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'cog') and ctx.command.cog == self:
            if isinstance(error, commands.CheckFailure):
                await ctx.send("🦉 **You lack the authority to command me.** (ID Mismatch)")

async def setup(bot):
    await bot.add_cog(Admin(bot))