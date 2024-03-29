import datetime
import os
from json import load
from pathlib import Path
from re import findall
from typing import Dict, List, Tuple

import discord

from app.constants import CogsConstants as cogconstants
from app.constants import Emojis as constants
from app.constants import LogTypes as logconstants


def check_message_has_link(message: str, allowed_links: List[str]) -> List[str]:
    links = [
        link
        for link in findall(
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            message.content.lower(),
        )
        if not any(allowed.lower() in link.lower() for allowed in allowed_links)
    ]

    return links


# TODO: maybe use cache instead of read file every time
def parse_json_to_dict(key: str, locale: str, file: str) -> Dict[str, str]:
    file = Path.joinpath(
        Path().absolute(), "app", "resources", str(locale).lower(), key, file
    )
    with open(file, "r") as f:
        return load(f)


def get_guild_text_channels_id(guild, channels: list) -> List[str]:
    return [
        str(discord.utils.get(guild.channels, name=channel).id) for channel in channels
    ]


def get_text_channels_by_guild(guild: discord.Guild) -> Dict[str, str]:
    return {channel.name: str(channel.id) for channel in guild.text_channels}


def get_roles_by_guild(guild: discord.Guild) -> Dict[str, str]:
    return {role.name: str(role.id) for role in guild.roles if role.name != "@everyone"}


def get_available_roles_by_guild(guild: discord.Guild) -> Dict[str, str]:
    return {
        role.name: str(role.id)
        for role in guild.roles
        if role.name != "@everyone"
        and guild.me.top_role.position > role.position
        and not role.managed
    }


def list_roles_id(roles: List[discord.Role]) -> List[int]:
    return [str(role.id) for role in roles]


def check_two_lists_intersection(x: list, y: list) -> bool:
    return bool(set(x).intersection(y))


def check_answer_message(ctx, message) -> bool:
    return message.author == ctx.author and message.channel == ctx.channel


def parse_form_cogs_titles(form_json: List[Dict[str, str]]) -> Dict[str, str]:
    return {
        item["key"]: item["title"]
        for item in form_json
        if item["key"] not in ["form", "confirm"]
    }


def parse_cog_data_to_param_result(
    cog_data: List[Dict[str, str]], form_json: Dict[str, str]
) -> List[Dict[str, str]]:
    cogs_title = parse_form_cogs_titles(form_json)
    response = [
        {"title": cogs_title[cog_key], "value": value}
        for cog_key, value in cog_data.items()
        if cogs_title.get(cog_key)
    ]
    return response


def get_cog_with_title(
    cog_data: List[Dict[str, str]], form_json: Dict[str, str]
) -> Dict[str, str]:
    cogs_title = parse_form_cogs_titles(form_json)
    response = {
        cogs_title[cog_key]: cog_key for cog_key in cog_data if cogs_title.get(cog_key)
    }
    return response


def parse_form_params_result(responses: List[Dict[str, str]]) -> str:
    result = []
    for item in responses:
        values = item.get("value", [])

        if not values:
            values = "-"
        elif not isinstance(values, str):
            values = ", ".join(values)

        result.append(f"\n{constants.FRISBEE_EMOJI} {item['title']}: **{values}**")

    return "".join(result)


def parse_locale(locale: str) -> str:
    return str(locale).split("-")[0]


def parse_command_event_description(
    description: str, interaction_date: datetime.datetime, command_name: str, user: str
) -> str:
    description = description.replace("$command_name", command_name)
    description = description.replace(
        "$date", interaction_date.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    )
    description = description.replace("$user", user)
    return description


def format_traceback_message(traceback: str) -> str:
    if traceback == "NoneType: None\n":
        return None

    tb = traceback
    if len(tb.split("\n")) > 15:
        tb = "\n".join(tb.split("\n")[-15:])
        tb_formatted = tb
        if len(tb_formatted) > 3000:
            tb_formatted = "...\n" + tb_formatted[-3000:]
        return tb_formatted
    return tb


def get_cogs_folder() -> List[str]:
    directory = "app/cogs"
    cogs = []

    for filename in os.listdir(directory):
        if filename.startswith("_"):
            continue

        if filename.endswith(".py"):
            filename = filename[:-3]

        if filename in cogconstants.LAZY_LOAD_COGS:
            continue

        cogs.append(filename)

    return cogs


async def cogs_manager(bot, mode: str, cogs: list[str], sync: bool = False) -> None:
    from app import logger

    for cog in cogs:
        cog = f"app.cogs.{cog}" if "app" not in cog else cog

        if mode == "unload":
            await bot.unload_extension(cog)

        elif mode == "load":
            await bot.load_extension(cog)

        elif mode == "reload":
            await bot.reload_extension(cog)
        else:
            raise ValueError("Invalid mode.")

    cogs_list = ", ".join(cogs)
    logger.info(f"Cogs {cogs_list} {mode}ed.", log_type=logconstants.COMMAND_INFO_TYPE)

    if sync:
        await bot.tree.sync()


def format_datetime_output(datetime) -> str:
    days, seconds = datetime.days, datetime.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return f"{days}d {hours}h {minutes}m {seconds}s"


def parse_log_filename_with_date(
    filename: str, year: str, month: str, day: str
) -> Tuple[str, str]:
    if not (day and month and year):
        return filename, ""

    date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    return filename, date
