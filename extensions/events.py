import discord, traceback, datetime
from discord.ext import commands, tasks
from asyncio import sleep

from core import *

class Events(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		self.status.start()
		print(f'{self.client.user.name} is up and running')
		now = datetime.datetime.now()
		if now.hour < 12:
			await sleep((datetime.datetime(now.year, now.month, now.day, 12, 0, 0, 0) - now).seconds)
		else:
			await sleep(((datetime.datetime(now.year, now.month, now.day, 12, 0, 0, 0) + datetime.timedelta(days = 1)) - now).seconds)
		await update_users_count(self.client)

	@commands.Cog.listener()
	async def on_command_error(self, ctx, exception):

		# This prevents any commands with local handlers being handled here in on_command_error.
		if hasattr(ctx.command, 'on_error'):
			return
		if isinstance(exception, commands.CommandNotFound):
			return

		#if this part of code gets executed it means that an unhandled, unexpected error has occurred
		#The full error gets logged to console, and a warning gets sent to a private, dev only channel
		await self.client.get_channel(748894459118354532).send(f'{Emoji.warning} Check console for errors') 

		if ctx.guild != None:
			print(exception, ctx.message.content, f'author: {ctx.author.id}', f'guild: {ctx.guild.id}') 
		for el in traceback.format_exception(type(exception), exception, exception.__traceback__):
			print(el.strip())

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.content.lower().strip() in (f'<@!{self.client.user.id}>', f'<@{self.client.user.id}>'):
			if message.guild == None:
				return await message.author.send(embed = help_embed(self.client, message.guild))
			await message.channel.send(embed = help_embed(self.client, message.guild))

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		#loads the default configuration in the database
		Vars.collection.insert_one({'_id' : guild.id, 'prefix' : 's!', 'users' : [], 'logs' : {}, 'members' : {}, 'settings' : {}})

		#logs the event to a dev only channel
		await self.client.get_channel(748894459118354532).send(f"{self.client.user.name} was added to a new server\n{self.client.user.name}'s now in {len(self.client.guilds)} server")

		#tries to send a message in the dms of the one who added the bot
		def check(event):
			return event.target.id == self.client.user.id
		if guild.me.guild_permissions.administrator:
			bot_entry = await guild.audit_logs(action=discord.AuditLogAction.bot_add).find(check)
			await bot_entry.user.send(content = 'Thanks for inviting me!', embed = help_embed(self.client, guild))

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		#logging to dev only channel
		await self.client.get_channel(748894459118354532).send(f"{self.client.user.name} has been removed from a server\n{self.client.user.name}'s now in {len(self.client.guilds)} servers")
		try:
			collection.delete_one({'_id' : guild.id})
		except: pass

	@tasks.loop(hours = 1)
	async def status(self):
		await update_status(self.client)

def setup(client):
	client.add_cog(Events(client))