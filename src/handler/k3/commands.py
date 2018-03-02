#!/usr/bin/env python3

"""This is a small and basic command handling framework for making Python bots."""

import asyncio
import importlib
import inspect
import json
import logging
import shlex
import sys
import time
from typing import List

try:
    import aiohttp
except ImportError:
    pass

import k3.keygen
import k3.formatters.core

logger = logging.getLogger(__name__)


class NotCoroutine(Exception):
    """Raised if a command is passed a function that is not a coroutine."""
    pass


class CommandExists(Exception):
    """Raised if a command registration attempt is made, but the name already exists in the bot."""
    pass


class OnCooldown(Exception):
    """Raised if a command is invoked while on cooldown."""
    pass


class BadArgument(Exception):
    """Raised if a bad argument is supplied to a command."""
    pass


class NotBotOwner(Exception):
    """Raised if an owner-only command is invoked by someone who isn't the bot owner."""
    pass


def parse_arguments(text: str):
    """A very simple argument parser.

    * `text` - An `str` to be parsed into arguments.
    """
    try:
        arguments = shlex.split(text)
    except ValueError:
        # Fallback if shlex blows up.
        text = text.strip()
        arguments = list(filter(lambda item: item != "", text.split(" ")))
    return arguments


def convert_arguments(start: int, signature: inspect.Signature, *args):
    """Parse and typecast arguments based on a function signature. Returns a `list` truncated to
    the length of the signature or the argument list, whichever is shorter.

    * `start` - The starting index to use for the parameters. This is used so we can skip over the
                `ctx` argument that is required by k3 command coroutines.
    * `signature` - An `inspect.Signature` that is used as a basis for converting the arguments.
    * `args` - The arguments to be converted.
    """
    return_args = []
    signature_params = list(signature.parameters.values())
    for index, (param, arg) in enumerate(zip(signature_params[start:], args)):
        if param.kind == param.VAR_POSITIONAL:
            # We've reached an *args parameter, so we just concatenate the remaining arguments
            # onto the return. This is why enumerate is used here - it gives us an index to mark
            # where the leftover arguments begin.
            return_args += args[index:]
        elif param.annotation is not param.empty:
            try:
                return_args.append(param.annotation(arg))  # Typecast using param.annotation.
            except ValueError:
                raise BadArgument((f"Argument named \"{param.name}\" must be of type "
                                   f"{param.annotation.__name__}."))
        else:
            return_args.append(arg)
    return return_args


class Context:
    """This object represents an abstracted context under which a `Command` is invoked.

    You don't make these manually.
    """

    def __init__(self, *, callback_send, character_limit: int=2000, command, bot,
                 invoked_with: str):
        """**Parameters**

        * `callback_send` - A coroutine for sending a message. This is entirely dependent on your
                            library. You may have to implement a custom coroutine, depending on
                            the format of your library's own method for sending messages.
        * `character_limit` - An `int` representing the maximum allowable characters per message.
                              The abstracted `send` method will automatically split messages that
                              are too long; if this behavior is undesirable, you should do a
                              manual truncation.
        * `command` - The `Command` object associated with the context.
        * `bot` - The `Bot` object associated with your bot.
        * `invoked_with` - `str` representing the command name associated with the context.
        * `formatter` or `f` - Shorthand for `ctx.bot.formatter`.
        """
        if not asyncio.iscoroutinefunction(callback_send):
            raise NotCoroutine(f"{callback_send.__name__} is not a coroutine function.")
        self._callback_send = callback_send
        self.bot = bot
        self.command = command
        self.character_limit = character_limit
        self.invoked_with = invoked_with

    @property
    def formatter(self):
        """Shorthand for `ctx.bot.formatter`."""
        return self.bot.formatter

    @property
    def f(self):
        """Shorthand for `ctx.bot.formatter`."""
        return self.bot.formatter

    async def send(self, message):
        """An abstracted method that sends a message to the desired location. This is a coroutine.

        You must specify the actual send method in the `Context` constructor.
        """
        message = str(message)
        cl = self.character_limit
        pages = [message[i:i+cl] for i in range(0, len(message), cl)]
        for page in pages:
            await self._callback_send(page)


class CommandGroupMixin:
    """This class contains partial command handling facilities, as well as command grouping
    functionality. Generally, you do not use this by itself.

    Both `Bot` and `Command` inherit from this class.

    * `commands` - A `dict` containing all of the bot's commands.
    * `all_commands` - A `dict` containing all of the bot's commands, counting aliases.
    * `name` - An `str` representing the name of the `CommandGroupMixin`. Children classes
               should reimplement `__init__` to set it as desired. `name` is used in `process`
               to detect command invocations, where a matching `name` will trigger the
               corresponding command.
    * `aliases` - A `list` of `str` representing alternates to `name` for command invocations.
    * `parent` - The parent object of the mixin; the command or bot that it has been added to.
    """

    def __init__(self, *, name: str=None, aliases: List[str]=[]):
        self.commands = {}
        self.all_commands = {}
        self.name = name or self.__name__
        self.aliases = []
        self.parent = None

    def add_command(self, command, *, skip_duplicate=False):
        """Add a `Command` object to the group.

        Normally, you do not call this by itself; instead, you use the `CommandGroupMixin.command`
        decorator. Or you may call `Bot.add_module()` on a module that contains a series of commands
        created using the `k3.command` decorator.

        * `command` - A `Command` object to be added.
        * `skip_duplicate` - A `bool`. If `True`, the function returns immediately if the command
                             is found to already exist. Otherwise, it raises a `CommandExists`
                             exception. Defaults to `False`.
        """
        if command.name in self.all_commands.keys() and skip_duplicate:
            return
        elif command.name in self.all_commands.keys():
            raise CommandExists(f"{command.name} is a command that already exists.")
        command.parent = self  # Set the command's bot instance
        self.commands[command.name] = command
        self.all_commands[command.name] = command
        for alias in command.aliases:
            self.all_commands[alias] = command

    def remove_command(self, name):
        """Remove a `Command` object from the group, by name.

        * `name` - An `str` referring to the name of the command to remove.
        """
        aliases = self.commands[name].aliases
        self.commands[name].parent = None
        del self.commands[name]
        del self.all_commands[name]
        for alias in aliases:
            del self.all_commands[alias]

    async def process(self, message: str, *, callback_send, is_owner: bool=False,
                      character_limit: int=2000, prefixes: List[str]=[]):
        """Process the given message. This is a coroutine.

        * `message` - A message `str` for the bot to process.
        * `is_owner` - A `bool` used to force an owner check override if you want an alternative
                       handler instead of k3's clunky key system. This is useful if the library you
                       use has some automated means of distinguishing the bot owner. For example,
                       discord.py offers owner information via `discord.Client.application_info()`,
                       so you can use that to check if the message sender is the owner, and then
                       pass the result on to the k3 handler.
        * `callback_send` - A coroutine that k3 will use to send messages. This is library-
                            dependent, and you may have to define a custom coroutine depending on
                            the exact format of your library's methods.
        * `character_limit` - An `int` representing the number of allowed characters in a given
                              message.
        * `prefixes` - A `list` of `str` to look out for in the process of invoking commands.
                       If a message starts with one of the `str` in the `list`, then an
                       invocation will be attempted. Normally, you don't override this.
        """
        if not prefixes:
            prefixes = [self.name] + self.aliases

        for prefix in prefixes:
            if message.startswith(prefix):

                noprefix_message = message[len(prefix):].strip()
                arguments = noprefix_message.split(" ")

                if arguments and arguments[0] in self.all_commands.keys():
                    await self.all_commands[arguments[0]].process(noprefix_message,
                                                                  is_owner=is_owner,
                                                                  callback_send=callback_send,
                                                                  character_limit=character_limit)
                else:
                    await self.invoke(message, is_owner=is_owner, callback_send=callback_send,
                                      character_limit=character_limit)
                break

    async def invoke(self, message: str, *, is_owner: bool=False, callback_send,
                     character_limit: int=2000):
        """This is a dummy `invoke` method, to be reimplemented in children classes.

        It is called to invoke the `CommandGroupMixin`, but this is a mixin class and thus does
        not have anything to invoke, really.
        """
        pass

    def command(self, *, name: str=None, aliases: List[str]=[], help: str=None,
                owner_only: bool=False):
        """This is a shortcut decorator that directly adds a subcommand.

        Refer to the `k3.command` decorator for more details, as it is functionally similar.
        """

        def decorator(coro):
            new_command = Command(coro, name=name, aliases=aliases, help=help,
                                  owner_only=owner_only)
            self.add_command(new_command)
            return new_command

        return decorator

    @property
    def top_level(self):
        """Returns the top-level container for this object. Usually a commands.Bot()."""
        current_level = self
        while current_level.parent:
            current_level = current_level.parent
        return current_level


class Bot(CommandGroupMixin):
    """This is a bot object that contains basic command handling functionality.

    Inherits `CommandGroupMixin` functionality; refer to that class for additional functionality.
    """

    def __init__(self, *, loop: asyncio.AbstractEventLoop, prefix: str, name: str="k3",
                 description: str="A bot made using the k3 command handler.", logout=None,
                 formatter=None, config_file: str="config.json"):
        """This object respresents a command-based bot; i.e. it can process and handle commands.
        Commands are represented by `Command` objects.

        To use this, instantiate it and then call `Bot.process(text)` whenever a message event
        occurs. Some examples are provided in the repository.

        * `loop` - An `asyncio.AbstractEventLoop` to pass to the bot.
        * `prefix` - An `str` that the bot uses to identify whether a command is being
                     requested by someone. All attempted command invocations must start with
                     the prefix.
        * `name` - An `str` representing the name of the bot. Defaults to `k3`.
        * `description` - An `str` representing the description of the bot. Defaults to `A bot made
                          using the k3 command handler.`
        * `logout` - An optional callable parameter that allows for an abstracted bot logout. This
                     allows you to supply a method for cleanly exiting the bot. It can be as simple
                     as supplying `sys.exit`, though this will usually not be a clean exit. The
                     `logout` parameter may be a coroutine function.
        * `formatter` - A custom `Formatter` object for formatting things into platform-specific
                        outputs. You can use one of k3's built-in formatters, or you can make one
                        of your own. Formatters should be subclassed from
                        `k3.formatters.BaseFormatter`.
        * `config_file` - An `str` representing the configuration file of the bot. Defaults to
                          `config.json`. This doesn't really have to be used, but it's there for
                          convenience reasons.

        Instance variables not in the constructor:

        * `key` - An `str` key for the bot owner. Use this for platform-agnostic owner-only
                  commands. Commands marked as owner-only will require the key to be supplied as
                  the last command argument. Because the key obviously becomes public as soon as
                  it's posted to a chat, it changes upon every use.
        * `session` - An `aiohttp.ClientSession` that the bot can use to make HTTP requests.
                      This is useful for commands that perform API hooks. If `aiohttp` is not
                      available, this is just `None`.
        * `config` - A `dict` containing key-value pairs meant for bot configuration. This doesn't
                     really have to be used, but it's there for convenience reasons.

        Example usage:

            import discord

            from k3 import commands

            client = discord.Client()
            bot = commands.Bot(loop=client.loop, prefix=">>", name="MyBot", logout=client.logout)
        """
        super(Bot, self).__init__(name=name)
        self.loop = loop
        try:
            self.session = aiohttp.ClientSession(loop=self.loop)
        except NameError:
            self.session = None
        self.prefix = prefix
        self.description = description
        self._logout = logout
        if not formatter:
            self.formatter = k3.formatters.core.BaseFormatter()
        elif not isinstance(formatter, k3.formatters.core.BaseFormatter):
            raise TypeError(f"{formatter} is not a BaseFormatter.")
        else:
            self.formatter = formatter
        self.config = {}
        self.config_file = config_file

        self._task_key_regeneration = self.loop.create_task(self._regenerate_key_auto())

    async def logout(self):
        """An abstracted logout method. This is a coroutine.

        You must specify the logout function in the `Bot` constructor.
        """
        self.session.close()
        self._task_key_regeneration.cancel()
        if asyncio.iscoroutinefunction(self._logout):
            await self._logout()
        elif callable(self._logout):
            self._logout()

    def load_config(self, filename: str=None):
        """Load config from a JSON file.

        * `filename` - The filename of the JSON file to be loaded. If not specified, the bot will
                       default to `Bot.config_file`.
        """
        if not filename:
            filename = self.config_file
        with open(filename) as file_object:
            config = json.load(file_object)
        if isinstance(config, dict):
            for key, value in config.items():
                self.config[key] = value

    def save_config(self, filename: str=None):
        """Save config to a JSON file.

        * `filename` - The filename of the JSON file to be saved to. If not specified, the bot will
                       default to `Bot.config_file`.
        """
        if not filename:
            filename = self.config_file
        with open(filename, "w") as file_object:
            json.dump(self.config, file_object)

    def regenerate_key(self):
        """Generate a new key for the bot. Random alphanumeric string, 64 characters long.

        This is called every 30 minutes, and also whenever an owner-only command is invoked unless
        an override is requested.
        """
        self.key = k3.keygen.generate_key()
        logger.info("Bot key is now {self.key}")

    async def _regenerate_key_auto(self):
        """Regenerate key every 30 minutes."""
        while 1:
            self.regenerate_key()
            await asyncio.sleep(1800)

    async def process(self, message: str, *, callback_send, is_owner: bool=False,
                      character_limit: int=2000):
        """Reimplemented `process` to check against the bot's prefix. Refer to
        `CommandGroupMixin.process` for more details."""
        await super(Bot, self).process(message, callback_send=callback_send, is_owner=is_owner,
                                       character_limit=character_limit, prefixes=[self.prefix])

    def add_module(self, name: str, *, skip_duplicate_commands: bool=False):
        """Add a Python module to the bot, by name.

        The bot will check said module for instances of `Command` and add all of them to itself.

        * `name` - An `str` representing the name of the module to import.
        * `skip_duplicate_commands` - A `bool`. If `True`, the function will skip command names
                                      that already exist. Otherwise, it raises a `CommandExists`
                                      exception. Defaults to `False`.
        """

        # If the module is already in memory, we reload it instead.
        if name in sys.modules.keys():
            importlib.reload(sys.modules[name])
            module = sys.modules[name]
        else:
            module = importlib.import_module(name)

        for command in dir(module):

            command = getattr(module, command)

            if isinstance(command, Command) and not command.parent:
                self.add_command(command, skip_duplicate=skip_duplicate_commands)

    def remove_module(self, name):
        """Remove a Python module to the bot, by name.

        When this is called, the bot will remove all `Command` objects that belong to the module
        in question. It does not unload the module from memory, as Python doesn't support this.
        This isn't considered a serious issue, since the hit to memory usage shouldn't be
        significant.

        * `name` - An `str` representing the name of the module to remove.
        """
        for command_name, command in tuple(self.commands.items()):
            if command.coro.__module__ == name:
                self.remove_command(command_name)


class Command(CommandGroupMixin):

    def __init__(self, coro, *, name: str=None, aliases: List[str]=[], help: str=None,
                 owner_only=False):
        """This object represents a command that a bot can use.

        Normally, you do not construct this directly. Use the decorator syntax instead.

        * `coro` - A coroutine function that the command uses upon calling `invoke()`.
                   Should have an `*args` to catch any extra arguments.
        * `name` - An `str` representing the name for the command. If unspecified, it's set to
                   `coro.__name__`.
        * `aliases` - A `list` of `str` representing aliases for the command; that is, alternative
                      names you can invoke the command under.
        * `help` - An `str` representing the command's help text. It can alternatively be read from
                   the coroutine's docstring, which makes code easier to read.
        * `owner_only` - A `bool`. Determines whether the command is meant for the bot owner only.
                         If `True`, the command will require the bot's temporary key as the final
                         command argument, and will fail to run unless `is_owner` is overridden in
                         the call to the `invoke()` method. Defaults to `False`.

        Instance variables not in the constructor:

        * `bot` - The `Bot` instance that the command is assigned to.
        * `signature` - An `inspect.Signature` reflecting the command signature.
        """

        name = name or coro.__name__
        super(Command, self).__init__(name=name, aliases=aliases)

        self.help = help or inspect.getdoc(coro)

        if not asyncio.iscoroutinefunction(coro):
            raise NotCoroutine(f"{coro.__name__} is not a coroutine function.")
        self.coro = coro
        self.signature = inspect.signature(self.coro)

        self.owner_only = owner_only

        # These are used internally for cooldowns.
        self._interval_start = 0  # This tracks the start of an interval.
        self._times_invoked = 0  # This tracks the number of times the command is used.
        self._limit = 0  # Limit of uses per interval
        self._interval = 0  # Interval in seconds

    def set_cooldown(self, limit: int, interval: float=1):
        """This sets the cooldown for the command.

        Normally, you do not call this directly; use the decorator syntax instead.

        * `limit` - An `int` representing the limit of uses per interval before the cooldown kicks.
        * `interval` - A `float` representing, in seconds, the interval before the cooldown resets.
                       Defaults to `1`.
        """
        self._limit = limit
        self._interval = interval

    def _update_cooldown(self):
        if self._limit > 1:
            invoke_time = time.time()
            if invoke_time - self._interval_start >= self._interval:
                self._times_invoked = 1
                self._interval_start = invoke_time
            elif self._times_invoked >= self._limit:
                raise OnCooldown("Command on cooldown.")
            else:
                self._times_invoked += 1

    async def invoke(self, message: str, *, is_owner: bool=False, callback_send,
                     character_limit: int=2000):
        """Calling this will invoke the command, provided a message string.

        Normally, you do not call this by itself; instead run `Bot.process()`.

        * `message` - An `str` to pass the command for processing.
        * `is_owner` - A `bool` that overrides the owner checking. Use this if you have some other
                       means of checking for the owner.
        * `callback_send` - A coroutine that k3 will use to send messages. This is library-
                            dependent, and you may have to define a custom coroutine depending on
                            the exact format of your library's methods.
        * `character_limit` - An `int` representing the number of allowed characters in a given
                              message.
        """
        # Cooldown
        self._update_cooldown()

        arguments = parse_arguments(message)
        invoked_with = arguments.pop(0)

        # Override.
        if is_owner:
            pass
        # Check arguments against the bot's key if owner_only.
        # We assume that top_level is a Bot in this case.
        elif self.owner_only and (not arguments or arguments[-1] != self.top_level.key):
            raise NotBotOwner("You don't own this bot.")
        elif self.owner_only:
            arguments.pop(-1)
            self.top_level.regenerate_key()

        ctx = Context(callback_send=callback_send, bot=self.top_level, command=self,
                      character_limit=character_limit, invoked_with=invoked_with)
        converted_arguments = convert_arguments(1, self.signature, *arguments)
        response = await self.coro(ctx, *converted_arguments)

        return response


def command(*, name: str=None, aliases: List[str]=[], help: str=None, owner_only: bool=False):
    """This is a decorator, which you call on a coroutine to make it into a `Command` object.

    Normally, you should use this instead of constructing `Command` objects directly.

    * `coro` - A coroutine function that the command uses upon calling `invoke()`.
               Should have an `*args` to catch any extra arguments.
    * `name` - An `str` reperesnting the name for the command. If unspecified, it's set to
               `coro.__name__`.
    * `aliases` - A `list` of `str` representing aliases for the command; that is, alternative
                  names you can invoke the command under.
    * `help` - An `str` representing the command's help text.
    * `owner_only` - A `bool`. Determines whether the command is meant for the bot owner only.
                     If `True`, the command will require the bot's temporary key as the final
                     command argument, and will fail to run unless `is_owner` is overridden in the
                     call to the `invoke()` method. Defaults to `False`.

    Example:

        @commands.command()
        async def ping(*args):
            return "Pong!"
    """

    def decorator(coro):
        new_command = Command(coro, name=name, aliases=aliases, help=help, owner_only=owner_only)
        return new_command

    return decorator


def cooldown(uses: int, interval: float=1):
    """This is a decorator that sets the cooldown for a command.

    Normally, you should use this instead of calling `Command.set_cooldown()` directly.

    * `limit` - An `int` representing the limit of uses per interval before the cooldown kicks.
    * `interval` - A `float` representing, in seconds, the interval before the cooldown resets.
                   Defaults to `1`.

    Example:

        @commands.cooldown(6, 12) # Allow 6 uses per 12 seconds.
        @commands.command()
        async def ping(*args):
            return "Pong!"
    """

    def decorator(command):
        command.set_cooldown(uses, interval)
        return command

    return decorator
