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


import json

from .exceptions import SyntaxError  # noqa: ignore=E402 pylint: disable=redefined-builtin,wrong-import-position


__all__ = ["LocaleEngine", "SyntaxError"]


class LocaleEngine:
    """
    Handles translation data
    Translation data format in JSON
    """

    def __init__(self, filename):
        self.data = {}
        self.filename = filename
        self.reload()

    def __getattr__(self, item):
        return self.data[item]

    def reload(self):
        """ Reloads data from the translation file """

        try:
            with open(self.filename) as f:
                data = json.load(f)

        except json.JSONDecodeError:
            raise SyntaxError("Invalid JSON in translation file!")

        else:
            self.data = data  # noqa: ignore=F821
