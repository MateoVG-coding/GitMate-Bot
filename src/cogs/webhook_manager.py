import requests
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
    async def create_webhook(self, ctx, channel: discord.TextChannel, name):
        """Command to create a webhook"""

        if not channel.permissions_for(ctx.author).manage_webhooks:
            return await ctx.send("😕 *Sorry, it seems you do not have permission to manage webhooks in this channel.*")

        webhook = await channel.create_webhook(name=name)
        body = f"""◉ **Url:** ```{webhook.url}```
                   ◉ **Id:** `{webhook.id}`
                   ◉ **Channel:** {channel.mention}"""

        embed = discord.Embed(colour=0x541dd3, description=body)
        embed.set_author(name=f"Webhook {webhook.name}",
                        url=f"{webhook.url}")

        await ctx.respond(embed=embed, ephemeral=True)

    @webhook_mang.command(name='delete', description='Delete a webhook by URL')
    @option("channel", description="Enter the channel of this webhook")
    @option("id", description="Enter the ID of the webhook to delete")
    async def delete_webhook(self, ctx, channel: discord.TextChannel, webhook_id):
        """Command to delete a webhook by URL"""

        if not channel.permissions_for(ctx.author).manage_webhooks:
            return await ctx.send("😕 *Sorry, it seems you do not have permission to manage webhooks in this channel.*")

        await ctx.bot.http.request(discord.http.Route('DELETE', f'/webhooks/{webhook_id}'))
        await ctx.respond("✅ *Webhook deleted successfully!*", ephemeral=True)

def is_valid_icon_url(url):
    """Function to check if the icon url is valid"""
    try:
        response = requests.head(url, timeout=30)
        return response.status_code == 200
    except requests.RequestException:
        return False

def setup(bot):
    """Function to setup the cog"""
    bot.add_cog(WebhookManager(bot))