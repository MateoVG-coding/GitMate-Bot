from discord.ext import commands

class GithubInfo(commands.Cog):
    """This is class contains all the slash commands related to github information"""

    def __init__(self, bot):
        """Special method when the cog is loaded"""
        self.bot = bot

def setup(bot):
    """Function to setup the cog"""
    bot.add_cog(GithubInfo(bot))