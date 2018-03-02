# k3 modules

A module in k3 is simply a Python file that contains `commands.Command` objects in the namespace.

For example:

```py
import random

from k3 import commands


@commands.command()
async def ping(ctx):
    """A simple ping command."""
    await ctx.send("Pong!")


@commands.command()
async def xkcd(ctx):
    """A simple xkcd command."""
    url = "https://xkcd.com/info.0.json"
    async with ctx.bot.session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            await ctx.send(data["img"])
        else:
            await ctx.send("Could not reach xkcd.")

@commands.cooldown(6, 12)
@commands.command()
async def roll(ctx, number_of_dice: int):
    """Rolls some dice.
    
    * number_of_dice - The number of dice to roll.
    """
    rolls = []
    for i in range(0, number_of_dice):
        rolls.append(random.randint(1, 6))
    await ctx.send(", ".join(rolls)
```
