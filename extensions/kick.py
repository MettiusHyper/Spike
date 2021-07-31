import discord
from discord.ext import commands
from datetime import datetime

from core import *

class Kick(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description = 'Kicks from the guild the specified member.')
	@commands.guild_only()
	@commands.has_permissions(kick_members = True)
	async def kick(self, ctx, member : discord.Member, *, reason : str = None):
		#check role height, so that mods can't ban admins
		if ctx.author.top_role < member.top_role or ctx.guild.me.top_role < member.top_role or ctx.guild.owner_id == member.id:
			return await ctx.send("{} You can not kick someone with a role higher of yours or the bot's role".format(Emoji.cross))
		#send dm to the kicked member
		try:
			await member.send(embed = discord.Embed(
				color = Vars.empty_color,
				title = '{} | Kick from {}'.format(Emoji.kick, ctx.guild.name),
				description = 'You have been kicked from the `{}` server.\nYou are still able to join back with an invite link.'.format(ctx.guild.name)
			).add_field(name = 'Reason', value = str(reason)[:1024]))
		except:
			await ctx.send("{} Couldn't send a dm to the member, proceeding with the kick".format(Emoji.warning))
		#actual kick
		await ctx.guild.kick(member, reason = str(reason)[:1024])

		#adds the kick for the member in the guild in the database
		data = Vars.collection.find_one({'_id' : ctx.guild.id})['members']
		if str(member.id) in data:
			if 'kicks' in data[str(member.id)]:
				data[str(member.id)]['kicks'] += 1
			else:
				data[str(member.id)].update({'kicks' : 1})
		else:
			data.update({str(member.id) : {'kicks' : 1}})
		Vars.collection.update_one({'_id': ctx.guild.id}, {'$set': {'members' : data}})

		#send log to setted channel
		try:
			await ctx.guild.get_channel(int(Vars.collection.find_one({'_id' : ctx.guild.id})['logs']['kick'])).send(
				embed = discord.Embed(
					color = Vars.empty_color,
					title = '{} | Kick Case'.format(Emoji.kick),
					description = '**Member:** `{}`\n**Staff:** `{}`\n**Reason:** `{}`'.format(member, ctx.author, str(reason)[:1600]),
					timestamp = datetime.now()
				))
		except: pass
		#send confirmation in ctx
		await ctx.send('{0} {1}(`{1.id}`) has been banned from the server.'.format(Emoji.kick, member))

	@kick.error
	async def kick_error(self, ctx, error):
		if isinstance(error, commands.MissingPermissions):
			await ctx.send("{} You don't have the required permissions (Kick Members)".format(Emoji.cross))
		elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
			await ctx.send('{} Please specify a valid member'.format(Emoji.cross))
		elif isinstance(error, commands.CommandInvokeError):
			await ctx.send('{} {} does not have the permissions to kick members.'.format(Emoji.cross, self.client.user.name))

def setup(client):
	client.add_cog(Kick(client))