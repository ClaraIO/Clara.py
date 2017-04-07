import json

from classes import Bot

with open("config.json") as config:
    settings = json.load(config)

# If you need sharding, use
# Bot(..., shard_id=x, shard_count=y)
bot = Bot(
    prefix = settings.get("prefix") or "!",
    admins = settings.get("admins") or []
)


bot.run(settings.get("token"))
