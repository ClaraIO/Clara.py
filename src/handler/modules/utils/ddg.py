#!/usr/bin/env python3

"""DuckDuckGo query commands."""

import json
import urllib.parse

from k3 import commands

BASE_URL_DUCKDUCKGO = "https://duckduckgo.com/?{0}"


async def _duckduckgo(ctx, *, query: str, field: str="Answer"):
    """Retrieve an answer from DuckDuckGo, using the Instant Answers JSON API.

    * query - A string to be used in the search criteria.
    * field - The field to query from.

    This function is both powerful and dangerous! It isn't its own command for a reason.
    """
    params = urllib.parse.urlencode({"q": query, "t": "k3",
                                     "format": "json", "no_html": 1})
    url = BASE_URL_DUCKDUCKGO.format(params)
    async with ctx.bot.session.get(url) as response:
        if response.status == 200:
            # This should be response.json() directly, but DuckDuckGo returns an incorrect MIME.
            data = await response.text()
            data = json.loads(data)
            answer = data[field]
            return answer
        message = "Failed to fetch answer. :("
        return message


def _attribution(message):
    return f"{message}\nPowered by DuckDuckGo"


@commands.cooldown(6, 12)
@commands.command()
async def fortune(ctx):
    """Produce a random fortune. :3"""
    answer = await _duckduckgo(ctx, query="random fortune")
    await ctx.send(_attribution(answer))


@commands.cooldown(6, 12)
@commands.command(aliases=["randomname"])
async def rname(ctx):
    """Generate a random name."""
    answer = await _duckduckgo(ctx, query="random name")
    answer = answer.replace("(random)", "")
    await ctx.send(_attribution(answer))
