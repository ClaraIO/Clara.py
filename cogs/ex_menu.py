from .classes import Cog, Command, Paginator, Menu, Page

class ExampleMenu(Cog):

	@Command("paginated", desc="A [aginated menu")
	async def paginated_menu(self, message):
		text = ""
		for x in range(100):
			text += "Line {}".format(x)

		paginator_obj = Paginator(text)
		menu_obj = paginator.get_menu(self.bot, self.channel, message.author)
		await menu_obj.start()

	@Command("custom", desc="A custom menu")
	async def custom_menu(self, message):
		p1 = Page("Title", "body")
		p2 = Page("Title", "sample text")
		p3 = Page("Title", "awau")
		menu_obj = Menu(self.bot, self.channel, message.author, p1,p2,p3)
		await menu_obj.start()


def setup(bot):
	return ExampleMenu(bot)