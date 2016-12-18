import asyncio

import cogs.utils as utils

from cogs.classes import Bot

try:
	import uvloop
	asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
	print("Please install uvloop, `pip install uvloop`")

admins = (
	"161866631004422144",
	"156324425673736192"
)

token = utils.config.get('Discord', 'Token', fallback=None)
client = Bot(utils.config.get('Discord', 'Prefix', fallback="!"), admins)
client.gather_cogs()
client.run(token)