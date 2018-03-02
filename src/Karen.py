"""
Copyright 2018 (c) ClarityMoe
Licensed under BSD 3-Clause. 
"""

import discord
import json
import redis
import k3

# try to find JSON file
try :
    with open("./config.json") as f:
        config = json.load(f)
except:
    print('Unable to find the configuration file. The client will not load.')
    exit(1)

class Karen(discord.Client):
    def __init__(self, config, args, **options)
        super().__init__(**options)
        self.args = args
        self.config = config
        self.cmd_handler = k3.commands.CommandGroupMixin
        self.commands = self.cmd_handler
    