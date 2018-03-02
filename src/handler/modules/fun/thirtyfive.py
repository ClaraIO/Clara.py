#!/usr/bin/env python3

"""Meme command(s)."""

import random

from k3 import commands

systemrandom = random.SystemRandom()

AAA = ("a",
       "A",
       "\u3041",
       "\u3042",
       "\u30A1",
       "\u30A2")


@commands.cooldown(6, 12)
@commands.command(aliases=["aa", "aaa"])
async def a(ctx):
    """Aaaaaaa!"""
    message = systemrandom.choice(AAA) * systemrandom.randint(10, 200)
    await ctx.send(message)
