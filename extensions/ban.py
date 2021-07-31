import discord
from discord.ext import commands
from datetime import datetime

from core import *

class Ban(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description = "Bans a member from the server. If setted, a link for appealing the ban gets sent in the user's dms")
	@commands.guild_only()
	@commands.has_permissions(ban_members = True)
	async def ban(self, ctx, user : discord.User, *, reason : str = None):
		try:
			user = await ctx.guild.fetch_member(user.id)
		except: pass
		#check role height, so that mods can't ban admins
		if isinstance(user, discord.Member) and (ctx.author.top_role < user.top_role or ctx.guild.me.top_role < user.top_role or ctx.guild.owner_id == user.id):
			return await ctx.send("{} You can not ban someone with a role higher of yours or the bot's role".format(Emoji.cross))
		#get banappeal link from database, if any was set
		try:
			banappeal = ':link: [**Appeal the ban with this link**]({})'.format(Vars.collection.find_one({'_id' : ctx.guild.id})['settings']['banappeal'])
		except:
			banappeal = ''
		#send dm to the banned user
		try:
			await user.send(embed = discord.Embed(
				color = Vars.empty_color,
				title = '{} | Ban from {}'.format(Emoji.ban, ctx.guild.name),
				description = 'You have been banned from the `{}` server.\nYou will be able to join back only if unbanned.\n{}'.format(ctx.guild.name, banappeal)
			).add_field(name = 'Reason', value = str(reason)[:1024]))
		except:
			await ctx.send("{} Couldn't send a dm to the user, proceeding with the ban".format(Emoji.warning))
		#actual ban
		await ctx.guild.ban(user, reason = str(reason)[:1024])

		#resets the database for the user in the current guild
		data = Vars.collection.find_one({'_id' : ctx.guild.id})['members']
		if str(user.id) in data:
			del data[str(user.id)]
			Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'members' : data}})

		#send log to setted channel
		try:
			await ctx.guild.get_channel(int(Vars.collection.find_one({'_id' : ctx.guild.id})['logs']['ban'])).send(
				embed = discord.Embed(
					color = Vars.empty_color,
					title = '{} | Ban Case'.format(Emoji.ban),
					description = '**Member:** `{}`\n**Staff:** `{}`\n**Reason:** `{}`'.format(user, ctx.author, str(reason)[:1600]),
					timestamp = datetime.now()
				))
		except: pass
		#send confirmation in ctx
		await ctx.send('{0} {1}(`{1.id}`) has been banned from the server.'.format(Emoji.ban, user))

	@ban.error
	async def ban_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Ban Members)".format(Emoji.cross))
		elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
			await ctx.send('{} Please specify a valid user'.format(Emoji.cross))
		elif isinstance(error, commands.CommandInvokeError):
			await ctx.send('{} {} does not have the permissions to ban members.'.format(Emoji.cross, self.client.user.name))

	@commands.command(description = 'Unbans the specified member')
	@commands.guild_only()
	@commands.has_permissions(ban_members = True)
	async def unban(self, ctx, user : discord.User, *, reason : str = None):
		
		if type(await is_banned(ctx, user)) == bool:
			return await ctx.send('{} This user is not yet banned.'.format(Emoji.cross))

		#actual ban
		await ctx.guild.unban(user, reason = str(reason)[:1024])

		#send log to setted channel
		try:
			await ctx.guild.get_channel(int(Vars.collection.find_one({'_id' : ctx.guild.id})['logs']['ban'])).send(
				embed = discord.Embed(
					color = Vars.empty_color,
					title = '{} | UnBan Case'.format(Emoji.unban),
					description = '**Member:** `{}`\n**Staff:** `{}`\n**Reason:** `{}`'.format(user, ctx.author, str(reason)[:1600]),
					timestamp = datetime.now()
				))
		except: pass
		#send confirmation in ctx
		await ctx.send('{0} {1}(`{1.id}`) has been unbanned from the server.'.format(Emoji.unban, user))

	@unban.error
	async def unban_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Ban Members)".format(Emoji.cross))
		elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.CommandInvokeError):
			await ctx.send('{} Please specify a valid user'.format(Emoji.cross))

def setup(client):
	client.add_cog(Ban(client))