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

import contextlib
import inspect
import io
import pprint
import re
import textwrap
import traceback

import discord

from base import Cog, command, check
import settings


class Code(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        self.ln = 0
        self.env = {}
        self._ = None
        self.stdout = io.StringIO()

    def _format(self, inp, out):
        self._ = out

        res = ""

        # Erase temp input we made
        if inp.startswith("_ = "):
            inp = inp[4:]

        lines = [l for l in inp.split("\n") if l.strip()]
        if len(lines) != 1:
            lines += [""]

        # Create the inpit dialog
        for i, line in enumerate(lines):
            if i == 0:
                s = f"In [{self.ln}]: "

            else:
                # Indent the 3 dots correctly
                s = (f"{{:<{len(str(self.ln))+2}}}...: ").format("")

            if i == len(lines)-2:
                if line.startswith("return"):
                    line = line[6:].strip()

            res += s + line + "\n"

        self.stdout.seek(0)
        text = self.stdout.read()
        self.stdout.close()
        self.stdout = io.StringIO()

        if text:
            res += text + "\n"

        if out is None:
            # No output, return the input statement
            return (res, None)

        res += f"Out[{self.ln}]: "

        if isinstance(out, discord.Embed):
            # We made an embed? Send that as embed
            res += "<Embed>"
            res = (res, out)

        else:
            if (isinstance(out, str) and
                    out.startswith("Traceback (most recent call last):\n")):
                # Leave out the traceback message
                out = "\n"+"\n".join(out.split("\n")[1:])

            pretty = (pprint.pformat(out, compact=True, width=60) if not
                      isinstance(out, str) else str(out))

            if pretty != str(out):
                # We're using the pretty version, start on the next line
                res += "\n"

            if pretty.count("\n") > 20:
                # Text too long, shorten
                l = pretty.split("\n")
                pretty = "\n".join(l[:3]) + "\n ...\n" + "\n".join(l[-3:])

            # Add the output
            res += pretty
            res = (res, None)

        return res

    async def _eval(self, ctx, code):
        self.ln += 1

        if code.startswith("exit"):
            self.ln = 0
            self.env = {}
            return await ctx.send(f"```Reset history!```")

        env = {
            "message": ctx.message,
            "author": ctx.message.author,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "ctx": ctx,
            "self": self,
            "bot": self.bot,
            "inspect": inspect,
            "discord": discord,
            "contextlib": contextlib
        }

        self.env.update(env)

        # Ignore this shitcode, it works
        _code = """
async def func():
    try:
        with contextlib.redirect_stdout(self.stdout):
{}
        if '_' in locals():
            if inspect.isawaitable(_):
                _ = await _
            return _
    finally:
        self.env.update(locals())
""".format(textwrap.indent(code, '            '))

        try:
            exec(_code, self.env)  # pylint: disable=exec-used
            func = self.env['func']
            res = await func()

        except:  # noqa pylint: disable=bare-except
            res = traceback.format_exc()

        out, embed = self._format(code, res)
        await ctx.send(f"```py\n{out}```", embed=embed)

    @check(lambda ctx: ctx.author.id in settings.admins)
    @command()
    async def eval(self, ctx, *, code):
        """ Run eval in a REPL-like format. """
        code = code.strip("`")
        if code.startswith("py\n"):
            code = "\n".join(code.split("\n")[1:])

        if not re.search(  # Check if it's an expression
                r"^(return|import|for|while|def|class|"
                r"from|exit|[a-zA-Z0-9]+\s*=)",
                code, re.M) and len(code.split("\n")) == 1:
            code = "_ = "+code

        await self._eval(ctx, code)


def setup(bot):
    bot.add_cog(Code(bot))
