from typing import Callable

import discord
from i18n import t

from app.components.select import Select
from app.services.utils import parse_form_cogs_titles, parse_json_to_dict
from app.views.form import Form


class EditCommand(discord.ui.View):
    def __init__(self, command_key: str, locale: str, callback: Callable):
        self.command_key = command_key
        self.locale = locale
        self.after_callback = callback
        self.form_view = Form(self.command_key, self.locale)
        super().__init__()
        self.add_item(
            Select(
                t("commands.command-event.edit.placeholder", locale=self.locale),
                self.get_command_options(),
            )
        )

    def get_command_options(self):
        form_json = parse_json_to_dict(self.command_key, self.locale, "forms.json")
        return parse_form_cogs_titles(form_json)

    async def callback(self, interaction: discord.Interaction):
        self.form_view.filter_questions(self.selected_options)
        self.form_view._set_after_callback(self.after_callback)
        await self.form_view._callback(interaction)
