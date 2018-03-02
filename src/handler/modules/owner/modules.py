#!/usr/bin/env python3

"""Module loading and unloading commands."""

from k3 import commands


@commands.command(owner_only=True)
async def load(ctx, name):
    """Load a k3 module by name. Owner only.

    Example usage:
    load modules.core.ping
    """
    ctx.bot.config.setdefault("module_blacklist", [])
    if name in ctx.bot.config["module_blacklist"]:
        ctx.bot.config["module_blacklist"].remove(name)
        ctx.bot.save_config()
        try:
            ctx.bot.add_module(name, skip_duplicate_commands=True)
            await ctx.send(f"Loaded module {name}")
            return
        except Exception as error:
            await ctx.send(error)
            return
    await ctx.send(f"{name} is already loaded.")


@commands.command(owner_only=True)
async def reload(ctx, name):
    """Reload a k3 module by name. Owner only.

    Example usage:
    reload modules.core.ping
    """
    try:
        ctx.bot.remove_module(name)
        ctx.bot.add_module(name)
        await ctx.send(f"Reloaded module {name}")
    except Exception as error:
        await ctx.send(error)


@commands.command(owner_only=True)
async def unload(ctx, name):
    """Unload a k3 module by name. Owner only.

    Example usage:
    unload modules.core.ping
    """
    ctx.bot.config.setdefault("module_blacklist", [])
    if name not in ctx.bot.config["module_blacklist"]:
        ctx.bot.config["module_blacklist"].append(name)
        ctx.bot.save_config()
        try:
            ctx.bot.remove_module(name)
            await ctx.send(f"Unloaded module {name}")
            return
        except Exception as error:
            await ctx.send(error)
            return
    await ctx.send(f"{name} is not currently loaded.")
