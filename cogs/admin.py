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

import inspect
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

    def _format(self, inp, out):
        self._ = out

        res = ""

        if inp.startswith("_ = "):
            inp = inp[4:]

        for i, line in enumerate(inp.split("\n")):
            if i == 0:
                s = f"In [{self.ln}]: "

            else:
                s = (f"{{:<{len(str(self.ln))+2}}}...: ").format("")

            res += s+line+"\n"

        if out is None:
            return (res, None)

        res += f"Out[{self.ln}]: "

        if isinstance(out, discord.Embed):
            res += "<Embed>"
            res = (res, out)

        else:
            if (isinstance(out, str) and
                    out.startswith("Traceback (most recent call last):\n")):
                out = "\n"+"\n".join(out.split("\n")[1:])

            pretty = (pprint.pformat(out, compact=True, width=60) if
                      not isinstance(out, str) else str(out))
            if pretty != str(out):
                res += "\n"

            if pretty.count("\n") > 20:
                l = pretty.split("\n")
                pretty = "\n".join(l[:3]) + "\n ...\n" + "\n".join(l[-3:])

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
            "discord": discord
        }

        self.env.update(env)

        # Ignore this shitcode, it works
        _code = """
async def func():
    old_locals = locals().copy()
    try:
{}
        new_locals = {{k:v for k,v in locals().items()
                       if (k not in old_locals and
                           k not in ['old_locals','_','func'])}}
        if new_locals != {{}}:
            return new_locals
        else:
            if '_' in locals() and inspect.isawaitable(_):
                _ = await _
            return _
    finally:
        self.env.update({{k:v for k,v in locals().items()
                          if (k not in old_locals and
                              k not in ['old_locals','_','new_locals','func'])
                        }})
""".format(textwrap.indent(code, '        '))

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
