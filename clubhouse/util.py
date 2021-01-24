import re
from typing import Optional

from PyDrocsid.settings import Settings
from PyDrocsid.translations import translations
from discord import Embed
from discord.ext.commands import ColorConverter, BadArgument

from colours import Colours


class Color(ColorConverter):
    async def convert(self, ctx, argument: str) -> Optional[int]:
        try:
            return await super().convert(ctx, argument)
        except BadArgument:
            pass

        if not re.match(r"^[0-9a-fA-F]{6}$", argument):
            raise BadArgument(translations.invalid_color)
        return int(argument, 16)


def make_error(message) -> Embed:
    return Embed(title=translations.error, colour=Colours.error, description=str(message))


async def get_prefix() -> str:
    return await Settings.get(str, "prefix", ".")

#
# async def set_prefix(new_prefix: str):
#     await Settings.set(str, "prefix", new_prefix)
