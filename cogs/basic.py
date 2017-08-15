"""
Copyright (C) 2017 ClaraIO

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Written by ClaraIO <chinodesuuu@gmail.com>, August 2017
"""

from base import Cog, command


# TODO: Translations (cc @Enra @Cameron)
help_text = """Hello! I'm {0.bot.user}.
I'm written in Python using the ClaraIO/Karen framework.

For a list of commands, use `{0.bot.prefix}commands`
For more information on a command, use `{0.bot.prefix}help <command name>`

Github: https://github.com/ClaraIO/Karen
Support: https://discord.gg/rmMTZue"""


class Basic(Cog):
    @command(name="help")
    async def _help(self, ctx, _command: str = None):
        """ Send information about the bot or help on a command """
        if _command is None or self.bot.get_command(_command) is None:
            await ctx.send(help_text.format(ctx))

        comm = self.bot.get_command(_command)

        # TODO: @property on command that utilizes the signature
        await ctx.send(comm.func.__doc__)

    @command()
    async def commands(self, ctx):
        """ Returns a list of commands """
        commands = [c['invokes'][0] for c in self.bot._commands.commands]
        commlist = ", ".join(commands)
        await ctx.send(f"My commands: {commlist}")


def setup(bot):
    bot.add_cog(Basic(bot))
