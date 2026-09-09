import discord
from discord.ext import commands
import os

class MyBot(commands.Bot):
    def __init__(self):
        # বটের ইনটেন্ট সেটআপ (মেসেজ কন্টেন্ট পড়া এবং স্ল্যাশ কমান্ডের জন্য)
        intents = discord.Intents.default()
        intents.message_content = True
        
        # কমান্ড প্রেফিক্স '!' রাখা হয়েছে
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Cogs ফোল্ডার না থাকলে তৈরি করবে
        if not os.path.exists('./cogs'):
            os.makedirs('./cogs')
            
        # Cogs ফোল্ডার থেকে সব .py ফাইল (cog) লোড করবে
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ Loaded Cog: {filename}")
        
        # হাইব্রিড/স্ল্যাশ কমান্ডগুলো ডিসকর্ডের সাথে সিঙ্ক (Sync) করবে
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'🚀 Bot is online and ready as {bot.user}')

# Environment Variable থেকে টোকেন নেওয়া হচ্ছে
# হোস্টিং প্যানেলে Variable Name 'BOT_TOKEN' দিয়ে বটের টোকেনটি অ্যাড করুন
TOKEN = os.environ.get("BOT_TOKEN")

if TOKEN is None:
    print("❌ ERROR: BOT_TOKEN ভেরিয়েবলটি পাওয়া যায়নি! হোস্টিং প্যানেলে এটি অ্যাড করুন।")
else:
    # বট রান করা হচ্ছে
    bot.run(TOKEN)
    
