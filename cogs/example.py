from classes import Cog, Command


class ExampleCog(Cog):
    @Command("example", description="Example command.")
    async def example(self, message, arg1: int, optarg: str=None):
        if optarg is None:
            await self.bot.send_message(
                message.channel,
                "Got a number: " + str(arg1))
        else:
            await self.bot.send_message(
                message.channel,
                "Number: {}\nString: {}"
                .format(arg1, optarg))


def setup(bot):
    return ExampleCog(bot)
