#!/usr/bin/env python3

"""Simple xkcd command."""

from k3 import commands


@commands.cooldown(6, 12)
@commands.command()
async def xkcd(ctx):
    """Fetch the latest xkcd comic."""
    url = "https://xkcd.com/info.0.json"
    async with ctx.bot.session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            await ctx.send(data["img"])
        else:
            await ctx.send("Could not reach xkcd.")
