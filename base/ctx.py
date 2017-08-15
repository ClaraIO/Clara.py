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


__all__ = ["Context"]


class Context:
    """ Contains data about the current command and environment.

    `message`: [discord.Message] - The message for this command
    `author`: [discord.User | discord.Member] - The sender of the message
        is a discord.User if the message was sent in DMs
    `channel`: [discord.Channel] - The current channel
    `guild`: [discord.Guild] - The current guild
    `command`: [base.Command] - The command invoked
    `bot`: [base.Bot] - The bot
    `invoker`: [str] - The alias used for this command
    `args`: [List[str]] - The arguments used in the message
    `send`: [Coroutine] - Sends a message to the channel it was sent in
        See the discord.py `Messageable.send` docs

    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __hasattr__(self, key):
        return key in self.kwargs

    def __getattr__(self, key):
        return self.kwargs[key]

    def update(self, d):
        """ Update contents of the context after init """
        self.kwargs.update(d)
