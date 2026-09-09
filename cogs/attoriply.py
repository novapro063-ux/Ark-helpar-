import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime

DATA_FILE = 'commands_data.json'

# Function to load and save data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Dashboard Button System
class DashboardView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="➕ Add New Command", style=discord.ButtonStyle.success)
    async def add_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📝 **Please type the trigger word** (e.g., rex).\n*You have 60 seconds.*", ephemeral=True)
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            trigger_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
            trigger = trigger_msg.content.lower()
            
            await interaction.followup.send("🖼️ **Now, send the reply!**\nYou can send text, a **GIF link**, or directly **upload an image/GIF** here.", ephemeral=True)
            
            reply_msg = await self.bot.wait_for('message', check=check, timeout=120.0)
            
            reply_text = reply_msg.content
            image_url = None
            
            if reply_msg.attachments:
                image_url = reply_msg.attachments[0].url
            
            data = load_data()
            data[trigger] = {
                "text": reply_text,
                "image": image_url
            }
            save_data(data)
            
            await interaction.followup.send(f"✅ **Successfully saved!**\n**Trigger:** `{trigger}`", ephemeral=True)
            
            await trigger_msg.delete()
            await reply_msg.delete()
            
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Time's up! Please try again from the dashboard.", ephemeral=True)

    @discord.ui.button(label="🗑️ Delete Command", style=discord.ButtonStyle.danger)
    async def del_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🗑️ **Type the trigger word you want to delete:**", ephemeral=True)
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
            
        try:
            del_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
            trigger = del_msg.content.lower()
            
            data = load_data()
            if trigger in data:
                del data[trigger]
                save_data(data)
                await interaction.followup.send(f"✅ `{trigger}` has been successfully deleted.", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ No command found with this trigger.", ephemeral=True)
                
            await del_msg.delete()
                
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Time's up!", ephemeral=True)

# Main Cog Class
class AutoReplyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. Dashboard Command
    @commands.hybrid_command(name="dashboard", description="Open the Auto-Reply Dashboard")
    @commands.has_permissions(administrator=True)
    async def dashboard(self, ctx: commands.Context):
        embed = discord.Embed(
            title="⚙️ Auto-Reply Management", 
            description="Manage your custom auto-replies below.\nYou can set text, links, or directly upload images/GIFs.", 
            color=discord.Color.dark_theme()
        )
        await ctx.send(embed=embed, view=DashboardView(self.bot))

    # 2. Help Command (Changed from arhelp to help)
    @commands.hybrid_command(name="help", description="List all available auto-reply commands")
    async def help_command(self, ctx: commands.Context):
        data = load_data()
        
        if not data:
            embed = discord.Embed(
                title="📜 Custom Commands List", 
                description="*No custom commands have been created yet.*", 
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        cmd_list = [f"• `{trigger}`" for trigger in data.keys()]
        description = "\n".join(cmd_list)[:4000]

        embed = discord.Embed(
            title="📜 Available Custom Commands",
            description=f"Here are the auto-reply triggers you can use in this server:\n\n{description}",
            color=discord.Color.teal()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Total Commands: {len(data)}")
        
        await ctx.send(embed=embed)

    # 3. Auto-Reply Event
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

            embed = discord.Embed(
                title=content.title(),
                description=text if text else None,
                color=discord.Color.teal()
            )
            
            if image_url:
                embed.set_image(url=image_url)
                
            footer_text = f"{message.author.display_name} | {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
            avatar_url = message.author.display_avatar.url if message.author.display_avatar else None
            embed.set_footer(text=footer_text, icon_url=avatar_url)

            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoReplyCog(bot))
    
