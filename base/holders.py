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


__all__ = ["CommandHolder"]


class CommandHolder:
    """ DONT USE THIS CLASS YOURSELF!
    This is a holder class used by the Bot class, and should never be
    used manually."""
    def __init__(self):
        self.commands = []

    def add_command(self, command):
        """ Registers a command """
        self.commands.append({
            "invokes": [command.name] + command.aliases,
            "command": command,
            "subcommands": command.subcommands
        })

    def get_command(self, name):
        """ Returns a command """
        for command in self.commands:
            if name in command["invokes"]:
                return command["command"]

        return False

    def remove_command(self, name):
        """ Removes a command """
        for i, command in enumerate(self.commands):
            if name in command["invokes"]:
                del self.commands[i]
                return True

        return False
