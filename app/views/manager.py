import discord

from app.components.buttons import DisableButtom, EditButtom
from app.views.edit import EditCommand
from app.services.moderations import delete_cog_by_guild, upsert_parameter_by_guild
from app.data import cogs as cogs_data
from app.services.utils import (
    parse_command_event_description,
    parse_locale,
    parse_json_to_dict,
    get_cog_with_title
)
from i18n import t


class Manager(discord.ui.View):
    """
    A custom view to create a form message with questions and
    save to database.

    Attributes:
        `command_key` -- the key of the form message from form.json file
    """

    def __init__(self, key: str, locale: str):
        self.command_key = key
        self.locale = locale
        super().__init__()
        self.add_item(EditButtom(callback=self.edit_callback, locale=locale))
        self.add_item(DisableButtom(callback=self.disable_callback, locale=locale))

    async def edit_callback(self, interaction: discord.Interaction):
        self.clear_items()

        view = EditCommand(self.command_key, self.locale)
        embed = interaction.message.embeds[0]

        await interaction.response.edit_message(embed=embed, view=view)

    async def disable_callback(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        embed = interaction.message.embeds[0]

        await upsert_parameter_by_guild(
            guild_id=guild_id, parameter=self.command_key, value=False
        )

        await delete_cog_by_guild(guild_id, self.command_key)

        embed.title = t("commands.command-event.disabled.title", locale=self.locale)
        embed.description = parse_command_event_description(
            t("commands.command-event.disabled.description", locale=self.locale),
            interaction.message.created_at,
            interaction.message.interaction.name,
            interaction.user.mention
        )
        self.clear_items()

        await interaction.response.send_message(embed=embed, view=self)
