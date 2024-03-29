import traceback

import discord
from discord.ext import commands
from i18n import t

from app import logger
from app.bot import DiscordBot
from app.constants import LogTypes as logconstants
from app.services import utils
from app.services.cache import increment_redis_key
from app.services.moderations import insert_error_by_command


class Errors(commands.Cog, name="errors"):
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ) -> None:
        await self.send_default_error_message(interaction)

        tb = traceback.format_exc()
        tb_formatted = utils.format_traceback_message(tb)

        error_message = f"The following command raised an exception: **{interaction.command.qualified_name}**```{type(error.original).__name__}: {error.original}```\n**Traceback**```{tb_formatted}```"
        logger.error(
            error_message,
            interaction=interaction,
            log_type=logconstants.COMMAND_ERROR_TYPE,
        )

        await insert_error_by_command(interaction.command._attr, error_message)

    @commands.Cog.listener()
    async def on_command_error(
        self,
        context: commands.Context,
        error: discord.app_commands.AppCommandError,
    ):
        if isinstance(error, commands.CommandNotFound):
            message = "🇧🇷 Português: Ops! 🐾 Parece que você está tentando fazer Keiko entender comandos com prefixo. 🐶 Lembre-se de usar as barras `(/)` para brincar com Keiko. Experimente digitar `/ajuda` para ver todas as brincadeiras disponíveis!\n\n"
            message += "🇺🇸 English: Oops! 🐾 It seems like you're trying to make Keiko understand commands with a prefix. 🐶 Remember to use slashes `(/)` to play with Keiko. Try typing `/help` to see all the fun tricks available!"

            return await context.send(message)

        error_message = f"Ignoring exception at **{context.message.content}**:\n{error}"
        logger.warn(
            error_message,
            log_type=logconstants.COMMAND_WARN_TYPE,
        )

    async def send_default_error_message(
        self, interaction: discord.Interaction
    ) -> None:
        default_error_message = t(
            "errors.command-generic-error.message",
            locale=utils.parse_locale(interaction.locale),
        )

        if interaction.response.is_done():
            await interaction.edit_original_response(content=default_error_message)
        else:
            await interaction.response.send_message(content=default_error_message)

        increment_redis_key(
            f"{logconstants.COMMAND_ERROR_TYPE}:{interaction.command._attr}"
        )


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Errors(bot))
