import discord
from discord.ext import commands
import os

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        # এখানে help_command=None যুক্ত করা হয়েছে ডিফল্ট হেল্প বন্ধ করার জন্য
        super().__init__(command_prefix='.', intents=intents, help_command=None)

    async def setup_hook(self):
        if not os.path.exists('./cogs'):
            os.makedirs('./cogs')
            
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ Loaded Cog: {filename}")
        
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'🚀 Bot is online and ready as {bot.user}')

TOKEN = os.environ.get("BOT_TOKEN")

if TOKEN is None:
    print("❌ ERROR: BOT_TOKEN is missing!")
else:
    bot.run(TOKEN)
    
