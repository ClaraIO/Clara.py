#!/usr/bin/env python3

"""Bot information command."""

import resource
import sys

import k3
from k3 import commands


@commands.cooldown(6, 12)
@commands.command(aliases=["about", "stats"])
async def info(ctx):
    """Display some basic information about the bot, such as memory usage."""
    usage_memory = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000, 2)
    message = [
        ctx.bot.name,
        ctx.bot.description,
        f"# of commands: {len(ctx.bot.commands)}",
        "Python: {0}.{1}.{2}".format(*sys.version_info),
        f"k3: {k3.version}",
        f"Cookies eaten: {usage_memory} megabites"
    ]
    message = ctx.f.codeblock("\n".join([str(line) for line in message if len(line) > 0]))

    await ctx.send(message)