import discord, datetime, humanfriendly
from discord.ext import commands, tasks
from pytimeparse.timeparse import timeparse

from core import *

class Mute(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		self.mutes.start()

	@tasks.loop(hours = 1)
	async def mutes(self):
		muted = Vars.collection.find_one({'_id' : 'muted'})['muted']
		for i, el in enumerate(muted):
			guild = self.client.get_guild(el['guild'])
			if guild == None:
				del muted[i]
			else:
				member = await guild.fetch_member(el['user'])
				if member != None and datetime.datetime.now() > el['date']:
					#unmute
					del muted[i]
					mute_role = get_mute_role(guild)
					await member.remove_roles(mute_role)
					#dm message
					try:
						embed = discord.Embed(
							color = Vars.empty_color,
							title = '{} | UnMute from {}'.format(Emoji.mute, guild.name),
							description = 'You have been unmuted from the `{}` server.\nYou are now able to type in any channel and join voice channels.'.format(guild.name)
						).add_field(name = 'Reason', value = 'Time is up')
						await member.send(embed = embed)
					except: pass
					#log message
					try:
						await guild.get_channel(int(Vars.collection.find_one({'_id' : guild.id})['logs']['mute'])).send(
							embed = discord.Embed(
								color = Vars.empty_color,
								title = '{} | UnMute Case'.format(Emoji.mute),
								description = '**Member:** `{}`\n**Staff:** `{}`\n**Reason:** `{}`'.format(member, self.client.user, 'Time is up'),
								timestamp = datetime.datetime.now()
							))
					except: pass
		Vars.collection.update_one({'_id' : 'muted'}, {'$set': {'muted' : muted}})


	@commands.command(description = 'Mutes the specified member for the specified amount of time')
	@commands.guild_only()
	@commands.has_guild_permissions(mute_members = True)
	async def mute(self, ctx, member : discord.Member, *, reason : str = None):
		#check role height, so that mods can't ban admins
		if ctx.author.top_role < member.top_role or ctx.guild.me.top_role < member.top_role or ctx.guild.owner_id == member.id:
			return await ctx.send("{} You can not mute someone with a role higher of yours or the bot's role".format(Emoji.cross))
		#check if user is already muted
		muted = Vars.collection.find_one({'_id' : 'muted'})['muted']
		for el in muted:
			if member.id == el['user']:
				return await ctx.send('{} This member is already muted!')
		#get muted role / create it
		mute_role = get_mute_role(ctx.guild)
		if mute_role == None:
			mute_role = await create_mute_role(ctx.guild)
		#get duration in seconds
		await ctx.send('Type the duration of the mute (valid formats are: 1h30m/1:30:0)')
		def check(m):
			return m.author == ctx.author
		msg = await self.client.wait_for('message', check=check)
		try:
			mute_time = datetime.timedelta(seconds = timeparse(msg.content))
		except:
			return await ctx.send('{} Please specify a valid duration (formats can be: 1h30m/1:30:0)'.format(Emoji.cross))
		#add role to member
		await member.add_roles(mute_role)
		#add time to database
		muted = Vars.collection.find_one({'_id' : 'muted'})['muted']
		muted.append({
			'user' : member.id,
			'guild' : ctx.guild.id,
			'date' : datetime.datetime.now() + mute_time
		})
		Vars.collection.update_one({'_id' : 'muted'}, {'$set': {'muted' : muted}})
		#dm message
		try:
			embed = discord.Embed(
				color = Vars.empty_color,
				title = '{} | Mute from {}'.format(Emoji.mute, ctx.guild.name),
				description = 'You have been muted from the `{}` server.\nYou will not be able to type in any channel or join voice channels.'.format(ctx.guild.name)
			).add_field(name = 'Reason', value = str(reason)[:1024])
			embed.add_field(name = 'Duration', value = humanfriendly.format_timespan(mute_time))
			await member.send(embed = embed)
		except:
			await ctx.send("{} Couldn't send a dm to the member, proceeding with the mute".format(Emoji.warning))
		#log message
		try:
			await ctx.guild.get_channel(int(Vars.collection.find_one({'_id' : ctx.guild.id})['logs']['mute'])).send(
				embed = discord.Embed(
					color = Vars.empty_color,
					title = '{} | Mute Case'.format(Emoji.mute),
					description = '**Member:** `{}`\n**Staff:** `{}`\n**Reason:** `{}`\n**Duration:** `{}`'.format(member, ctx.author, str(reason)[:1600], humanfriendly.format_timespan(mute_time)),
					timestamp = datetime.datetime.now()
				))
		except: pass
		#ctx confirmation
		await ctx.send('{0} {1}(`{1.id}`) has been muted from the server.'.format(Emoji.mute, member))

	@mute.error
	async def mute_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Mute Members)".format(Emoji.cross))
		elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
			await ctx.send('{} Please specify a valid member'.format(Emoji.cross))
		elif isinstance(error, commands.CommandInvokeError):
			await ctx.send('{} {} does not have the permissions to perform this action.'.format(Emoji.cross, self.client.user.name))

	@commands.command(description = 'UnMutes the member in the server')
	@commands.guild_only()
	@commands.has_guild_permissions(mute_members = True)
	async def unmute(self, ctx, member : discord.Member, *, reason : str = None):
		#check role height, so that mods can't ban admins
		if ctx.author.top_role < member.top_role or ctx.guild.me.top_role < member.top_role or ctx.guild.owner_id == member.id:
			return await ctx.send("{} You can not unmute someone with a role higher of yours or the bot's role".format(Emoji.cross))
		#check if user is already muted
		muted = Vars.collection.find_one({'_id' : 'muted'})['muted']
		for i, el in enumerate(muted):
			if member.id == el['user']:
				if guild.id != el['guild']:
					return await ctx.send('{} This Member is not currently muted'.format(Emoji.cross))
				#get muted role
				mute_role = get_mute_role(ctx.guild)
				#remove role
				if mute_role == None:
					await ctx.send("{} Could't find the muterole, proceeding with the unmute".format(Emoji.warning))
				else:
					await member.remove_roles(mute_role)
				#unmute from database
				del muted[i]
				Vars.collection.update_one({'_id' : 'muted'}, {'$set': {'muted' : muted}})
				#dm message
				try:
					embed = discord.Embed(
						color = Vars.empty_color,
						title = '{} | UnMute from {}'.format(Emoji.mute, ctx.guild.name),
						description = 'You have been unmuted from the `{}` server.\nYou are now able to type in any channel and join voice channels.'.format(ctx.guild.name)
					).add_field(name = 'Reason', value = str(reason)[:1024])
					await member.send(embed = embed)
				except:
					await ctx.send("{} Couldn't send a dm to the member, proceeding with the unmute".format(Emoji.warning))
				#log message
				try:
					await ctx.guild.get_channel(int(Vars.collection.find_one({'_id' : ctx.guild.id})['logs']['mute'])).send(
						embed = discord.Embed(
							color = Vars.empty_color,
							title = '{} | UnMute Case'.format(Emoji.mute),
							description = '**Member:** `{}`\n**Staff:** `{}`\n**Reason:** `{}`'.format(member, ctx.author, str(reason)[:1600]),
							timestamp = datetime.datetime.now()
						))
				except: pass
				#ctx confirmation
				return await ctx.send('{0} {1}(`{1.id}`) has been unmuted from the server.'.format(Emoji.mute, member))
		await ctx.send('{} This Member is not currently muted'.format(Emoji.cross))

	@unmute.error
	async def unmute_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Mute Members)".format(Emoji.cross))
		elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
			await ctx.send('{} Please specify a valid member'.format(Emoji.cross))
		elif isinstance(error, commands.CommandInvokeError):
			await ctx.send('{} {} does not have the permissions to perform this action.'.format(Emoji.cross, self.client.user.name))

def setup(client):
	client.add_cog(Mute(client))