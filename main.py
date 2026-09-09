import discord
from discord.ext import commands
import os

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        # কমান্ড প্রেফিক্স '!' রাখা হয়েছে
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Cogs ফোল্ডার থেকে সব cog লোড করবে
        if not os.path.exists('./cogs'):
            os.makedirs('./cogs')
            
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ Loaded Cog: {filename}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'🚀 Bot is online and ready as {bot.user}')

# Environment Variable থেকে টোকেন নেওয়া হচ্ছে
# হোস্টিং প্যানেলে ভেরিয়েবলের নাম অবশ্যই 'BOT_TOKEN' রাখতে হবে
TOKEN = os.environ.get("BOT_TOKEN")

if TOKEN is None:
    print("❌ ERROR: BOT_TOKEN ভেরিয়েবলটি পাওয়া যায়নি! হোস্টিং প্যানেলে এটি অ্যাড করুন।")
else:
    bot.run(TOKEN)
  
