#!/usr/bin/env python3

"""ram.moe image commands."""

from k3 import commands

BASE_URL_API = "https://rra.ram.moe/i/r?type={0}"
BASE_URL_IMAGE = "https://cdn.ram.moe{0[path]}"

COMMANDS = {
    "cuddle": ["cuddles", "snuggle", "snuggles", "snug"],
    "hug": [],
    "kiss": [],
    "lewd": ["2lewd", "2lewd4me"],
    "lick": [],
    "nom": [],
    "nyan": ["nya", "meow"],
    "owo": [],
    "pat": ["headpat", "pet"],
    "pout": [],
    "slap": [],
    "smug": [],
    "stare": [],
    "tickle": [],
    "triggered": []
}

_globals = globals()

# This programmatically generates the ram image commands.
for key in COMMANDS:

    help = f"{key.capitalize()}!"

    async def coro(ctx):
        url = BASE_URL_API.format(ctx.command.name)
        async with ctx.bot.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                message = BASE_URL_IMAGE.format(data).replace("i/", "")
            else:
                message = "Could not retrieve image. :("
            await ctx.send(message)

    # Ew, gross.
    _globals[key] = commands.command(name=key, aliases=COMMANDS[key], help=help)(coro)
    _globals[key].set_cooldown(6, 12)
