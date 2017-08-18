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

from .holders import CommandHolder
from .converters import Converter
from .translations import LocaleEngine
from .exceptions import CheckFailed, FrameworkException


__all__ = ["command", "Command"]


def command(bot=None, **kwargs):
    """ Command creation decorator when not using @bot.command """
    def decorator(func):  # pylint: disable=missing-docstring
        return Command(func=func, bot=bot, **kwargs)
    return decorator


class Command:
    """ Command dataclass """
    def __init__(self, **kwargs):
        func = kwargs['func']
        self.func = func
        self.sig = inspect.signature(func)
        self.name = kwargs.get("name") or func.__name__
        self.aliases = kwargs.get("aliases") or []
        self.pass_ctx = kwargs.get("pass_context", True)
        self.subcommands = CommandHolder()
        if "translation_file" in kwargs:
            self.translation = LocaleEngine(kwargs.get("translation_file"))
        if kwargs.get("bot") is not None:
            kwargs['bot'].add_command(self)
        self.checks = []
        self.cog = None

    def set_cog(self, cog):
        self.cog = cog

    def _do_check(self, _check, ctx):  # pylint: disable=no-self-use
        """ Run a check on the ctx """
        try:
            assert _check(ctx)

        except Exception as e:  # noqa pylint: disable=broad-except
            raise e from CheckFailed

    async def invoke(self, context):  # pylint: disable=too-many-branches
        """ Run the command or optionally subcommands """
        args = context.args

        if self.has_subcommands and args[0] in self.subcommands.commands:  # noqa pylint: disable=no-member
            # The command's subcommand is called, invoke that
            comm = self.subcommands.get_command(args.pop(0))
            context.update({"invoked_subcommand": comm})
            return await comm.invoke(context)

        # Run checks
        for _check in self.checks:
            self._do_check(_check, context)

        # Get the function arguments
        func_args = self.sig.parameters.values()

        if self.pass_ctx:
            # pass ctx
            args.insert(0, context)

        kwarg_data = {}

        for i, arg in enumerate(func_args):
            # Iterate over the function arguments

            if arg.name == "self":
                args.insert(0, None)  # dummy value
                kwarg_data['self'] = self.cog
                continue

            try:
                if arg.kind.value == 3:  # keyword-only
                    # Consume rest
                    args[i] = " ".join(args[i:])
                    del args[i+1:]

                if arg.annotation == arg.empty:
                    # No annotation, don't convert
                    kwarg_data[arg.name] = args[i]

                elif (inspect.isfunction(arg.annotation) or
                      (inspect.isclass(arg.annotation) and not
                       issubclass(arg.annotation, Converter))):
                    # The annotation is a callable/class, but not a Converter
                    kwarg_data[arg.name] = arg.annotation(args[i])

                elif (isinstance(arg.annotation, Converter) or
                      inspect.isclass(arg.annotation)):
                    if inspect.isclass(arg.annotation):
                        # It's a class, instantiate it with no args
                        inst = arg.annotation()
                    else:
                        # Already an instance
                        inst = arg.annotation

                    # Simply convert using the converter's `convert` method
                    kwarg_data[arg.name] = inst.convert(args[i], context)

                else:
                    raise FrameworkException("Invalid type annotation!")

            except IndexError:
                if arg.default != arg.empty:
                    break
                raise FrameworkException(f"Missing argument: {arg.name}!")

        # Run the function using the arguments collected
        await self.func(**kwarg_data)

    @property
    def has_subcommands(self):  # pylint: disable=unused-variable
        """ Returns true if the command has subcommands """
        return bool(self.subcommands.commands)

    def subcommand(self, **kwargs):  # pylint: disable=unused-variable
        """ Creates a subcommand for the command
        Used as decorator
        """
        return command(bot=self, **kwargs)
