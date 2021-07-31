import discord
from discord.ext import commands

from core import *

class HelpCommand(commands.MinimalHelpCommand):
	async def send_bot_help(self, mapping):
		channel = self.get_destination()
		try:
			await channel.send(embed=help_embed(self.context.bot, channel.guild))
		except:
			await channel.send(embed=help_embed(self.context.bot, None))

	async def send_command_help(self, command):
		embed = discord.Embed(title =  str(command), description = command.description, color = Vars.color)
		embed.set_footer(text = '<> is required | [] is optional')
		embed.add_field(name = 'Usage', value = '```' + self.get_command_signature(command) + '```')
		alias = command.aliases
		if alias:
			embed.add_field(name='Aliases', value='```' + ', '.join(alias) + '```')
		await self.get_destination().send(embed=embed)

	async def send_group_help(self, group):
		embed = discord.Embed(title =  str(group), description = group.description, color = Vars.color)
		commands = ''
		for command in group.commands:
			commands += (str(command) + '\n')
		embed.add_field(name = 'Commands', value = '```' + commands + '```')
		alias = group.aliases
		if alias:
			embed.add_field(name='Aliases', value='```' + ', '.join(alias) + '```')
		await self.get_destination().send(embed=embed)

	async def send_cog_help(self, cog):
		embed = discord.Embed(title = cog.qualified_name, description = self.get_opening_note(), color = Vars.color)
		commands = ''
		for command in cog.get_commands():
			commands += (str(command) + '\n')
		embed.add_field(name = 'Commands', value = commands)
		await self.get_destination().send(embed=embed)

	async def send_error_message(self, error):
		await self.get_destination().send(Emoji.cross + ' ' + error)

class Help(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.client.help_command = HelpCommand()

	@commands.command(description = 'Shows a complete list of every command', aliases = ['command'])
	async def commands(self, ctx):
		prefix = custom_prefix(self.client, ctx.message)[1]
		description = ''
		for command in self.client.commands:
			if command.cog != self.client.get_cog('Dev'):
				description += prefix + str(command) + ' ' + command.signature + '\n'
		embed = discord.Embed(title = 'Commands', color = Vars.color, description = description)
		embed.set_footer(text = 'Type {}help [command] for more informations\n<> is required | [] is optional'.format(prefix))
		await ctx.send(embed = embed)

def setup(client):
	client.add_cog(Help(client))