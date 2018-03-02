#!/usr/bin/env python3

"""Subcommand testing."""

from k3 import commands


@commands.cooldown(6, 12)
@commands.command()
async def cg(ctx, *args):
    """A test command that checks command group handling."""
    await ctx.send(args)


@commands.cooldown(1, 90)
@cg.command()
async def sc(ctx):
    """A test command that checks command group handling."""
    await ctx.send("Meow?")
