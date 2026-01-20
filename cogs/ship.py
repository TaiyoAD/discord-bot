import discord
from discord.ext import commands
import random
import io
from utils.image_generator import create_wanted_poster

class Ship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member = None):
        # Logic to determine who is being shipped
        if user2 is None:
            # If only one person mentions, ship Author x User1
            target1 = ctx.author
            target2 = user1
        else:
            # If two people mentioned, ship User1 x User2
            target1 = user1
            target2 = user2

        # Wan Shi Tong hates wasting time (Self-ship check)
        if target1 == target2:
            await ctx.send("Do not waste my time. You cannot judge your own spirit alone.")
            return

        # 1. Logic
        match_percentage = random.randint(0, 100)
        
        # Uppercase names for the poster
        name1 = target1.display_name.upper()
        name2 = target2.display_name.upper()

        # 2. Get Avatars
        avatar1 = await target1.display_avatar.with_format("png").read()
        avatar2 = await target2.display_avatar.with_format("png").read()

        # 3. Generate Image (The Wanted Poster)
        async with ctx.typing():
            final_image = await self.bot.loop.run_in_executor(
                None, 
                create_wanted_poster, 
                avatar1, 
                avatar2, 
                name1, 
                name2, 
                match_percentage
            )

        # 4. Send Result (Wan Shi Tong Flavor Text)
        with io.BytesIO() as image_binary:
            final_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            
            # Text logic based on percentage
            if match_percentage > 85:
                msg = f"⚠️ **HIGH THREAT LEVEL DETECTED**\n**Subjects:** {target1.mention} & {target2.mention}\n**Affinity: {match_percentage}%**\n*These spirits are dangerous together. I shall add them to the prohibited list.*"
            elif match_percentage < 35:
                msg = f"📉 **Inconsequential.**\n**Subjects:** {target1.mention} & {target2.mention}\n**Affinity: {match_percentage}%**\n*Their connection is weak. Unworthy of the archives.*"
            else:
                msg = f"⚖️ **Judgement Delivered.**\n**Subjects:** {target1.mention} & {target2.mention}\n**Affinity: {match_percentage}%**\n*An average pairing. Do not disturb me again.*"
                
            await ctx.send(content=msg, file=discord.File(fp=image_binary, filename='judgement.png'))

async def setup(bot):
    await bot.add_cog(Ship(bot))