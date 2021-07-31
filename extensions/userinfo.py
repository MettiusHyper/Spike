import discord, datetime
from discord.ext import commands

from core import *

class Userinfo(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command(description = 'Returns lots of useful informations on a discord user')
	async def userinfo(self, ctx, member: discord.User = None):
		if member == None:
			member = ctx.author

		if ctx.guild != None and ctx.guild.get_member(member.id) != None:
			member = ctx.guild.get_member(member.id)

		embed = discord.Embed(title = 'Userinfo', color = Vars.color)
		embed.add_field(name = member, value = f'<@{member.id}> | {member.id}', inline = False)
		embed.set_thumbnail(url = member.avatar_url)
		embed.add_field(name = 'Joined Discord:', value = '{}\n({} days ago)'.format(member.created_at.strftime('%d %B %Y, %H:%M'), (datetime.datetime.utcnow() - member.created_at).days))
		if isinstance(member, discord.Member):
			embed.add_field(name = 'Joined Server:', value = '{}\n({} days ago)'.format(member.joined_at.strftime('%d %B %Y, %H:%M'), (datetime.datetime.utcnow() - member.joined_at).days))
			embed.add_field(name = 'Highest Role', value = member.top_role.mention, inline = False)
		else:
			embed.add_field(name = 'Joined Server:', value = 'This user is not in the server.')
			embed.add_field(name = 'Highest Role', value = 'No role', inline = False)
		if ctx.guild != None and ctx.message.author.guild_permissions.manage_messages == True:
			ban = await is_banned(ctx, member)
			if type(ban) != bool:
				embed.add_field(name = 'Infractions', value = ban, inline = False)
			else:
				data = Vars.collection.find_one({'_id' : ctx.guild.id})['members']
				if str(member.id) not in data:
					warn = mute = kick = 0
				else:
					warn, mute, kick = 0, 0, 0
					if 'warns' in data[str(member.id)]:
						warn = len(data[str(member.id)]['warns'])
					if 'mutes' in data[str(member.id)]:
						mute = (data[str(member.id)]['mutes'])
					if 'kicks' in data[str(member.id)]:
						kick = (data[str(member.id)]['kicks'])
				embed.add_field(name = 'Infractions', value = '**Kicks** | User has got `{}` kicks\n**Mutes** | User has got `{}` mutes\n**Warns** | User has got `{}` warns'.format(kick, mute, warn), inline = False)
		if isinstance(member, discord.Member):
			vc = member.voice
			if vc == None:
				vc = 'Not connected'
		else:
			vc = 'Not connected'
		embed.add_field(name = 'Voice Channel', value = vc)
		if ctx.guild != None and ctx.message.author.guild_permissions.manage_messages == True:
			data = Vars.collection.find_one({'_id' : 'muted'})
			muteTime = None
			for el in data['muted']:
				if el['user'] == member.id and el['guild'] == ctx.guild.id:
					#muteTime = Functions.formatDelta(el['date'] - datetime.datetime.now())
					embed.add_field(name = 'Mute', value = 'muteTime')
			if muteTime == None:
				embed.add_field(name = 'Mute', value = 'No active mute')
		else:
			if ctx.message.author.bot == True:
				embed.add_field(name = 'Is Bot?', value='Yes')
			else:
				embed.add_field(name = 'Is Bot?', value='No')
		await ctx.send(embed = embed)

def setup(client):
	client.add_cog(Userinfo(client))