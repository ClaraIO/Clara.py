#!/usr/bin/env python3

"""jisho.org query command."""

import urllib.parse

from k3 import commands

BASE_URL_JISHO_API = "http://jisho.org/api/v1/search/words?{0}"


@commands.cooldown(6, 12)
@commands.command(aliases=["jp"])
async def jisho(ctx, query, *args):
    """Translate a word into Japanese.

    Example usage:
    jisho test
    """
    query = f"{query} {' '.join(args)}"
    params = urllib.parse.urlencode({"keyword": query})
    url = BASE_URL_JISHO_API.format(params)
    async with ctx.bot.session.get(url) as response:
        if response.status == 200:
            data = await response.json()

            if not data["data"]:
                await ctx.send("No result found.")

            japanese = data["data"][0]["japanese"][0]
            sense = data["data"][0]["senses"][0]
            english_string = ", ".join(sense["english_definitions"])
            message = [
                ctx.f.bold("Kanji: ") + str(japanese.get("word")),
                ctx.f.bold("Kana: ") + str(japanese.get("reading")),
                ctx.f.bold("English: ") + english_string
            ]
            await ctx.send("\n".join(message))
        else:
            await ctx.send("Couldn't reach Jisho.org. x.x")
