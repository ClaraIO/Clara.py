#!/usr/bin/env python3

"""Bot help command."""

from k3 import commands


@commands.cooldown(6, 12)
@commands.command(aliases=["commands"])
async def help(ctx, command_name: str=None):
    """Help command. Run help <command name> for more information on a specific command.

    Example usage:
    help
    help ping
    help info
    """
    if command_name:
        cmd = ctx.bot.commands.get(command_name)
        if not ctx:
            await ctx.send(f"{command_name} is not a valid command.")
        else:
            await ctx.send(ctx.f.codeblock(f"{cmd.help}"))
    else:
        commands = ctx.f.codeblock(", ".join(sorted(ctx.bot.commands.keys())) + "\n")
        commands = ctx.f.bold("List of commands:\n") + commands
        commands += f"\nRun {ctx.f.bold('help command')} for more details on a command."
        await ctx.send(commands)
