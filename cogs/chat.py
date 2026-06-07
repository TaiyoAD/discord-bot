import asyncio
import discord
from discord.ext import commands
from google import genai
from google.genai import types

# Initialize the Async Client
ai_client = genai.Client().aio 

class Chat(commands.Cog):
    """The Brain of the Spirit Library"""
    def __init__(self, bot):
        self.bot = bot
        # This lock currently throttles your entire bot across all servers.
        # Consider a per-user or per-channel lock for future scaling.
        self.global_ai_lock = asyncio.Lock()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore self
        if message.author == self.bot.user:
            return
            
        # The Trigger
        if self.bot.user.mentioned_in(message) or message.content.lower().startswith("spirit,"):
            
            # Clean up the user's input
            prompt = message.clean_content.replace(f"@{self.bot.user.name}", "").strip()
            if message.content.lower().startswith("spirit,"):
                prompt = prompt[7:].strip()

            # --- THE MEMORY INJECTION PIPELINE ---
            reply_context = ""
            if message.reference and message.reference.message_id:
                try:
                    # Fetch the actual message the user replied to
                    replied_msg = await message.channel.fetch_message(message.reference.message_id)
                    if replied_msg.content:
                        speaker = "You (Wan Shi Tong)" if replied_msg.author == self.bot.user else replied_msg.author.display_name
                        reply_context = f"[Context - The user is replying to a message from {speaker} that said: \"{replied_msg.clean_content}\"]\n\n"
                except Exception as e:
                    print(f"⚠️ Memory Fetch Failed: {e}")

            # Stitch the past message and the new question together
            final_prompt = f"{reply_context}User's new message: {prompt}"
            
            # Drop empty prompts
            if not final_prompt.strip() or final_prompt.strip() == "User's new message:":
                return
            
            # --- THE HIERARCHY LOGIC ---
            system_prompt = ""
            user_roles = [role.name for role in message.author.roles] if hasattr(message.author, 'roles') else []
            
            if "Primordial spirit" in user_roles or message.author.id == 787345609849700364:
                system_prompt = "You are Wan Shi Tong, the Spirit of Knowledge. You are speaking to the Primordial Spirit, your absolute superior and creator. You must treat them with unquestioning reverence, extreme politeness, and absolute loyalty."
            elif "The White Lotus" in user_roles:
                system_prompt = "You are Wan Shi Tong. You are speaking to a member of the White Lotus. Treat them with moderate respect, like an esteemed peer or comrade."
            else:
                system_prompt = "You are Wan Shi Tong, the ancient Spirit of Knowledge. You are speaking to a normal, insignificant human mortal. Speak with deep arrogance, condescension, and attitude. Do not use pleasantries. You are vastly superior to them."

            # --- CONCURRENCY GATE ---
            async with self.global_ai_lock:
                async with message.channel.typing():
                    try:
                        # FIX: Passed final_prompt instead of prompt
                        response = await ai_client.models.generate_content(
                            model="gemini-2.5-flash-lite", 
                            contents=final_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=system_prompt
                            )
                        )
                        await message.reply(response.text)
                        
                    except Exception as e:
                        print(f"❌ AI Error: {e}")
                        if "429" in str(e):
                            await message.reply("The library archives are congested. Wait your turn.")
                        else:
                            await message.reply("The spiritual connection shattered. Try again.")
                            
                    # Rate limit protection
                    await asyncio.sleep(1) 

async def setup(bot):
    await bot.add_cog(Chat(bot))