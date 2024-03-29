import base64
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

    @gh_info.command(name='user', description='Get detailed information on a user')
    @option("username", description="Enter the username you are looking for")
    async def user_info(self, ctx, username):
        """Command to get user information"""
        url = f"{BASE_URL}/users/{username}"
        r = requests.get(url, timeout=30)

        if r.status_code == 200:
            data = r.json()
            body = f"◉ **Name:** {data['name']}\n◉ **Created at:** `{parse_date(data['created_at'])}`"

            if data['blog'] != "":
                body += f"\n◉ **Blog:** {data['blog']}"
            if data['bio']:
                body += f"\n◉ **Bio:** ```{data['bio']}```"

            body += f"""\n\n◉ **Repositories:** `{data['public_repos']}`\n◉ **Followers:** `{data['followers']}`\n◉ **Following:** `{data['following']}`\n"""

            if data['location']:
                body += f"\n◉ **Location:** 📍{data['location']}"

            embed = discord.Embed(colour=0x541dd3, description=body)
            embed.set_author(name=username,
                            url=data['html_url'])
            embed.set_thumbnail(url=data['avatar_url'])

            await ctx.respond(embed=embed, view=GithubLink(data['html_url'], "Check user"))
        else:
            await ctx.respond("🤔 *Sorry! I could not find the user you requested.*", ephemeral=True)

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
            body = f"""◉ **Author:** [{data['author']['login']}]({data['author']['html_url']})
◉ **Message:** ```{data['commit']['message']}```
◉ **Created at:** `{parse_date(data['commit']['committer']['date'])}`"""
            embed = discord.Embed(colour=0x541dd3, description=body)
            embed.set_author(name=f"Repository {repo}\nCommit {ref}" ,
                            url=data['html_url'])
            embed.set_thumbnail(url=data['author']['avatar_url'])

            await ctx.respond(embed=embed, view=GithubLink(data['html_url'], "Check commit"))
        else:
            await ctx.respond("🤔 *Sorry! I could not find the commit you requested.*", ephemeral=True)

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
            await ctx.respond("🤔 *Sorry! I could not find the repository you requested.*", ephemeral=True)

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
            body = f"""◉ **Author:** [{data['user']['login']}]({data['user']['html_url']})
◉ **Description:** ```{data['body'][:400] + "..."}```
◉ **Created at:** `{parse_date(data['created_at'])}`
◉ **State:** `{data['state']}`"""

            if data['state'] == 'closed':
                body += f"""\n◉ **Closed by:** [{data['closed_by']['login']}](
{data['closed_by']['html_url']})
◉ **Closed at:** `{parse_date(data['closed_at'])}`"""

            embed = discord.Embed(colour=0x541dd3, description=body)
            embed.set_author(name=f"Repository {repo}\nIssue {data['number']}, {data['title']}" ,
                            url=data['html_url'])
            embed.set_thumbnail(url=data['user']['avatar_url'])

            await ctx.respond(embed=embed, view=GithubLink(data['html_url'], "Check issue"))
        else:
            await ctx.respond("🤔 *Sorry! I could not find the issue you requested.*", ephemeral=True)

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
            body = f"""◉ **Tag:** `{data['tag_name']}`
◉ **Description:** ```{data['body'][:400] + "..."}```
◉ **Author:** [{data['author']['login']}]({data['author']['html_url']})
◉ **Created at:** `{parse_date(data['created_at'])}`
◉ **Published at:** `{parse_date(data['published_at'])}`
◉ **Assets:**\n[Source code (zip)]({data['zipball_url']})
[Source code (tar)]({data['tarball_url']})\n"""
            embed = discord.Embed(colour=0x541dd3, description=body)
            embed.set_author(name=f"Repository {repo}\nRelease {data['name']}" ,
                            url=data['html_url'])

            await ctx.respond(embed=embed, view=GithubLink(data['html_url'], "Check release"))
        else:
            await ctx.respond("🤔 *Sorry! I could not find the release you requested.*", ephemeral=True)

    @gh_info.command(name='file', description='Get content of a file in a repository')
    @option("owner", description="Enter the owner of the repository")
    @option("repo", description="Enter the name of the repository")
    @option("path", description="Enter the path of the file")
    async def file_info(self, ctx, owner, repo, path):
        """Command to get content file in repo"""
        url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        r = requests.get(url, timeout=30)

        if r.status_code == 200:
            data = r.json()

            if isinstance(data, list):
                return await ctx.respond("❌ *Sorry, it seems the path you provided leads to a folder rather than a file.*", ephemeral=True)

            file_content = data['content']
            file_content_encoding = data.get('encoding')

            if file_content_encoding == 'base64':
                file_content = base64.b64decode(file_content).decode()[:600] + "..."

            body = f"""◉ **Type:** `{data['type']}`
                       ◉ **Path:** `{data['path']}`
                       ◉ **Content:** ```{file_content}```
                       [Get file]({data['download_url']})"""

            embed = discord.Embed(colour=0x541dd3, description=body)
            embed.set_author(name=f"Repository {repo}\nFile {data['name']}" ,
                            url=data['html_url'])

            await ctx.respond(embed=embed, view=GithubLink(data['html_url'], "Check file"))
        else:
            await ctx.respond("🤔 *Sorry! I could not find the file you requested.*", ephemeral=True)

    @gh_info.command(name='folder', description='Get content of a folder in a repository')
    @option("owner", description="Enter the owner of the repository")
    @option("repo", description="Enter the name of the repository")
    @option("path", description="Enter the path of the folder")
    async def folder_info(self, ctx, owner, repo, path):
        """Command to get content of folder in repo"""
        url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        r = requests.get(url, timeout=30)

        if r.status_code == 200:
            data = r.json()
            file_tree = ""

            for item in data:
                if item['type'] == "dir":
                    file_tree += f"📁 [`{item['name']}`]({item['html_url']})\n"
                else:
                    file_tree += f"📄 [{item['name']}]({item['html_url']})\n"

            embed = discord.Embed(colour=0x541dd3,  description= f"**{path}**\n {file_tree}")
            embed.set_author(name=f"Repository {repo}" ,
                            url=f"https://github.com/{owner}/{repo}")

            await ctx.respond(embed=embed)
        else:
            await ctx.respond("🤔 *Sorry! I could not find the folder you requested.*", ephemeral=True)

    @gh_info.command(name='workflows', description='Get list of workflows in a repository')
    @option("owner", description="Enter the owner of the repository")
    @option("repo", description="Enter the name of the repository")
    async def list_workflows_info(self, ctx, owner, repo):
        """Command to get list of workflows in repo"""
        url = f"{BASE_URL}/repos/{owner}/{repo}/actions/workflows"
        r = requests.get(url, timeout=30)

        if r.status_code == 200:
            data = r.json()
            list_workflows = ""

            for item in data['workflows']:
                list_workflows += f"""⚙️  [`{item['name']}`]({item['html_url']})
                  **({item['state']})**\n"""

            embed = discord.Embed(colour=0x541dd3,
                                  description="**Workflows:**\n\n" + list_workflows)
            embed.set_author(name=f"Repository {repo}" ,
                            url=f"https://github.com/{owner}/{repo}")

            await ctx.respond(embed=embed)
        else:
            await ctx.respond("🤔 *Sorry! I could not find the repository you requested.*", ephemeral=True)

    @gh_info.command(name='pull-request', description='Get detailed information on a pull request')
    @option("owner", description="Enter the owner of the repository")
    @option("repo", description="Enter the name of the repository")
    @option("ref", description="Enter the number of the pull request")
    async def pull_request_info_command(self, ctx, owner, repo, ref):
        """Command to get pull request information"""
        url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{ref}"
        r = requests.get(url, timeout=30)

        if r.status_code == 200:
            data = r.json()
            body = f"""◉ **Author:** [{data['user']['login']}]({data['user']['html_url']})
◉ **Title:** {data['title']}
◉ **Description:** ```{data['body']}```
◉ **State:** `{data['state']}`
◉ **Created at:** `{parse_date(data['created_at'])}`"""

            if data['state'] == "closed":
                body += f"""\n◉ **Merged at:** `{parse_date(data['merged_at'])}`
                              ◉ **Closed at:** `{parse_date(data['closed_at'])}`"""

            body += f"""\n\n This pull request has **{data['changed_files']} changed files**, **{data['additions']} additions**, **{data['deletions']} deletions**, and **{data['commits']} commits**."""
            embed = discord.Embed(colour=0x541dd3, description=body)
            embed.set_author(name=f"Repository {repo}\nPull request {data['number']} " ,
                            url=data['html_url'])
            embed.set_thumbnail(url=data['user']['avatar_url'])

            await ctx.respond(embed=embed, view=GithubLink(data['html_url'], "Check pull request"))
        else:
            await ctx.respond("🤔 *Sorry! I could not find the pull request you requested.*", ephemeral=True)

def setup(bot):
    """Function to setup the cog"""
    bot.add_cog(GithubInfo(bot))

def parse_date(date_string):
    """Function to parse date from Github API format"""
    try:
        date_obj = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime('%A %b %d, %Y at %H:%M GMT')
    except ValueError:
        return "Invalid date format"
