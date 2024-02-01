import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, option
import requests

BASE_URL = "https://api.github.com"

class GithubInfo(commands.Cog):
    """This is class contains all the slash commands related to github information"""

    def __init__(self, bot):
        """Special method when the cog is loaded"""
        self.bot = bot

    gh_info = SlashCommandGroup(
        "info", "Get detailed information about commits, users, repositories, and more...")

    @gh_info.command(name='commit', description='Get detailed information on a commit')
    @option("owner", description="Enter the owner of the repository")
    @option("repo", description="Enter the name of the repository")
    @option("ref", description="Enter the SHA of the commit")
    async def commit_info(self, ctx, owner, repo, ref):
        """Command to get commit information"""
        url = f"{BASE_URL}/repos/{owner}/{repo}/commits/{ref}"
        r = requests.get(url, timeout=20)

        if r.status_code == 200:
            data = r.json()
            embed = discord.Embed(colour=0x541dd3)
            embed.set_author(name=f"Commit {data['sha']}" ,
                            url=data['html_url'])
            embed.add_field(name="Author",
                            value=f"{data['author']['login']}\n{data['author']['html_url']}",
                            inline=False)
            embed.add_field(name="Message",
                            value=f"{data['commit']['message']}",
                            inline=False)
            embed.add_field(name="Date commit",
                            value=f"{data['commit']['committer']['date']}",
                            inline=False)
            embed.set_thumbnail(url=data['author']['avatar_url'])
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("Sorry! I could not find the commit you requested.")

def setup(bot):
    """Function to setup the cog"""
    bot.add_cog(GithubInfo(bot))