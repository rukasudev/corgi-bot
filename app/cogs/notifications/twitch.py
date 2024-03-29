import discord
from discord import app_commands
from discord.app_commands import locale_str


class Twitch(app_commands.Group, name=locale_str("twitch", namespace="commands")):
    @app_commands.command(
        name=locale_str("twitch-activate", namespace="commands"),
        description=locale_str("twitch-activate-desc", namespace="commands"),
    )
    async def _sync(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello!")
