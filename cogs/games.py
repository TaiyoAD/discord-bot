import discord
from discord.ext import commands
import random
import os
import pymongo

# --- MONGODB CONNECTION ---
MONGO_URL = os.environ.get("MONGO_URL")

if MONGO_URL:
    cluster = pymongo.MongoClient(MONGO_URL)
    db = cluster["SpiritLibrary"] 
    collection = db["UserData"]
    print("✅ Games Module Connected to Database.")
else:
    print("⚠️ GAMES ERROR: MONGO_URL missing.")
    cluster = None

def get_user_data(user_id):
    if not cluster: return None
    data = collection.find_one({"_id": user_id})
    if data is None:
        new_user = {
            "_id": user_id, 
            "hp": 1000, "max_hp": 1000, 
            "inventory": {"Cabbage": 2, "Spirit Token": 0}
        }
        collection.insert_one(new_user)
        return new_user
    return data

def update_db(user_id, data):
    if cluster: collection.update_one({"_id": user_id}, {"$set": data})

class Games(commands.Cog):
    """Survival & Risk. The Database lives here."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['inv', 'bag'])
    async def inventory(self, ctx):
        """Check your HP and Satchel."""
        data = get_user_data(ctx.author.id)
        if not data: return await ctx.send("The Library Database is offline.")

        status = "🟢 Healthy"
        if data['hp'] <= 0: status = "💀 SPIRIT BROKEN"
        elif data['hp'] < 300: status = "⚠️ Critical"

        inv_text = ""
        for item, count in data.get("inventory", {}).items():
            if count > 0: inv_text += f"**{item}:** x{count}\n"

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Satchel", color=0x3498db)
        embed.add_field(name="Status", value=status, inline=False)
        embed.add_field(name="❤️ HP", value=f"{data['hp']}/{data['max_hp']}", inline=False)
        embed.add_field(name="🎒 Loot", value=inv_text if inv_text else "Dust.", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def eat(self, ctx):
        """Eat a Cabbage (+300 HP)."""
        data = get_user_data(ctx.author.id)
        if data["inventory"].get("Cabbage", 0) > 0:
            data["inventory"]["Cabbage"] -= 1
            data["hp"] = min(data["max_hp"], data["hp"] + 300)
            update_db(ctx.author.id, data)
            await ctx.send(f"🥬 **Crunch.** Recovered HP. (Current: {data['hp']})")
        else:
            await ctx.send("You have no Cabbages! Use `~forage` to find some.")

    @commands.command()
    async def forage(self, ctx):
        """(Safe) Search the library gardens for food."""
        # This replaces the farming we removed from ship.py
        data = get_user_data(ctx.author.id)
        
        if random.random() < 0.6: # 60% chance to find food
            data["inventory"]["Cabbage"] = data["inventory"].get("Cabbage", 0) + 1
            update_db(ctx.author.id, data)
            await ctx.send("🥬 You searched the underbrush and found a **Cabbage**.")
        else:
            await ctx.send("🍃 You searched but found nothing but dry leaves.")

    @commands.command()
    async def scavenge(self, ctx):
        """(Hard) Hunt for Spirit Tokens. Risk of Damage."""
        data = get_user_data(ctx.author.id)
        if data['hp'] <= 0: return await ctx.send("💀 You are too weak. Eat first.")

        roll = random.randint(1, 100)
        if roll > 65: # Hard Win
            data["inventory"]["Spirit Token"] = data["inventory"].get("Spirit Token", 0) + 1
            embed = discord.Embed(description=f"**VICTORY!**\nFound: **Spirit Token**", color=0x2ecc71)
        else: # Loss
            dmg = random.randint(100, 300)
            data["hp"] = max(0, data["hp"] - dmg)
            embed = discord.Embed(description=f"**FAILURE.**\nA spirit attacked you! **-{dmg} HP**", color=0xe74c3c)

        update_db(ctx.author.id, data)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))