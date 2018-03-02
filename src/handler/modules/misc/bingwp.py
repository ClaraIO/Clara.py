#!/usr/bin/env python3

"""Bing wallpaper command."""

import random

from k3 import commands

BASE_URL_BING_API = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n={0}&mkt=en-US"
BASE_URL_BING = "https://www.bing.com{0}"

systemrandom = random.SystemRandom()


@commands.cooldown(6, 12)
@commands.command(aliases=["bwp"])
async def bingwp(ctx):
    """Query Bing for a wallpaper."""

    url = BASE_URL_BING_API.format(8)

    async with ctx.bot.session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            image = systemrandom.choice(data["images"])
            url = BASE_URL_BING.format(image["url"])
            await ctx.send(url)
        else:
            message = "Could not fetch wallpaper. :<"
            await ctx.send(message)
