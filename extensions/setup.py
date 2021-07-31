import discord, asyncio
from discord.ext import commands

from core import *

def getChannel(ctx, name):
	logs = Vars.collection.find_one({'_id' : ctx.guild.id})['logs']
	if name in logs and ctx.guild.get_channel(logs[name]) != None:
		return ctx.guild.get_channel(logs[name]).mention
	else:
		return '`Not setted`'

logsNames = {
	'🔨' : 'Ban',
	'👢' : 'Kick',
	'🔇' : 'Mute',
	'☢️' : 'Warn'
}

class Setup(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	@commands.guild_only()
	@commands.has_permissions(administrator = True)
	async def prefix(self, ctx, prefix : str = None):
		current_prefix = custom_prefix(self.client, ctx.guild)[1]
		if prefix == None:
			return await ctx.send('The current prefix for {} in this server is `{}`'.format(self.client.user.name, current_prefix))
		if len(prefix) > 3:
			return await ctx.send('{} Please specify a prefix with at most 3 characters'.format(Emoji.cross))
		Vars.collection.update_one({"_id" : ctx.guild.id}, {"$set" : {"prefix" : prefix}})
		await ctx.send('{} The prefix has been setted correctly, now you can use `{}` as a prefix in this server'.format(Emoji.tick, prefix))

	@prefix.error
	async def prefix_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Administrator)".format(Emoji.cross))


	@commands.group(description = 'A command that lets you change every setting of the bot', aliases = ["settings", "impostazioni", "config", "configuration"], invoke_without_command = True, case_insensitive = True)
	@commands.has_permissions(administrator = True)
	@commands.guild_only()
	async def setup(self, ctx):
		prefix = custom_prefix(self.client, ctx.message)[1]
		await ctx.send(embed = discord.Embed(color = Vars.color, title = 'Setup :gear:')
			.add_field(name = '<:channels:772528907156586537> Logs', value='Use `{}settings logs`'.format(prefix))
			.add_field(name = '{} BanAppeal'.format(Emoji.ban), value='Use `{}settings banappeal`'.format(prefix))
			.add_field(name = '\u200C', value = '\u200C')
			.add_field(name = '{} MuteRole'.format(Emoji.mute), value='Use `{}settings muterole`'.format(prefix))
			.add_field(name = ':pencil: Prefix', value='Use `{}prefix`'.format(prefix))
			.add_field(name = '\u200C', value = '\u200C')
		)
	
	@setup.error
	async def setup_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Administrator)".format(Emoji.cross))

	@setup.command(name = 'logs')
	@commands.has_permissions(administrator = True)
	async def logs(self, ctx):
		logs = Vars.collection.find_one({'_id' : ctx.guild.id})['logs']
		msg = await ctx.send(
			embed = discord.Embed(color = Vars.color, title = 'Logs <:channels:772528907156586537>', description = 'React with the respective emoji to edit the channel.')
			.add_field(name = 'Ban Channel {}'.format(Emoji.ban), value = getChannel(ctx, 'ban'))
			.add_field(name = 'Kick Channel {}'.format(Emoji.kick), value = getChannel(ctx, 'kick'))
			.add_field(name = '\u200C', value = '\u200C')
			.add_field(name = 'Mute Channel {}'.format(Emoji.mute), value = getChannel(ctx, 'mute'))
			.add_field(name = 'Warn Channel {}'.format(Emoji.warn), value = getChannel(ctx, 'warn'))
			.add_field(name = '\u200C', value = '\u200C')
		)
		for el in logsNames:
			await msg.add_reaction(el)
		try:
			def check(reaction, user):
				return user == ctx.author and str(reaction.emoji) in logsNames
			reaction, user = await self.client.wait_for('reaction_add', timeout = 60.0, check = check)
			await msg.edit(
				embed = discord.Embed(
					color = Vars.color,
					title = '{} Channel {}'.format(logsNames[str(reaction)], reaction),
					description = 'React with:\n:green_square: to specify a new channel\n:red_square: to remove the current channel'
				)
				.add_field(name = 'Current Channel', value = getChannel(ctx, logsNames[str(reaction)].lower()))
			)
			message = await ctx.channel.fetch_message(msg.id)
			await message.clear_reactions()
		except asyncio.TimeoutError:
			message = await ctx.channel.fetch_message(msg.id)
			return await message.clear_reactions()
		await msg.add_reaction('🟩')
		await msg.add_reaction('🟥')

		try:
			def check(reaction, user):
				return user == ctx.author and str(reaction.emoji) in ('🟥', '🟩')
			react, user = await self.client.wait_for('reaction_add', timeout = 60.0, check = check)
			if str(react) == '🟩':
				await ctx.send('Send a message with only the mention of the **channel**.')
				def check(m):
					return m.author == ctx.author
				command = await self.client.wait_for('message', timeout = 60.0, check=check)
				command = command.content
				try:
					if command.startswith('<#') and command.endswith('>'):
						command = int(command.strip()[-19:-1])
					else:
						command = int(command)
				except:
					pass
				if (type(command) == int and len(str(command)) == 18) and ctx.guild.get_channel(command) != None:
					if ctx.guild.get_channel(command).type != discord.ChannelType.text:
						return await ctx.send('{} please specify only text channels'.format(Emoji.cross))
					logs.update({logsNames[str(reaction)].lower() : command})
					Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'logs' : logs}})
					await ctx.send('{} Channel has been setted'.format(Emoji.tick))
				else:
					await ctx.send('{} Please specify a valid channel'.format(Emoji.cross))
			elif str(react) == '🟥':
				if getChannel(ctx, logsNames[str(reaction)].lower()).startswith('`'):
					await ctx.send('{} No channel has been previusly setted.'.format(Emoji.cross))
				else:
					del logs[logsNames[str(reaction)].lower()]
					Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'logs' : logs}})
					await ctx.send("{} Channel has been removed from the bot's settings".format(Emoji.tick))
			raise asyncio.TimeoutError
		except asyncio.TimeoutError:
			message = await ctx.channel.fetch_message(msg.id)
			await message.clear_reactions()

	@logs.error
	async def setup_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Administrator)".format(Emoji.cross))

	@setup.command(name = 'banappeal')
	@commands.has_permissions(administrator = True)
	async def banappeal(self, ctx):
		settings = Vars.collection.find_one({'_id' : ctx.guild.id})['settings']
		if 'banappeal' in settings:
			link = settings['banappeal']
		else:
			link = '`Not setted`'
		msg = await ctx.send(
			embed = discord.Embed(
				color = Vars.color,
				title = 'BanAppeal {emoji}'.format(emoji = Emoji.ban),
				description = 'React with:\n:green_square: to specify a new link\n:red_square: to remove the current link'
			)
			.add_field(name = 'Setted link', value = link)
		)
		await msg.add_reaction('🟩')
		await msg.add_reaction('🟥')
		try:
			def check(reaction, user):
				return user == ctx.author and str(reaction.emoji) in ('🟥', '🟩')
			reaction, user = await self.client.wait_for('reaction_add', timeout = 60.0, check = check)
			if str(reaction) == '🟩':
				await ctx.send('Send a message with only the new **link** to be used to appeal bans.')
				def check(m):
					return m.author == ctx.author
				try:
					command = await self.client.wait_for('message', timeout = 60.0, check=check)
					command = command.content
					if command.startswith('https://docs.google.com/forms'):
						settings.update({'banappeal' : command.strip()})
						Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'settings' : settings}})
						await ctx.send('{} Link has been setted'.format(Emoji.tick))
					else:
						await ctx.send('{} Please specify a valid link (only link starting with <https://docs.google.com/forms> are allowed)'.format(Emoji.cross))
				except:
					raise asyncio.TimeoutError
			elif str(reaction) == '🟥':
				if link.startswith('`'):
					await ctx.send('{} No link has been previusly setted.'.format(Emoji.cross))
				else:
					del settings['banappeal']
					Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'settings' : settings}})
					await ctx.send("{} Link has been removed from the bot's settings".format(Emoji.tick))
			raise asyncio.TimeoutError
		except asyncio.TimeoutError:
			message = await ctx.channel.fetch_message(msg.id)
			await message.clear_reactions()

	@banappeal.error
	async def setup_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Administrator)".format(Emoji.cross))

	@setup.command(name = 'muterole')
	@commands.has_permissions(administrator = True)
	@commands.guild_only()
	async def muterole(self, ctx):
		settings = Vars.collection.find_one({'_id' : ctx.guild.id})['settings']
		if 'muterole' in settings and ctx.guild.get_role(settings['muterole']) != None:
			role = ctx.guild.get_role(settings['muterole']).mention
		else:
			role = '`Not setted`'
		msg = await ctx.send(
			embed = discord.Embed(
				color = Vars.color,
				title = 'MuteRole {}'.format(Emoji.mute),
				description = 'React with:\n:green_square: to specify a custom role\n:red_square: to remove the current role\n{} to create a standard one'.format(Emoji.mute)
			)
			.add_field(name = 'Setted role', value = role)
		)
		await msg.add_reaction('🟩')
		await msg.add_reaction('🟥')
		await msg.add_reaction('🔇')
		try:
			def check(reaction, user):
				return user == ctx.author and str(reaction.emoji) in ('🟥', '🔇', '🟩')
			reaction, user = await self.client.wait_for('reaction_add', timeout = 60.0, check = check)
			if str(reaction) == '🟩':
				await ctx.send('Send a message with only the **mention** or the **id** of the role.')
				def check(m):
					return m.author == ctx.author
				try:
					command = await self.client.wait_for('message', timeout = 60.0, check=check)
					command = command.content
					try:
						if command.startswith('<@&') and command.endswith('>'):
							command = int(command.strip()[-19:-1])
						else:
							command = int(command)
					except:
						pass
					if (type(command) == int and len(str(command)) == 18) and ctx.guild.get_role(command) != None:
						settings.update({'muterole' : command})
						Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'settings' : settings}})
						await ctx.send('{} Role has been setted'.format(Emoji.tick))
					else:
						await ctx.send('{} Please specify a valid role'.format(Emoji.cross))
				except:
					raise asyncio.TimeoutError
			elif str(reaction) == '🟥':
				if role.startswith('`'):
					await ctx.send('{} No role has been previusly setted.'.format(Emoji.cross))
				else:
					del settings['muterole']
					Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'settings' : settings}})
					await ctx.send("{} Role has been removed from the bot's settings".format(Emoji.tick))
			elif str(reaction) == '🔇':
				nRole = await create_mute_role(ctx.guild)
				get_mute_role(ctx.guild, nRole)
				await ctx.send('{} New role has been created ({})'.format(Emoji.tick, nRole.mention))
			raise asyncio.TimeoutError
		except asyncio.TimeoutError:
			message = await ctx.channel.fetch_message(msg.id)
			await message.clear_reactions()

	@muterole.error
	async def setup_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Administrator)".format(Emoji.cross))

def setup(client):
	client.add_cog(Setup(client))