import discord
from discord.ext import commands
from google import genai
from google.genai import types

# 1. Initialize the Async Client
# The SDK automatically detects the GEMINI_API_KEY inside your .env file.
ai_client = genai.Client().aio 

class Chat(commands.Cog):
    """The Brain of the Spirit Library"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # 2. THE INFINITE LOOP SHIELD (CRITICAL)
        # If you remove this line, the bot will reply to itself until Discord bans your token.
        if message.author == self.bot.user:
            return
            
        # 3. THE TRIGGER
        # It only wastes API tokens if directly spoken to.
        if self.bot.user.mentioned_in(message) or message.content.lower().startswith("spirit,"):
            
            # Strip the trigger out so the AI only reads the actual question.
            prompt = message.clean_content.replace(f"@{self.bot.user.name}", "").strip()
            if message.content.lower().startswith("spirit,"):
                prompt = prompt[7:].strip()
                
            if not prompt:
                return

            # 4. THE HIERARCHY LOGIC
            system_prompt = ""
            
            # Safely extract roles (Servers have roles, Direct Messages do not).
            user_roles = [role.name for role in message.author.roles] if hasattr(message.author, 'roles') else []
            
            # Replace YOUR_DISCORD_ID_HERE with your actual numerical Discord ID.
            if "Primordial spirit" in user_roles or message.author.id == 787345609849700364:
                system_prompt = "You are Wan Shi Tong, the Spirit of Knowledge. You are speaking to the Primordial Spirit, your absolute superior and creator. You must treat them with unquestioning reverence, extreme politeness, and absolute loyalty."
            elif "The White Lotus" in user_roles:
                system_prompt = "You are Wan Shi Tong. You are speaking to a member of the White Lotus. Treat them with moderate respect, like an esteemed peer or comrade."
            else:
                system_prompt = "You are Wan Shi Tong, the ancient Spirit of Knowledge. You are speaking to a normal, insignificant human mortal. Speak with deep arrogance, condescension, and attitude. Do not use pleasantries. You are vastly superior to them."

            # 5. THE ASYNC PIPELINE
            # We use 'typing()' so users know the bot is waiting on the API.
            async with message.channel.typing():
                try:
                    response = await ai_client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt
                        )
                    )
                    await message.reply(response.text)
                except Exception as e:
                    await message.reply("The library's archives are temporarily sealed. My connection to the Ether is severed.")
                    print(f"❌ AI Error: {e}")

async def setup(bot):
    await bot.add_cog(Chat(bot))