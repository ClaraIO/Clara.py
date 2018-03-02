#!/usr/bin/env python3

"""Wikipedia lookup command."""

import urllib.parse

from k3 import commands

BASE_URL_WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php?{0}"


@commands.cooldown(6, 12)
@commands.command(aliases=["wikipedia"])
async def wiki(ctx, query, *args):
    """Search Wikipedia.

    Example usage:
    wiki fox
    wiki discord (software)
    wiki declaration of independence
    """
    query = query + " ".join(args)

    params = urllib.parse.urlencode({"action": "opensearch", "search": query})
    url = BASE_URL_WIKIPEDIA_API.format(params)
    async with ctx.bot.session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            if not data[1]:
                await ctx.send("No results found. :<")
                return
            entries = []
            for index in range(0, min(3, len(data[1]))):
                title = ctx.f.bold(data[1][index])
                link = ctx.f.no_embed_link(data[3][index])
                description = "\n" + data[2][index] if data[2][index] else ""
                entry = f"{title}\n{link}{description}"
                entries.append(entry)
            entries = "\n\n".join(entries)
            await ctx.send(entries)
        else:
            await ctx.send("Couldn't reach Wikipedia. x.x")
