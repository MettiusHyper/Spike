import discord
from discord.ext import commands, tasks

from core import Vars

class Basic(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description = 'Returns the current ping of the bot', aliases = ['latency', 'pong'])
	async def ping(self, ctx):
		await ctx.send("{emoji} Pong!\n{bot}'s current ping is {ping} ms"
			.format(emoji = ':ping_pong:', bot = self.client.user.name, ping = round(self.client.latency*1000))
		)

	@commands.command(description = 'Returns some useful informations about the bot', aliases = ['information', 'informations', 'informazioni', 'informazione'])
	async def info(self, ctx):
		devs = [await self.client.fetch_user(int(dev)) for dev in Vars.collection.find_one({'_id' : 'developer'})['developers']]
		fields = [
			('Version <:version:768126836014055465>', f'v. {Vars.version}'),
			('Developers <:botdev:768126563605676082>', ' '.join([dev.mention for dev in devs])), ('\u200B', '\u200B'),
			('Servers <:online:768127882932256859>', "{}'s in {} servers".format(self.client.user.name, len(self.client.guilds))),
			('Bot Invite <:bot:768127528862482433>', '[{0}](https://{0})'.format(Vars.invite_link)), ('\u200B', '\u200B')		   
		]
		info_embed = discord.Embed(color = Vars.color)
		[info_embed.add_field(name = field[0], value = field[1]) for field in fields]
		await ctx.send(
			content = 'Spike is a simple moderation bot, with tons of\nuseful features to moderate a discord server.',
			embed = info_embed
		)

def setup(client):
	client.add_cog(Basic(client))