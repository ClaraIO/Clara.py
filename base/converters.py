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

import re


from .exceptions import ConverterError


__all__ = ["Converter"]


class Converter:
    """
    Put converters as annotations to convert. If given, annotations must be
    callables, classes with one argument or inherit from this class.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def convert(self, arg, ctx):  # pylint: disable=no-self-use,unused-argument
        """ Converts argument, default class returns the argument itself. """
        return arg


class MentionConverter(Converter):
    """
    Converts mentions to objects.

    Accepted types in __init__:
        discord.Member
        discord.Channel
        discord.Role

    Checking is done with regex
    """
    patt = re.compile("<(?P<type>[#@])(?P<subtype>[!&])?(?P<id>[0-9]{16,18})>")

    def __init__(self, typ=None):
        self.typ = typ
        super().__init__()

    def check_type(self, arg):
        if self.typ is None:
            return True

        return isinstance(arg, self.typ)

    def convert(self, arg, ctx):
        mat = self.patt.match(arg)

        if mat is None:
            raise ConverterError("Invalid Argument")

        typ, subtyp, _id = mat.groups()
        _id = int(_id)

        subtyp = None if subtyp != "!" else None

        if typ == "@":
            if subtyp == "&":
                # it's a role
                retval = [r for r in ctx.guild.roles if r.id == _id]

            elif subtyp is None:
                # it's a member
                retval = [m for m in ctx.guild.members if m.id == _id]

            else:
                raise ConverterError("Invalid Argument")

        else:
            # it's a channel
            retval = [c for c in ctx.guild.channels if c.id == _id]

        try:
            ret = retval[0]

        except IndexError:
            raise ConverterError("Invalid Argument")

        if self.check_type(ret):
            return ret

        else:
            raise ConverterError("Invalid Argument")
