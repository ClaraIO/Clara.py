#!/usr/bin/env python3

"""Commands that evaluate expressions."""

import subprocess

from k3 import commands


@commands.command(name="sh", owner_only=True)
async def shell(ctx, *args):
    """Execute a system command. Owner only.

    Example usage:
    sh git pull
    """
    if args:
        process = subprocess.Popen(args,
                                   universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    else:
        await ctx.send("Please specify a command.")
        return
    try:
        output, errors = process.communicate(timeout=8)
        process.terminate()
    except subprocess.TimeoutExpired:
        process.kill()
        output = "Command timed out. x.x"
    output = ctx.f.codeblock(output)
    await ctx.send(output)


@commands.command(name="eval", owner_only=True)
async def _eval(ctx, *args):
    """Evaluate a Python expression. Owner only.

    Example usage:
    eval 'hello'
    """
    if args:
        if args[0] == "await":
            args = args[1:]
            output = await eval(" ".join(args))
        else:
            output = eval(" ".join(args))
    else:
        await ctx.send("Please specify an expression.")
        return
    output = ctx.f.codeblock(output, syntax="py")
    await ctx.send(output)
