import os
import discord
from dotenv import load_dotenv

load_dotenv()
bot = discord.Bot()

bot.load_extension('cogs.github_info')

@bot.event
async def on_ready():
    """Function to notify when the bot is online"""
    print(f"{bot.user} is ready and online!")

bot.run(os.getenv('TOKEN'))
