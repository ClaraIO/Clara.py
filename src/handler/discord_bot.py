#!/usr/bin/env python3

"""A basic Discord bot made using k3's command handler.

Requires Python 3.6+ and discord.py rewrite (1.0).
"""

import logging
import os

import discord

from k3 import commands
import k3.formatters.discord

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

client = discord.AutoShardedClient()
formatter = k3.formatters.discord.DiscordFormatter()
bot = commands.Bot(loop=client.loop, prefix="!", logout=client.logout, formatter=formatter,
                   config_file="config.json")


@client.event
async def on_ready():
    """Set the bot's playing status to the help command."""
    game = discord.Game()
    game.name = f"Type {bot.prefix} help for help!"
    await client.change_presence(game=game)


@client.event
async def on_message(message):
    """Broadly handle on_message events from Discord."""
    if message.author.bot:  # Ignore other bots.
        return
    # Check if the message author is the bot owner. This overrides k3's key system, making the bot
    # easier to use.
    application_info = await client.application_info()
    is_owner = message.author.id == application_info.owner.id
    # Transfer processing to the k3 command handler.
    try:
        await bot.process(message.content, is_owner=is_owner, callback_send=message.channel.send,
                          character_limit=2000)
    except Exception as error:
        await message.channel.send(error)

if __name__ == "__main__":
    bot.load_config()

    assert (isinstance(bot.config.get("discord_token"), str)), "Bot token not valid."
    assert (isinstance(bot.config.get("module_blacklist", []), list)), "Blacklist must be a list."

    bot.prefix = bot.config.get("prefix", "k3")

    blacklist = bot.config.get("module_blacklist", [])

    # Automatically load all modules.
    for dirpath, dirnames, filenames in os.walk("modules"):
        for filename in filenames:
            if filename.endswith(".py"):
                fullpath = os.path.join(dirpath, filename).split(os.sep)
                module = ".".join(fullpath)[:-3]  # Eliminate the .py
                if module in blacklist:  # Skip blacklisted modules.
                    continue
                try:
                    bot.add_module(module, skip_duplicate_commands=True)
                except Exception as error:
                    print(f"Unable to load {module}: {error}")
    client.run(bot.config["discord_token"])
