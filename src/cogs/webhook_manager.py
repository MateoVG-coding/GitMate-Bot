import requests
from io import BytesIO
import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, option

class WebhookManager(commands.Cog):
    """This class contains all the slash commands related to webhooks"""

    def __init__(self, bot):
        """Special method when the cog is loaded"""
        self.bot = bot

    webhook_mang = SlashCommandGroup(
        "webhook", "Manage GitHub webhooks for your Discord channels and receive updates from your repositories")
    
    @webhook_mang.command(name='create', description='Create a webhook for a Discord channel')
    @option("channel", description="Enter the channel for this webhook")
    @option("name", description="Enter the name for the webhook")
    @option("icon-url", description="Enter the icon URL for this webhook", required=False)
    async def create_webhook(self, ctx, channel: discord.TextChannel, name, icon_url):
        """Command to create a webhook"""

        if not channel.permissions_for(ctx.author).manage_webhooks:
            return await ctx.send("😕 *Sorry, it seems you do not have permission to manage webhooks in this channel.*")

        if icon_url:
            if not is_valid_icon_url(icon_url):
                return await ctx.respond("❌ *Sorry, it seems the icon url you provided is invalid.*", ephemeral=True)

            response = requests.get(icon_url)
            icon_bytes = BytesIO(response.content)
            avatar = icon_bytes.read()
        else:
            icon_bytes = None

        webhook = await channel.create_webhook(name=name, avatar=avatar)
        body = f"""◉ **Url:** ```{webhook.url}```
               ◉ **Channel:** {channel.mention}"""

        embed = discord.Embed(colour=0x541dd3, description=body)
        embed.set_author(name=f"Webhook {webhook.name}",
                        url=f"{webhook.url}", icon_url=icon_url)

        await ctx.respond(embed=embed, ephemeral=True)
    
def is_valid_icon_url(url):
    """Function to check if the icon url is valid"""
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

def setup(bot):
    """Function to setup the cog"""
    bot.add_cog(WebhookManager(bot))