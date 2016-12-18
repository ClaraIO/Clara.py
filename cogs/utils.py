import sys
import configparser
import youtube_dl
import functools
import aiohttp
import json

normalstdout = sys.stdout
config_file = './config.ini'
config = configparser.ConfigParser(interpolation=None)
config.read(config_file)

from contextlib import suppress

discard = suppress(Exception, IndexError, Warning)

async def get_json(loop, url, headers=None):
	async with aiohttp.ClientSession(loop=loop) as session:
		async with session.get(url, headers=headers or {}) as response:
			res = await response.json()
	return res
	
async def get(loop, url, headers=None):
	async with aiohttp.ClientSession(loop=loop) as session:
		async with session.get(url, headers=headers or {}) as response:
			res = await response.text()
	return res
	
async def get_image(loop, url, headers=None):
	async with aiohttp.ClientSession(loop=loop) as session:
		async with session.get(url, headers=headers or {}) as response:
			res = await response.read()
	bio = io.BytesIO()
	bio.write(res)
	bio.seek(0)
	return bio
	
async def post(loop, url, data, headers=None):
	async with aiohttp.ClientSession(loop=loop) as session:
		async with session.post(url, data=json.dumps(data), headers=(headers or {})) as response:
			res = await response.text()
	return res
	
async def download_song(loop, url, ytdl_options=None):
	opts = ytdl_options or {}
	url = url.split("/")[-1].split("?")[-1]
	opts["outtmpl"] = "songs/" + url.replace(" ",".") + ".flac"
	ydl = youtube_dl.YoutubeDL(opts)
	func = functools.partial(ydl.download, [url])
	await loop.run_in_executor(None, func)
	return opts["outtmpl"]