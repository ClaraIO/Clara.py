#!/usr/bin/env python3

"""A Magic 8-Ball command."""

import random

from k3 import commands

systemrandom = random.SystemRandom()

ANSWERS = [
    # Stock replies.
    "It it certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",

    "Reply hazy try again.",
    "Ask again later.",
    "Better not to tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",

    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",

    # Kitsuchan replies
    "Yay!",
    ":fox:",
    ":sunny: :3",
    ":clap:",
    "Kon kon!",
    "+1",
    "Awau! :3",
    ":thumbsup:",
    "Yes. :3",
    ":3",

    "Awau? o.o",
    "Ask again later?",
    "/mobileshrug",
    "Don't know? :<",
    "Kon kon kon.",

    "Awau. :<",
    "Get bent. :3",
    "No. :<",
    ":thumbsdown:",
    "RIP"]


@commands.cooldown(6, 12)
@commands.command(name="8ball", aliases=["eightball"])
async def _eightball(ctx):
    """Ask the Magic 8-Ball a question."""
    choice = systemrandom.choice(ANSWERS)
    await ctx.send(choice)