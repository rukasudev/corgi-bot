from app.bot import DiscordBot
from app.cogs.admin import Admin
from app.cogs.admin.cogs import Cogs
from app.cogs.admin.logs import DiscordLogsHandler
from app.cogs.events import Events
from app.cogs.moderations import Moderations
from app.cogs.moderations.block import Block
from app.cogs.moderations.roles import Roles
from app.cogs.notifications import Notifications
from app.cogs.notifications.twitch import Twitch


async def setup(bot: DiscordBot) -> None:
    DiscordLogsHandler(bot)

    moderations = Moderations(bot)

    moderations.app_command.add_command(Block(bot))
    moderations.app_command.add_command(Roles(bot))

    admin = Admin(bot)
    admin.app_command.add_command(Cogs(bot))

    notifications = Notifications(bot)
    notifications.app_command.add_command(Twitch())

    await bot.add_cog(moderations)
    await bot.add_cog(admin)
    await bot.add_cog(notifications)
    await bot.add_cog(Events(bot))
