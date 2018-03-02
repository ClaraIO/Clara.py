#!/usr/bin/env python3

"""A command that hooks strawpoll.me's API to create a poll."""

import logging

from k3 import commands

logger = logging.getLogger(__name__)

BASE_URL_STRAWPOLL = "https://strawpoll.me/{0}"
BASE_URL_STRAWPOLL_API = "https://strawpoll.me/api/v2/polls"


@commands.cooldown(6, 12)
@commands.command(aliases=["strawpoll", "poll"])
async def makepoll(ctx, *options):
    """Create a Straw Poll.

    Example usage:
    makepoll "Name of poll" "Option 1" "Option 2" Option3
    """
    options = " ".join(options).split(",")
    if len(options) < 3:
        return ("Please specify a title and at least two options. "
                "Arguments must be separated with commas, e.g. "
                "makepoll Test Poll, Option 1, Option 2")
    for index in range(0, len(options)):
        options[index] = options[index].strip()
    title = options.pop(0)
    logger.info("POSTing to Straw Poll API.")
    data = {"title": title, "options": options}
    async with ctx.bot.session.request("POST", BASE_URL_STRAWPOLL_API, json=data) as response:
        if response.status <= 210:
            logger.info("POSTing OK.")
            data = await response.json()
            url = BASE_URL_STRAWPOLL.format(data["id"])
            await ctx.send(f"Successfully created poll; you can find it at {url}")
        else:
            await ctx.send("Failed to create poll. x.x")
