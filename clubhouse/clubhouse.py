import os
import string
from datetime import datetime
from typing import Optional, Iterable

import sentry_sdk
from PyDrocsid.database import db
from PyDrocsid.events import listener, register_cogs
from PyDrocsid.help import send_help
from PyDrocsid.translations import translations
from PyDrocsid.util import measure_latency, send_long_embed, send_editable_log
from discord import Message, Embed, User, Forbidden, Intents
from discord.ext import tasks
from discord.ext.commands import (
    Bot,
    Context,
    CommandError,
    guild_only, CommandNotFound,
)
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from cogs.clubhouse import Clubhouse

from colours import Colours
from info import CLUBHOUSE_ICON, CONTRIBUTORS, GITHUB_LINK, VERSION, AVATAR_URL, GITHUB_DESCRIPTION
from permissions import PermissionLevel
from util import get_prefix

banner = r"""
  ____ _       _     _                          
 / ___| |_   _| |__ | |__   ___  _   _ ___  ___ 
| |   | | | | | '_ \| '_ \ / _ \| | | / __|/ _ \
| |___| | |_| | |_) | | | | (_) | |_| \__ \  __/
 \____|_|\__,_|_.__/|_| |_|\___/ \__,_|___/\___|
 
""".splitlines()
print("\n".join(f"\033[1m\033[36m{line}\033[0m" for line in banner))
print(f"Starting Clubhouse v{VERSION} ({GITHUB_LINK})\n")

sentry_dsn = os.environ.get("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        attach_stacktrace=True,
        shutdown_timeout=5,
        integrations=[AioHttpIntegration(), SqlalchemyIntegration()],
        release=f"clubhouse@{VERSION}",
    )

db.create_tables()


async def fetch_prefix(_, message: Message) -> Iterable[str]:
    return await get_prefix(), f"<@!{bot.user.id}> ", f"<@{bot.user.id}> "


intents = Intents.all()

bot = Bot(command_prefix=fetch_prefix, case_insensitive=True, description=translations.bot_description, intents=intents)
bot.remove_command("help")
bot.initial = True


def get_owner() -> Optional[User]:
    owner_id = os.getenv("OWNER_ID")
    if owner_id and owner_id.isnumeric():
        return bot.get_user(int(owner_id))
    return None


@listener
async def on_ready():
    if (owner := get_owner()) is not None:
        try:
            await send_editable_log(
                owner,
                translations.online_status,
                translations.f_status_description(VERSION),
                translations.logged_in,
                datetime.utcnow().strftime("%d.%m.%Y %H:%M:%S UTC"),
                force_resend=True,
                force_new_embed=bot.initial,
            )
        except Forbidden:
            pass

    print(f"\033[1m\033[36mLogged in as {bot.user}\033[0m")

    if owner is not None:
        try:
            status_loop.start()
        except RuntimeError:
            status_loop.restart()

    bot.initial = False


@tasks.loop(seconds=20)
async def status_loop():
    if (owner := get_owner()) is None:
        return
    try:
        await send_editable_log(
            owner,
            translations.online_status,
            translations.f_status_description(VERSION),
            translations.heartbeat,
            datetime.utcnow().strftime("%d.%m.%Y %H:%M:%S UTC"),
        )
    except Forbidden:
        pass


@bot.command()
async def ping(ctx: Context):
    if ctx.author.bot:
        return
    """
    display bot latency
    """

    latency: Optional[float] = measure_latency()
    embed = Embed(title=translations.pong, colour=Colours.ping)
    if latency is not None:
        embed.description = translations.f_pong_latency(latency * 1000)
    await ctx.send(embed=embed)


# @bot.command(name="prefix")
# @PermissionLevel.ADMINISTRATOR.check
# @guild_only()
# async def change_prefix(ctx: Context, new_prefix: str):
#     """
#     change the bot prefix
#     """
#
#     if not 0 < len(new_prefix) <= 16:
#         raise CommandError(translations.invalid_prefix_length)
#
#     valid_chars = set(string.ascii_letters + string.digits + string.punctuation)
#     if any(c not in valid_chars for c in new_prefix):
#         raise CommandError(translations.prefix_invalid_chars)
#
#     await set_prefix(new_prefix)
#     embed = Embed(title=translations.prefix, description=translations.prefix_updated, colour=Colours.prefix)
#     await ctx.send(embed=embed)


async def build_info_embed(authorized: bool) -> Embed:
    embed = Embed(title="Clubhouse", colour=Colours.info, description=translations.bot_description)
    embed.set_thumbnail(url=CLUBHOUSE_ICON)
    prefix = await get_prefix()
    features = translations.features
    if authorized:
        features += translations.admin_features
    embed.add_field(
        name=translations.features_title,
        value="\n".join(f":small_orange_diamond: {feature}" for feature in features),
        inline=False,
    )
    embed.add_field(name=translations.author_title, value="<@212866839083089921>", inline=True)
    embed.add_field(name=translations.contributors_title, value=" ".join(f"<@{c}>" for c in CONTRIBUTORS), inline=True)
    embed.add_field(name=translations.version_title, value=VERSION, inline=True)
    embed.add_field(name=translations.github_title, value=GITHUB_LINK, inline=False)
    embed.add_field(name=translations.prefix_title, value=f"`{prefix}` or {bot.user.mention}", inline=True)
    embed.add_field(name=translations.help_command_title, value=f"`{prefix}help`", inline=True)
    embed.add_field(
        name=translations.bugs_features_title,
        value=translations.bugs_features,
        inline=False,
    )
    return embed


@bot.command(name="help")
async def help_cmd(ctx: Context, *, cog_or_command: Optional[str]):
    if ctx.author.bot:
        return
    """
    Shows this Message
    """
    try:
        await send_help(ctx, cog_or_command)
    except Exception as e:
        print()


@bot.command(name="github", aliases=["gh"])
async def github(ctx: Context):
    if ctx.author.bot:
        return
    """
    return the github link
    """

    embed = Embed(
        title="TNT2k/Clubhouse",
        description=GITHUB_DESCRIPTION,
        colour=Colours.github,
        url=GITHUB_LINK,
    )
    embed.set_author(name="GitHub", icon_url="https://github.com/fluidicon.png")
    embed.set_thumbnail(url=AVATAR_URL)
    await ctx.send(embed=embed)


@bot.command(name="version")
async def version(ctx: Context):
    if ctx.author.bot:
        return
    """
    show version
    """

    embed = Embed(title=f"Clubhouse Bot v{VERSION}", colour=Colours.version)
    await ctx.send(embed=embed)


@bot.command(name="info", aliases=["infos", "about"])
async def info(ctx: Context):
    if ctx.author.bot:
        return
    """
    show information about the bot
    """

    await send_long_embed(ctx, await build_info_embed(False))


@bot.event
async def on_error(*_, **__):
    if sentry_dsn:
        sentry_sdk.capture_exception()
    else:
        raise  # skipcq: PYL-E0704


@bot.event
async def on_command_error(ctx: Context, error: CommandError):
    if ctx.author.bot:
        return
    if ctx.guild is not None and ctx.prefix == await get_prefix():
        if isinstance(error, CommandNotFound) and ctx.guild is not None and ctx.prefix == await get_prefix():
            await ctx.send(f"Use {await get_prefix()}help to get help!")
        else:
            sentry_sdk.capture_exception(error)
            await ctx.send("Critical error, check sentry")
    return


@listener
async def on_bot_ping(message: Message):
    if message.author.bot:
        return
    await message.channel.send(embed=await build_info_embed(False))


enabled_cogs = [Clubhouse]
# for cog_class in COGS:
#     enabled_cogs.append(cog_class)

register_cogs(bot, *enabled_cogs)

if bot.cogs:
    print(f"\033[1m\033[32m{len(bot.cogs)} Cog{'s' * (len(bot.cogs) > 1)} enabled:\033[0m")
    for cog in bot.cogs.values():
        commands = ", ".join(cmd.name for cmd in cog.get_commands())
        print(f" + {cog.__class__.__name__}" + f" ({commands})" * bool(commands))

bot.run(os.environ["TOKEN"])
