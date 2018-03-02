#!/usr/bin/env python3

"""Commands that encode and decode things."""

from k3 import commands


@commands.cooldown(6, 12)
@commands.command()
async def reverse(ctx, *message):
    """Reverse input text."""
    message = " ".join(message)
    await ctx.send(message[::-1])


@commands.cooldown(6, 12)
@commands.command(name="binary")
async def to_binary(ctx, *message):
    """Encode plaintext to binary.

    The behavior of this command isn't 100% correct as it may slip on Unicode.
    """
    message = list(" ".join(message))

    for index, character in enumerate(message):
        message[index] = str(bin(ord(character)))[2:].zfill(8)

    message = " ".join(message)
    await ctx.send(message)
