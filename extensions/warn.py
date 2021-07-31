import discord, datetime, uuid
from discord.ext import commands

from core import *

class Warn(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description = 'Warns the specified member')
	@commands.has_permissions(manage_messages = True)
	@commands.guild_only()
	async def warn(self, ctx, member: discord.Member, *, reason: str = None):

		#role check, so that moderators can't warn administrators
		if ctx.author.top_role < member.top_role:
			return await ctx.send("{cross} You can't warn someone that has an higher role than yours.".format(cross = Emoji.cross))

		#generating id
		warnId = str(uuid.uuid4())[:18]

		#logging in the database
		data = Vars.collection.find_one({'_id' : ctx.guild.id})['members']

		#if the member was warned in the past
		warn_object = {
			'id' : warnId,
			'date' : datetime.datetime.now(),
			'reason' : reason
		}
		if str(member.id) in data:
			db_member = data[str(member.id)]
			db_member['warns'].append(warn_object)
			data.update({str(member.id) : db_member})

		#if the member was never warned
		else:
			data.update({str(member.id) : {'warns' : [warn_object]}})

		#updating the database
		Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'members' : data}})

		#sends a dm to the member
		try:
			await member.send(embed = discord.Embed(
				color = Vars.empty_color,
				title = '{} | Warn from {}'.format(Emoji.warn, ctx.guild.name),
				description = 'You have been warned from the `{}` server.\nThis warning will remain logged until a moderator removes it.'.format(ctx.guild.name)
			).add_field(name = 'Reason', value = str(reason)[:1024])
			.add_field(name = 'Warn Id', value = f'`{warnId}`'))
		except:
			await ctx.send("{} Couldn't send a dm to the member, proceeding with the warn".format(Emoji.warning))

		#sends an embed in the selected logging channel
		try:
			await ctx.guild.get_channel(int(Vars.collection.find_one({'_id' : ctx.guild.id})['logs']['warn'])).send(
				embed = discord.Embed(
					color = Vars.empty_color,
					title = '{} | Warn Case'.format(Emoji.warn),
					description = '**Member:** `{}`\n**Staff:** `{}`\n**Warn Id:** `{}`\n**Reason:** `{}`'.format(member, ctx.author, warnId, str(reason)[:1600]),
					timestamp = datetime.datetime.now()
				))
		except: pass

		#sends a confirmation message in ctx
		await ctx.send('{0} {1}(`{1.id}`) has been warned succesfully.'.format(Emoji.warn, member))
		
	@warn.error
	async def warn_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Manage Messages)".format(Emoji.cross))
		elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
			await ctx.send('{} Please specify a valid user'.format(Emoji.cross))

	@commands.command(description = 'Removes a warn from the specified member')
	@commands.has_permissions(manage_messages = True)
	@commands.guild_only()
	async def unwarn(self, ctx, member: discord.Member, warnId = None):
		#role check, so that moderators can't ban administrators
		if ctx.author.top_role < member.top_role:
			return await ctx.send("{} You can't remove a warn from someone that has an higher role than yours.".format(Emoji.cross))

		data = Vars.collection.find_one({'_id' : ctx.guild.id})['members']

		#role check
		if str(member.id) not in data or 'warns' not in data[str(member.id)] or len(data[str(member.id)]['warns']) == 0:
			return await ctx.send("{cross} This member doesn't have any warns.".format(cross = Emoji.cross))

		#removes the warn from the database
		dm_member = data[str(member.id)]

		#without id takes the last warn that has been done
		if warnId == None:
			removed_warn = dm_member['warns'][-1]
			dm_member['warns'].pop()
			data.update({str(member.id) : dm_member})

		#if an id is specified tries to find it in the database
		else:
			for i, el in enumerate(dm_member['warns']):
				if el['id'] == warnId:
					removed_warn = el
					dm_member['warns'].pop(i)
					data.update({str(member.id) : dm_member})

		#if nothing has changed it means that didn't find the specified id
		if data == Vars.collection.find_one({'_id' : ctx.guild.id})['members']:
			return await ctx.send("{cross} Couldn't find the specified warn id.".format(cross = Emoji.cross))

		#updating database
		Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'members' : data}})

		#sends a dm to the user
		try:
			await member.send(embed = discord.Embed(
				color = Vars.empty_color,
				title = '{} | UnWarn from {}'.format(Emoji.warn, ctx.guild.name),
				description = 'One of your warns from the `{}` server has been removed.'.format(ctx.guild.name)
			).add_field(name = 'Previous Warn Id', value = f'`{removed_warn["id"]}`')
			.add_field(name = 'Previous Warn Reason', value = removed_warn['reason']))
		except:
			await ctx.send("{} Couldn't send a dm to the member, proceeding with the unwarn".format(Emoji.warning))

		#sends an embed in the selected logging channel
		try:
			await ctx.guild.get_channel(int(Vars.collection.find_one({'_id' : ctx.guild.id})['logs']['warn'])).send(
				embed = discord.Embed(
					color = Vars.empty_color,
					title = '{} | Warn Case'.format(Emoji.warn),
					description = '**Member:** `{}`\n**Staff:** `{}`\n**Previous Warn Id:** `{}`'.format(member, ctx.author, removed_warn['id']),
					timestamp = datetime.datetime.now()
				))
		except: pass

		#sends a confirmation message in ctx
		await ctx.send('{0} {1}(`{1.id}`) has been unwarned succesfully.'.format(Emoji.warn, member))
		
	@warn.error
	async def warn_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Manage Messages)".format(Emoji.cross))
		elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
			await ctx.send('{} Please specify a valid user'.format(Emoji.cross))

def setup(client):
	client.add_cog(Warn(client))
