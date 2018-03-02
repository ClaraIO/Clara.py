#!/usr/bin/env python3

"""Dictionary lookup command."""

import re
import urllib.parse

from k3 import commands

BASE_URL_OWL_API = "https://owlbot.info/api/v1/dictionary/{0}{1}"

MAX_NUM_RESULTS = 5


@commands.cooldown(6, 12)
@commands.command()
async def define(ctx, word):
    """Define a word.

    Example usage:
    define cat
    define dog
    define fox
    """
    word = word.lower()
    params = "?{0}".format(urllib.parse.urlencode({"format": "json"}))
    url = BASE_URL_OWL_API.format(word, params)
    async with ctx.bot.session.get(url) as response:
        if response.status == 200:
            data = await response.json()

            if not data:
                await ctx.send("No results found for that word.")
                return

            message = [
                ctx.f.bold(word),
                BASE_URL_OWL_API.format(word, "")
            ]

            results_to_display = min(MAX_NUM_RESULTS, len(data))

            for index in range(0, results_to_display):
                result = data[index]
                definition = result.get('defenition')
                description = re.sub("<.*?>|\u00E2|\u0080|\u0090", "",
                                     definition.capitalize())
                example = result.get('example')
                if example:
                    example = re.sub("<.*?>|\u00E2|\u0080|\u0090", "",
                                     example.capitalize())
                    example = ctx.f.italic(example)
                    description = f"{description}\nExample: {example}"
                message.append("\n" + result["type"] + "\n" + description)

            message = "\n".join(message)
        else:
            message = "Connection failed, or that isn't a word. :<"

        await ctx.send(message)
