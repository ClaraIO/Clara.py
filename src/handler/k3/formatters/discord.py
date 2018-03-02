#!/usr/bin/env python3

import k3.formatters.core


class DiscordFormatter(k3.formatters.core.BaseFormatter):

    def codeblock(self, text, syntax: str=""):
        return f"```{syntax}\n{text}```".strip("\n")

    def bold(self, text):
        return f"**{text}**"

    def italic(self, text):
        return f"*{text}*"

    def underline(self, text):
        return f"__{text}__"

    def no_embed_link(self, text):
        return f"<{text}>"
