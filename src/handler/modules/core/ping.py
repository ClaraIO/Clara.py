#!/usr/bin/env python3

"""Ping command."""

from k3 import commands


@commands.cooldown(6, 12)
@commands.command()
async def ping(ctx):
    """Pings the bot to see if it's alive."""
    await ctx.send(":3")
