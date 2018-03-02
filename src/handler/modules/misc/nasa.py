#!/usr/bin/env python3

"""NASA image commands."""

from k3 import commands

BASE_URL_NASA_IOTD = "https://api.pandentia.cf/nasa/iotd"
BASE_URL_NASA_APOD = "https://api.pandentia.cf/nasa/apod"


@commands.cooldown(6, 12)
@commands.command()
async def iotd(ctx):
    """Fetch NASA's Image of the Day."""

    async with ctx.bot.session.get(BASE_URL_NASA_IOTD) as response:
        if response.status == 200:
            data = await response.json()
            response = data["response"]
            if response["image_url"]:
                message = [
                    ctx.f.bold(response["title"]),
                    ctx.f.no_embed_link(response["link"]),
                    response["image_url"],
                    response["description"]
                ]
                message = "\n".join(message)
                await ctx.send(message)
            else:
                await ctx.send(response["link"])
        else:
            message = "Could not fetch image. :<"
            await ctx.send(message)


@commands.cooldown(6, 12)
@commands.command()
async def apod(ctx):
    """Fetch NASA's Astronomy Picture of the Day."""

    async with ctx.bot.session.get(BASE_URL_NASA_APOD) as response:
        if response.status == 200:
            data = await response.json()
            response = data["response"]
            if response["image_url"]:
                message = [
                    ctx.f.bold(response["title"]),
                    ctx.f.no_embed_link(response["link"]),
                    response["image_url"],
                    response["description"]
                ]
                message = "\n".join(message)
                await ctx.send(message)
            else:
                await ctx.send(response["link"])
        else:
            message = "Could not fetch image. :<"
            await ctx.send(message)
