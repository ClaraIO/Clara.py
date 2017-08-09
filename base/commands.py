"""
Copyright (C) 2017 Martmists

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

Written by Martmists <legal@martmists.com>, August 2017
"""

import inspect

from .holders import CommandHolder
from .converters import Converter
from .translations import Translation


__all__ = ["command", "Command"]


def command(bot=None, **kwargs):
    """ Command creation decorator when not using @bot.command """
    def decorator(func):  # pylint: disable=missing-docstring
        return Command(func=func, bot=bot, **kwargs)
    return decorator


class Command:
    """ Command dataclass """
    def __init__(self, **kwargs):
        self.func = kwargs['func']
        self.sig = inspect.signature(self.func)
        self.name = kwargs.get("name") or self.func.name
        self.aliases = kwargs.get("aliases") or []
        self.pass_ctx = kwargs.get("pass_context") or True
        self.subcommands = CommandHolder()
        if "translation_file" in kwargs:
            self.translation = Translation(kwargs.get("translation_file"))
        kwargs.get("bot").add_command(self)

    async def invoke(self, context):
        """ Run the command or optionally subcommands """
        args = context.args

        if self.has_subcommands and args[0] in self.subcommands.commands:  # noqa pylint: disable=no-member
            comm = self.subcommands.get_command(args.pop(0))
            context.update({"invoked_subcommand": comm})
            return await comm.invoke(context)

        func_args = self.sig.parameters.values()

        if self.pass_ctx:
            args.insert(0, context)

        kwarg_data = {}

        for i, arg in enumerate(func_args):
            if arg.name == "self":
                continue

            if arg.name == "*":
                args[i] = " ".join(args[i:])
                del args[i+1:]

            if arg.annotation == arg.empty:
                kwarg_data[arg.name] = args[i]

            elif (inspect.isfunction(arg.annotation) or
                  (inspect.isclass(arg.annotation) and not
                   issubclass(arg.annotation, Converter))):
                kwarg_data[arg.name] = arg.annotation(args[i])

            elif (isinstance(type(arg.annotation), Converter) or
                  inspect.isclass(arg.annotation)):
                if inspect.isclass(arg.annotation):
                    inst = arg.annotation()
                kwarg_data[arg.name] = inst.convert(args[i], context)

        @property
        def has_subcommands(self):  # pylint: disable=unused-variable
            """ Returns true if the command has subcommands """
            return bool(self.subcommands.commands)

        def subcommand(self, **kwargs):  # pylint: disable=unused-variable
            """ Creates a subcommand for the command
            Used as decorator
            """
            return command(bot=self, **kwargs)
