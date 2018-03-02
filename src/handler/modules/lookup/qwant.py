#!/usr/bin/env python3

"""This cog contains an image query command."""

import html
import random
import urllib.parse

from k3 import commands

BASE_URL_QWANT_API = "https://api.qwant.com/api/search/images?{0}"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0"
HEADERS = {"User-Agent": USER_AGENT}

systemrandom = random.SystemRandom()


@commands.cooldown(6, 12)
@commands.command(aliases=["qimage"])
async def image(ctx, *query):
    """Grab an image off the Internet using Qwant.

    * query - A list of strings to be used in the search criteria.
    """
    if not query:
        await ctx.send("Please specify a search query.")
        return
    query = " ".join(query)
    params = urllib.parse.urlencode({"count": "100", "offset": "1", "q": query})
    url = BASE_URL_QWANT_API.format(params)
    async with ctx.bot.session.request("GET", url, headers=HEADERS) as response:
        if response.status == 200:
            data = await response.json()
            if not data["data"]["result"]["items"]:
                await ctx.send("No results found. :<")
                return
            item = systemrandom.choice(data["data"]["result"]["items"])
            message = [
                html.unescape(item["title"]),
                ctx.f.no_embed_link(item["url"]),
                item["media"],
                "Powered by Qwant"
            ]
            message = "\n".join(message)
            await ctx.send(message)
        else:
            message = "Couldn't reach Qwant. x.x"
            await ctx.send(message)
