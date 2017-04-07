import asyncio
import sys
import inspect
import math
import traceback
import importlib

import discord


def get_args(args, args_name, ann):
    for k, i in enumerate(args_name):
        try:
            v = args[i]

            if not type(v) == ann[k]:
                try:
                    v = ann[k](v)

                except Exception:
                    raise TypeError(
                            "Invalid type: got {}, {} expected"
                            .format(ann[k].__name__,
                                    v.__class__.__name__))

            args[i] = v
        except IndexError:
            break
    return args


class Cog:
    def __init__(self, bot):
        self.bot = bot
        members = inspect.getmembers(self)
        for name, command in members:
            # register commands the cog has
            if (isinstance(command, Command) and
                    not isinstance(command, SubCommand)):
                # Ignore SubCommands, they're handled by the Command itself
                command.set_cog(self)
                self.add_command(command)

    def add_command(self, command):
        # Check if the Cog has a command wrapper for all of it's commands
        if hasattr(self, "command_wrapper"):
            self.bot.commands[command.comm] = self.command_wrapper(command)
            for x in command.alias:
                self.bot.commands[x] = self.command_wrapper(command)
        else:
            self.bot.commands[command.comm] = command
            for x in command.alias:
                self.bot.commands[x] = command


class Command:
    """ A command class to provide methods we can use with it """

    def __init__(self, comm, *alias, description=None,
                 admin=False, unprefixed=False, listed=True,
                 has=None):
        self.comm = comm
        self.desc = description
        self.alias = alias
        self.admin = admin
        self.listed = listed
        self.unprefixed = unprefixed
        self.subcommands = {}
        self.has = has or ""

    def set_cog(self, cog):
        self.cog = cog
        if self.subcommands == {}:
            return
        for n, s in self.subcommands.items():
            s.set_cog(cog)

    def subcommand(self, *args, **kwargs):
        """ Create subcommands """
        return SubCommand(self, *args, **kwargs)

    def __call__(self, func):
        """ Make it able to be a decorator """
        self.func = func
        return self

    @asyncio.coroutine
    def run(self, message):
        """ Does type checking for command arguments """
        if self.has != '':  # Checks if the user has a certain perm
            if (getattr(message.channel.permissions_for(message.author),
                        self.has) is False and
                    message.author.id not in self.cog.bot.admins):
                yield from self.cog.bot.send_message(
                    message.channel,
                    "You do not have permission to use this command. "
                    "Required permission: `{}`"
                    .format(self.has.replace("_", " ")))
                return

        # Strip the prefix and main command
        args = message.content[len(self.cog.bot.prefix):].split(" ")[1:]

        args_name = inspect.getfullargspec(self.func)[0][2:]

        if len(args) > len(args_name):
            args[len(args_name)-1] = " ".join(args[len(args_name)-1:])

            args = args[:len(args_name)]

        ann = self.func.__annotations__

        if self.subcommands != {}:
            try:
                # Get the first argument for the command
                # TODO: custom parsing for "multiword arg"
                subcomm = args[0].split(" ")[0]
            except IndexError:
                # No subcommand given, try main command

                args = get_args(args, args_name, ann)
                yield from self.func(self.cog, message, *args)
                return

            if subcomm in self.subcommands.keys():
                # Subcommand found, pop it from the argument list
                args.pop(0)

                # Get the message content
                # and pretend the subcommand doesn't exist
                # This should be redone
                # with for example a `subcommand_depth` kwarg
                c = message.content.split(" ")
                c.pop(1)

                # Update the message content
                message.content = " ".join(c)
                yield from self.subcommands[subcomm].run(message)

            else:
                # Subcommand does not exist,
                # assume arg for main command
                args = get_args(args, args_name, ann)
                yield from self.func(self.cog, message, *args)

        else:
            # No subcommands for the current command
            try:
                # Convert the arguments
                args = get_args(args, args_name, ann)
            except TypeError as e:
                # Not enough arguments given
                raise Exception(
                        "Not enough arguments for {}, required arguments: {}"
                        .format(self.comm, ", ".join(args_name)))

            # Run the command
            yield from self.func(self.cog, message, *args)


class SubCommand(Command):
    """ Subcommand class """

    def __init__(self, parent, comm, desc, *alias, has=''):
        self.comm = comm
        self.parent = parent
        self.has = has
        self.subcommands = {}
        parent.subcommands[comm] = self
        for a in alias:
            parent.subcommands[a] = self


class Page(discord.Embed):
    """ Class used by the Menu """
    def __init__(self, title, content):
        super().__init__()
        self.title = title
        self.description = content


class Paginator:
    """ Paginates text, and creates a Menu """
    def __init__(self, text, title="Page {page_no}/{page_total}",
                 minimum=1, maximum=100):
        self.pages = []

        count = len(text)

        elements = []

        n = math.ceil(math.sqrt(count))
        n = min(n, maximum)

        while count > 0 and len(elements) < n:
            elements.append(1)
            count -= 1

        i = 0
        while count > 0:
            elements[i] += 1
            count -= 1
            i = (i+1) % len(elements)

        items = []

        i = 0
        for l in elements:
            j = i+l
            items.append(text[i:j])
            i = j

        for l, page_no in enumerate(items):
            self.pages.append(
                    Page(title.format(page_no=page_no+1,
                                      page_total=len(items)),
                         "\n".join(l)))

    def get_menu(self, bot, channel, user):
        return Menu(bot, channel, user, *self.pages)


class Menu:
    def __init__(self, bot, channel, user, *pages):
        self.bot = bot
        self.channel = channel
        self.pages = pages
        self.length = len(pages)
        self.page = 0
        self.user = user

    async def start(self):
        # Check Bot permissions
        if not self.channel.permissions_for(
                self.channel.server.me).add_reactions:
            raise Exception(
                "Not allowed to add reactions or not given manage messages")
        if not self.channel.permissions_for(
                self.channel.server.me).manage_messages:
            raise Exception(
                "Not allowed to add reactions or not given manage messages")
        # Bot can add and remove reactions

        # Send initial message
        self.message = await self.bot.send_message(
                self.channel, embed=self.pages[0])

        # Send initial arrows
        await self.bot.add_reaction(self.message, "\u2B05")  # Arrow Left
        await self.bot.add_reaction(self.message, "\u27A1")  # Arrow Right

        while True:  # Loop for a bit, line 259 will get us out of here
            react = await self.bot.wait_for_reaction(["\u2B05", "\u27A1"],
                                                     message=self.message,
                                                     user=self.user,
                                                     timeout=60)
            if react is None:
                await self.bot.delete_message(self.message)
                return
            reaction = react.reaction
            message = reaction.message
            if message.id == self.message.id:
                if isinstance(reaction.emoji, str):
                    # It's a normal emoji, which we want
                    if reaction.emoji == "\u2B05":
                        await self.scroll_left()
                    elif reaction.emoji == "\u27A1":
                        await self.scroll_right()

                await self.bot.remove_reaction(message,
                                               reaction.emoji,
                                               react.user)

    async def scroll_right(self):
        if self.page+1 == self.length:
            # Reached maximum page
            self.page = 0
        else:
            self.page += 1

        # Update page
        await self.bot.edit_message(self.message, embed=self.pages[self.page])

    async def scroll_left(self):
        if self.page == 0:
            # Reached page 1
            self.page = self.length-1
        else:
            self.page -= 1

        # Update page
        await self.bot.edit_message(self.message, embed=self.pages[self.page])


class Bot(discord.Client):
    def __init__(self, prefix, admins, self_=False, cog_list=None,
                 *args, **kwargs):
        self.prefix = prefix
        self.admins = admins
        self.commands = {}
        self.cogs = {}
        self.count = 0
        self.settings = {}
        self.self_ = self_
        self.warns = {}
        self.cog_list = cog_list or "cogs.txt"  # plaintext of all cogs to load
        super().__init__(*args, **kwargs)

    def load_cog(self, name):
        if name in self.cogs:
            return

        lib = importlib.import_module(name)
        if not hasattr(lib, 'setup'):
            del lib
            raise Exception('extension does not have a setup function')

        cog = lib.setup(self)
        del lib
        self.cogs[cog.__class__.__name__] = cog

    def unload_cog(self, name):
        cog = self.cogs.get(name)
        if cog is None:
            return

        for key, command in self.commands.copy().items():
            if command.cog is cog:
                del self.commands[key]
        del sys.modules[cog.__module__]
        del cog

    def gather_cogs(self):
        with open("cog_list.txt") as cog_list:
            for module in cog_list.read().split("\n"):
                self.load_cog(module)

    def reload(self):
        for c in self.cogs.keys():
            self.unload_cog(c)
        self.gather_cogs()

    # TODO: pass all events to the cogs
    async def on_message_edit(self, b, a):
        # Pass this event to cogs with this event
        for c in self.cogs.values():
            if hasattr(c, "on_message_edit"):
                await c.on_message_edit(b, a)

    async def on_message_delete(self, m):
        # Pass this event to cogs with this event
        for c in self.cogs.values():
            if hasattr(c, "on_message_delete"):
                await c.on_message_delete(m)

    async def on_message(self, m):
        # Pass this event to cogs with this event
        for c in self.cogs.values():
            if hasattr(c, "on_message"):
                await c.on_message(m)

        # Ignore other bots
        if m.author.bot:
            return

        if self.self_:
            # Are we a selfbot?
            if m.author.id not in self.admins:
                return

        # Ignore this shitcode
        rawm = m
        m = m.content

        if m.startswith(self.prefix):
            m = m[len(self.prefix):]

            # Get the first word after the prefix
            l = m.split(" ")
            w = l.pop(0).lower()
            if w in self.commands:
                # It's a known command

                if self.commands[w].unprefixed:
                    # It's an unprefixed command, and a prefix was used.
                    return
                if (self.commands[w].admin and
                        rawm.author.id not in self.admins):
                    # Bot admin only command
                    await self.send_message(
                            rawm.channel,
                            "You do not have permission to use that command.")
                    return
                try:
                    await self.commands[w].run(rawm)
                except Exception as e:
                    await self.send_message(rawm.channel,
                                            e.__class__.__name__ + ": " +
                                            " ".join([str(x) for x in e.args]))
                    print("--- PRINTING TRACEBACK IN COMMAND {} ---"
                          .format(self.commands[w].comm))
                    traceback.print_exc()
                    print("--- END OF TRACEBACK ---")

        else:
            # No prefix was used
            l = m.split(" ")
            w = l.pop(0).lower()
            if w in self.commands:
                if not self.commands[w].unprefixed:
                    # Command is prefixed
                    return
                await self.commands[w].run(rawm)
