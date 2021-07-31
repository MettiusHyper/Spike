import io, discord, datetime
from discord.ext import commands
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

from core import *

blue = '#677BC4'
gray = '#B9BBBE'
black = '#292B2F'

class ServerInfo(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.group(name = 'serverinfo', description = "Returns lots of informations about the server, with a graph that displays the server's growth", invoke_without_command = True, case_insensitive = True)
	@commands.guild_only()
	async def serverinfo(self, ctx):
		embed = discord.Embed(colour = Vars.color)
		embed.set_author(name = f'{ctx.guild.name} ({ctx.guild.id})', icon_url = ctx.guild.icon_url)
		owner = await self.client.fetch_user(ctx.guild.owner_id)
		embed.add_field(name = 'Users <:members:772528856187666443>', value = str(ctx.guild.member_count))
		embed.add_field(name = 'Roles', value = str(len(ctx.guild.roles)))
		embed.add_field(name = 'Boosts <:boost:772528846775648258>', value = str(ctx.guild.premium_subscription_count))
		embed.add_field(name = 'Channels <:channels:772528907156586537>', value = str(len(ctx.guild.text_channels) + len(ctx.guild.voice_channels)))
		embed.add_field(name = 'Owner <:owner:772528832804290620>', value = owner.mention)
		embed.add_field(name = 'Bots <:bot:768127528862482433>', value = sum(member.bot for member in ctx.guild.members))
		embed.set_footer(text = 'Data for the cart obtained every day at 12:00 UTC')
		try:
			data = Vars.collection.find_one({'_id' : ctx.guild.id})['users']
			if data == False:
				embed.add_field(name = '\u200C', value = '{cross} Graph has been disabled. Use `{p}userinfo on`'.format(cross = Emoji.cross, p = Dev.prefix(self.client, ctx)[1]))
				return await ctx.send(embed = embed)
		except:
			data = []

		if len(data) == 0:
			embed.add_field(name = '\u200C', value = '{} Not enough data to create a chart! Please try again tomorrow.'.format(Emoji.cross))
			return await ctx.send(embed = embed)
		#getting x, the date part
		x = []
		if datetime.datetime.now().hour > 12:
			date = datetime.date.today() - datetime.timedelta(days = len(data) - 1)
		else:
			date = datetime.date.today() - datetime.timedelta(days = len(data))
		for el in data:
			x.append(date.strftime('%d/%m'))
			date = date + datetime.timedelta(days = 1)

		data_stream = io.BytesIO()
		plt.figure(figsize=(6.5, 3), facecolor = black)
		# plotting the points
		plt.plot(x, data, color = blue)

		#setting colors	   
		ax = plt.gca()
		ax.set_facecolor(black)
		ax.tick_params(colors =  gray)
		ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
		for el in ax.spines:
			ax.spines[el].set_color(gray)
		plt.savefig(data_stream, format='png', bbox_inches='tight', dpi = 80)
		data_stream.seek(0)
		chart = discord.File(data_stream,filename='image.png')
		embed.set_image(url='attachment://image.png')
		await ctx.send(embed = embed, file = chart)

	@serverinfo.command(name = 'off')
	async def serverinfo_off(self, ctx):
		Vars.collection.update_one({'_id' : ctx.guild.id}, {'$set' : {'users' : False}})
		await ctx.send(f'{Emoji.tick} We will not collect data for the graph on this server anymore.')
	
	@serverinfo.command(name = 'on')
	async def serverinfo_on(self, ctx):
		Vars.collection.update_one({'_id' : ctx.guild.id}, {'$set' : {'users' : []}})
		await ctx.send(f'{Emoji.tick} From now on the data for the graph will be collected.')

def setup(client):
	client.add_cog(ServerInfo(client))