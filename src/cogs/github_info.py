import datetime
import requests
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, option

BASE_URL = "https://api.github.com"

class GithubLink(discord.ui.View):
    """This class add button to embedded messages"""
    def __init__(self, _url: str, _label: str):
        super().__init__()

        self.add_item(discord.ui.Button(label=_label, url=_url,
                                        style=discord.ButtonStyle.url, emoji="🔍"))

class GithubInfo(commands.Cog):
    """This class contains all the slash commands related to github information"""

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
        r = requests.get(url, timeout=30)

        if r.status_code == 200:
            data = r.json()
            date = datetime.datetime.strptime(data['commit']['committer']['date'],
                                               "%Y-%m-%dT%H:%M:%SZ")
            date.strftime('%A %b %d, %Y at %H:%M GMT')
            body = f"""◉ **Author:** [{data['author']['login']}]({data['author']['html_url']})
                       ◉ **Message:** `{data['commit']['message']}`
                       ◉ **Created at:** `{date}`"""
            embed = discord.Embed(colour=0x541dd3, description=body)
            embed.set_author(name=f"Commit {ref}" ,
                            url=data['html_url'])
            embed.set_thumbnail(url=data['author']['avatar_url'])
            await ctx.respond(embed=embed, view=GithubLink(data['html_url'], "Check commit"))
        else:
            await ctx.respond("Sorry! I could not find the commit you requested.")

    @gh_info.command(name='branches', description='Get list of branches in a repository')
    @option("owner", description="Enter the owner of the repository")
    @option("repo", description="Enter the name of the repository")
    async def list_branches_info(self, ctx, owner, repo):
        """Command to get list of branches in repo"""
        url = f"{BASE_URL}/repos/{owner}/{repo}/branches"
        r = requests.get(url, timeout=30)

        if r.status_code == 200:
            data = r.json()
            list_branches = ""
            for item in data:
                list_branches += f"📍`{item['name']}`\n\n"
            embed = discord.Embed(colour=0x541dd3,  description= list_branches)
            embed.set_author(name=f"Repository {repo}" ,
                            url=f"https://github.com/{owner}/{repo}")
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("Sorry! I could not find the repository you requested.")

    @gh_info.command(name='issue', description='Get detailed information on an issue')
    @option("owner", description="Enter the owner of the repository")
    @option("repo", description="Enter the name of the repository")
    @option("issue number", description="Enter the issue number")
    async def issue_info(self, ctx, owner, repo, issue_number):
        """Command to get issue information"""
        url = f"{BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}"
        r = requests.get(url, timeout=30)

        if r.status_code == 200:
            data = r.json()
            date_open = datetime.datetime.strptime(data['created_at'],
                                               "%Y-%m-%dT%H:%M:%SZ")
            date_open.strftime('%A %b %d, %Y at %H:%M GMT')
            body = f"""◉ **Author:** [{data['user']['login']}]({data['user']['html_url']})
                       ◉ **Description:** ```{data['body']}```
                       ◉ **Created at:** `{date_open}`
                       ◉ **State:** `{data['state']}`"""
            if data['state'] == 'closed':
                date_closed = datetime.datetime.strptime(data['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
                date_closed.strftime('%A %b %d, %Y at %H:%M GMT')
                body += f"""\n◉ **Closed by:** [{data['closed_by']['login']}](
                                {data['closed_by']['html_url']})
                            ◉ **Closed at:** `{date_closed}`"""
            embed = discord.Embed(colour=0x541dd3, description=body)
            embed.set_author(name=f"Issue {data['number']}, {data['title']}" ,
                            url=data['html_url'])
            embed.set_thumbnail(url=data['user']['avatar_url'])

            await ctx.respond(embed=embed, view=GithubLink(data['html_url'], "Check issue"))
        else:
            await ctx.respond("Sorry! I could not find the issue you requested.")

    @gh_info.command(name='release', description='Get detailed information on an release')
    @option("owner", description="Enter the owner of the repository")
    @option("repo", description="Enter the name of the repository")
    @option("tag", description="Enter the tag name")
    async def release_info(self, ctx, owner, repo, tag):
        """Command to get release information"""
        url = f"{BASE_URL}/repos/{owner}/{repo}/releases/tags/{tag}"
        r = requests.get(url, timeout=30)

        if r.status_code == 200:
            data = r.json()
            date_open = datetime.datetime.strptime(data['created_at'],
                                               "%Y-%m-%dT%H:%M:%SZ")
            date_open.strftime('%A %b %d, %Y at %H:%M GMT')
            date_published = datetime.datetime.strptime(data['published_at'],"%Y-%m-%dT%H:%M:%SZ")
            date_published.strftime('%A %b %d, %Y at %H:%M GMT')
            body = f"""◉ **Tag:** `{data['tag_name']}`
                       ◉ **Description:** ```{data['body']}```
                       ◉ **Author:** [{data['author']['login']}]({data['author']['html_url']})
                       ◉ **Created at:** `{date_open}`
                       ◉ **Published at:** `{date_published}`
                       ◉ **Assets:**\n[Source code (zip)]({data['zipball_url']})
                            [Source code (tar)]({data['tarball_url']})\n"""
            embed = discord.Embed(colour=0x541dd3, description=body)
            embed.set_author(name=f"Release {data['name']}" ,
                            url=data['html_url'])

            await ctx.respond(embed=embed, view=GithubLink(data['html_url'], "Check release"))
        else:
            await ctx.respond("Sorry! I could not find the issue you requested.")

def setup(bot):
    """Function to setup the cog"""
    bot.add_cog(GithubInfo(bot))