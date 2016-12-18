import asyncio
import uuid
import io
import sys
import inspect
import math
import traceback
import discord
import importlib
import inspect
from contextlib import redirect_stdout

from discord import Embed

from . import utils
	
class Cog:
	def __init__(self, bot):
		self.bot = bot
		members = inspect.getmembers(self)
		for name, command in members:
			# register commands the cog has
			if isinstance(command, Command) and not isinstance(command, SubCommand): # Ignore SubCommands, they're handled by the Command itself
				command.set_cog(self)
				self.add_command(command)
	
	def add_command(self, command):
		self.bot.commands[command.comm] = command
		for x in command.alias:
			self.bot.commands[x] = command
	
class Command:
	""" A command class to provide methods we can use with it """
	
	def __init__(self, comm, desc='', alias=None, admin=False, unprefixed=False, listed=True):
		self.comm = comm
		self.desc = desc
		self.alias = alias or []
		self.admin = admin
		self.listed = listed
		self.unprefixed = unprefixed
		self.subcommands = {}
		
	def set_cog(self, cog):
		self.cog = cog
		if self.subcommands == {}:
			return
		for n, s in self.subcommands.items(): # AttributeError: 'list' object has no attribute 'items'
			s.cog = cog
	
	def subcommand(self, *args, **kwargs):
		""" Create subcommands """
		return SubCommand(self, *args, **kwargs)
	
	def __call__(self, func):
		""" Make it able to be a decorator """
		self.func = func
		return self
	
	@asyncio.coroutine
	def run(self, message):
		""" Does type checking for command arguments """
	
		args = message.content.split(" ")[1:]
		
		args_name = inspect.getfullargspec(self.func)[0][2:]
		
		if len(args) > len(args_name):
			args[len(args_name)-1] = " ".join(args[len(args_name)-1:])
			
			args = args[:len(args_name)]
			
		ann = self.func.__annotations__
		
		for x in range(0, len(args_name)):
			try:
				v = args[x]
				k = args_name[x]
				
				if not isinstance(v, ann[k]):
					try:
						v = ann[k](v)
						
					except: 
						raise TypeError("Invalid type: got {}, {} expected"
							.format(ann[k].__name__, v.__name__))
						
				args[x] = v
			except IndexError:
				pass

		if len(self.subcommands.keys())>0:
			try:
				subcomm = args.pop(0)
			except:
				yield from self.func(self.cog, message, *args)
				return
			if subcomm in self.subcommands:
				c = message.content.split(" ")
				message.content = c[0] + " " + " ".join(c[2:])
				yield from self.subcommands[subcomm].run(message)
			
			else:
				yield from self.func(self.cog, message, *args)
			
		else:
			try:
				yield from self.func(self.cog, message, *args)
			except TypeError:
				if len(args) < len(args_name):
					raise Exception("Not enough arguments for {}, required arguments: {}"
						.format(self.comm, ", ".join(args_name)))
				else:
					traceback.print_exc(limit=0)
			except:
				yield from self.cog.bot.send_message(message.channel, traceback.format_exc(limit=0))
	

	
class SubCommand(Command):
	""" Subcommand class """
	
	def __init__(self, parent, comm, *alias, desc=""):
		self.comm = comm
		self.parent = parent
		self.subcommands = {}
		parent.subcommands[comm] = self
		for a in alias:
			parent.subcommands[a] = self
	
class DiscordStdout:
	def __init__(self, bot, channel):
		self.bot = bot
		self.channel = channel
	def write(self, x):
		if x.strip():
			self.bot.loop.create_task(self.send(self.channel, x))
	async def send(self, x, y):
		await self.bot.send_message(x, y)
	def flush(*args, **kwargs):
		pass 

class Page(Embed):
	def __init__(self, title, content):
		super().__init__()
		self.title = title
		self.description = content
		
class Paginator:
	def __init__(self, text, title="Page {page_no}", minimum=1, maximum=10000):
		page_no = 0
		self.pages = []

		count = len(text)

		elements = []

		n = math.ceil(math.sqrt(count))
		n = min(n, maximum)

		while count > 0 and len(elements) < n:
			elements.append(1)
			count -= 1

		i = 0
		while count > 0:
			elements[i] += 1
			count -= 1
			i = (i+1) % len(elements)

		# print(elements)

		items = []

		i = 0
		for l in elements:
			j = i+l
			items.append(text[i:j])
			i = j
			
		for l in items:
			page_no += 1
			self.pages.append(Page(title.format(page_no=page_no), "\n".join(l)))
			
	def get_menu(self, bot, channel, user):
		return Menu(bot, channel, user, *self.pages)

class Menu:
	def __init__(self, bot, channel, user, *pages):
		self.bot = bot
		self.channel = channel
		self.pages = pages
		self.length = len(pages)
		self.page = 0
		self.user = user
	
	async def start(self):
		# Check Bot permissions
		if not self.channel.permissions_for(self.channel.server.me).add_reactions:
			raise Exception("Not allowed to add reactions or not given manage_messages")
		if not self.channel.permissions_for(self.channel.server.me).manage_messages:
			raise Exception("Not allowed to add reactions or not given manage_messages")
		# Bot can add and remove reactions
	
		# Send initial message
		self.message = await self.bot.send_message(self.channel, embed=self.pages[0])
		
		# Send initial arrows
		await self.bot.add_reaction(self.message, "\u2B05")
		await self.bot.add_reaction(self.message, "\u27A1")
		
		while True:
			react = await self.bot.wait_for_reaction(["\u2B05","\u27A1"], message=self.message, user=self.user, timeout=60)
			if react is None:
				await self.bot.delete_message(self.message)
				return
			reaction = react.reaction
			message = reaction.message
			if message.id == self.message.id:
				if isinstance(reaction.emoji, str):
					# It's a normal emoji, which we want
					if reaction.emoji == "\u2B05":
						await self.scroll_left()
					elif reaction.emoji == "\u27A1":
						await self.scroll_right()
				
				await self.bot.remove_reaction(message, reaction.emoji, react.user)
	
	async def scroll_right(self):
		if self.page+1 == self.length:
			# Reached maximum page
			self.page = 0
		else:
			self.page += 1
			
		# Update page
		await self.bot.edit_message(self.message, embed=self.pages[self.page])
	
	async def scroll_left(self):
		if self.page == 0:
			# Reached page 1
			self.page = self.length-1
		else:
			self.page -= 1
			
		# Update page
		await self.bot.edit_message(self.message, embed=self.pages[self.page])
		
class Bot(discord.Client):
	def __init__(self, prefix, admins, *args, **kwargs):
		self.prefix = prefix
		self.admins = admins
		self.commands = {}
		self.cogs = {}
		self.count = 0
		super().__init__(*args, **kwargs)
		
	def load_cog(self, name):
		if name in self.cogs:
			return

		lib = importlib.import_module(name)
		if not hasattr(lib, 'setup'):
			del lib
			raise Exception('extension does not have a setup function')

		cog = lib.setup(self)
		del lib
		self.cogs[cog.__class__.__name__] = cog

	def unload_cog(self, name):
		cog = self.cogs.get(name)
		if cog is None:
			return

		for key, command in self.commands.copy().items():
			if command.cog is cog:
				del self.commands[key]
		del cog
		
	def gather_cogs(self):
		with open("cog_list.txt") as cog_list:
			for module in cog_list.read().split("\n"):
				self.load_cog(module)
			
	def reload(self):
		self.cogs = {}
		self.commands = {}
		self.gather_cogs()

	async def on_message(self, m):
		self.count += 1
		if m.content.startswith("<font"):
			m.content = m.content[20:len(m.content)-7]
		if m.author.bot: return
		
		rawm = m
		m = m.content
		if m.startswith(self.prefix):
			m = m[len(self.prefix):]
			l = m.split(" ")
			w = l.pop(0).lower()
			if w in self.commands:
				if self.commands[w].unprefixed: return
				if self.commands[w].admin and not rawm.author.id in self.admins:
					await self.send_message(rawm.channel, "You are not allowed to use this command")
					return
				try:
					with redirect_stdout(DiscordStdout(self, rawm.channel)):
						await self.commands[w].run(rawm)
				except discord.errors.ClientException:
					await self.send_message(rawm.channel, "The bot is already connected to a voice channel. If you feel like this is not true, use 'resetmusic")
				except:
					await self.send_message(rawm.channel, traceback.format_exc(limit=0))
					with redirect_stdout(utils.normalstdout):
						print("--- PRINTING TRACEBACK IN COMMAND {} ---".format(self.commands[w].comm))
						traceback.print_exc()
						print("--- END OF TRACEBACK ---")
		else:
			if rawm.server is None: return
				
			if rawm.server.id == "81384788765712384":
				return
			l = m.split(" ")
			w = l.pop(0).lower()
			if w in self.commands:
				if not self.commands[w].unprefixed: return
				with utils.discard:
					await self.commands[w].run(rawm)
	#

	async def on_ready(self):
		while not self.servers:
			await asyncio.sleep(0.1)
		while self.servers == []:
			await asyncio.sleep(0.1)
		while None in self.servers:
			await asyncio.sleep(0.1)
		tm = math.floor(len(self.servers)/5)
		for _ in range(1,tm):
			await asyncio.sleep(1)
