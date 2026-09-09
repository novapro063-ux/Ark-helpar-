import discord
from discord.ext import commands
import json
import os
import asyncio

DATA_FILE = 'commands_data.json'

# ডেটা সেভ ও লোড করার ফাংশন
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ড্যাশবোর্ডের বাটন সিস্টেম
class DashboardView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="➕ নতুন কমান্ড বানান", style=discord.ButtonStyle.success)
    async def add_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📝 **দয়া করে ট্রিগারটি লিখুন** (যেটা লিখলে বট রিপ্লাই দেবে, যেমন: hello)।\n*আপনার কাছে ৬০ সেকেন্ড সময় আছে।*", ephemeral=True)
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            # ট্রিগার নেওয়া হচ্ছে
            trigger_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
            trigger = trigger_msg.content.lower()
            
            await interaction.followup.send("🖼️ **এবার রিপ্লাই দিন!**\nআপনি চাইলে কোনো টেক্সট, **GIF এর লিংক** দিতে পারেন। অথবা এই মেসেজেই সরাসরি **ছবি বা GIF আপলোড** করতে পারেন।", ephemeral=True)
            
            # রিপ্লাই নেওয়া হচ্ছে (ছবি সহ)
            reply_msg = await self.bot.wait_for('message', check=check, timeout=120.0)
            
            reply_text = reply_msg.content
            image_url = None
            
            # কেউ যদি সরাসরি চ্যানেল থেকে ছবি/GIF আপলোড করে
            if reply_msg.attachments:
                image_url = reply_msg.attachments[0].url
            
            # ডেটাবেসে সেভ করা
            data = load_data()
            data[trigger] = {
                "text": reply_text,
                "image": image_url
            }
            save_data(data)
            
            await interaction.followup.send(f"✅ **সফলভাবে সেভ হয়েছে!**\n**ট্রিগার:** `{trigger}`\n**ছবি/GIF:** {'যোগ করা হয়েছে 🖼️' if image_url else 'শুধু টেক্সট 📝'}", ephemeral=True)
            
            # সিকিউরিটির জন্য ইউজারের পাঠানো মেসেজগুলো ডিলিট করে দেওয়া
            await trigger_msg.delete()
            await reply_msg.delete()
            
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ সময় শেষ! আবার ড্যাশবোর্ড থেকে চেষ্টা করুন।", ephemeral=True)

    @discord.ui.button(label="🗑️ কমান্ড মুছুন", style=discord.ButtonStyle.danger)
    async def del_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🗑️ **যে ট্রিগারটি মুছতে চান সেটি লিখুন:**", ephemeral=True)
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
            
        try:
            del_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
            trigger = del_msg.content.lower()
            
            data = load_data()
            if trigger in data:
                del data[trigger]
                save_data(data)
                await interaction.followup.send(f"✅ `{trigger}` সফলভাবে ডিলিট করা হয়েছে।", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ এই নামে কোনো কমান্ড পাওয়া যায়নি।", ephemeral=True)
                
            await del_msg.delete()
                
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ সময় শেষ!", ephemeral=True)

# মূল Cog ক্লাস
class AutoReplyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # হাইব্রিড কমান্ড (স্ল্যাশ / এবং প্রেফিক্স ! দুটোই কাজ করবে)
    @commands.hybrid_command(name="dashboard", description="Auto-Reply ড্যাশবোর্ড ওপেন করুন")
    @commands.has_permissions(administrator=True) # শুধু অ্যাডমিনরা ড্যাশবোর্ড আনতে পারবে
    async def dashboard(self, ctx: commands.Context):
        embed = discord.Embed(
            title="⚙️ Auto-Reply Dashboard", 
            description="নিচের বাটনগুলোতে ক্লিক করে খুব সহজেই অটো-রিপ্লাই বানান।\nআপনি **লিংক** অথবা সরাসরি **ছবি/GIF আপলোড** করেও রিপ্লাই বানাতে পারবেন।", 
            color=discord.Color.brand_green()
        )
        await ctx.send(embed=embed, view=DashboardView(self.bot))

    # ইউজার মেসেজ দিলে চেক করে রিপ্লাই দেওয়ার ইভেন্ট
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        data = load_data()
        content = message.content.lower()

        if content in data:
            reply_data = data[content]
            text = reply_data.get("text", "")
            image_url = reply_data.get("image", None)

            # টেক্সট এবং আপলোড করা ছবি থাকলে
            if text and image_url:
                await message.channel.send(content=f"{text}\n{image_url}")
            # শুধু টেক্সট বা লিংক থাকলে (ডিসকর্ড লিংকে এমনিতেই GIF প্রিভিউ করে দেয়)
            elif text:
                await message.channel.send(content=text)
            # শুধু সরাসরি ছবি আপলোড করা থাকলে
            elif image_url:
                await message.channel.send(content=image_url)

async def setup(bot):
    await bot.add_cog(AutoReplyCog(bot))
        
