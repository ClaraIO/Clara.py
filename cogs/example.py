from .classes import Cog, Command

class Example(Cog):
	
	@Command("name", desc="description", alias=["awau"])
	async def example_command(self, message):
		await self.bot.send_message(message.channel, "This is an example command")

def setup(bot):
	return Example(bot)