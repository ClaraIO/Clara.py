#!/usr/bin/env python3

"""Argument parsing test."""

from k3 import commands


@commands.cooldown(6, 12)
@commands.command()
async def paramtest(ctx, integer: int, floating_point: float, *args):
    """A test command that checks argument parsing."""
    await ctx.send(f"{integer} is a {type(integer)}")
    await ctx.send(f"{floating_point} is a {type(floating_point)}")
    await ctx.send(args)
