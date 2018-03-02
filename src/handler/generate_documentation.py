#!/usr/bin/env python3

# https://stackoverflow.com/questions/33517072/

import pdoc

cwd = "."
pdoc.import_path.append(cwd)
module = pdoc.import_module("k3.commands")
documentation = pdoc.Module(module)
print(documentation.html())
