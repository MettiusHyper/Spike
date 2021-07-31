import os, pymongo, discord

class Emoji:
	tick = '<a:tick:763083389217144852>'
	cross = '<a:cross:868826888892735528>'
	warning = ':warning:'
	ban = ':hammer:'
	unban = ':dove:'
	kick = ':boot:'
	mute = ':mute:'
	warn = ':radioactive:'

class Vars:
	collection = pymongo.MongoClient(os.environ['MONGO'])['Spike']['SpikeDatabase']
	default_prefix = 's!'
	version = '1.1.0'
	color = 0x89defe
	empty_color = 0x2f3136
	invite_link = 'dsc.gg/spike'
	support_server = 'https://cutt.ly/netbot-discord'

def custom_prefix(client, message_or_guild):
	if isinstance(message_or_guild, discord.Message):
		guild = message_or_guild.guild
	else:
		guild = message_or_guild
	if guild != None:
		prefix = Vars.collection.find_one({'_id' : guild.id})['prefix']
		return (prefix + ' ', prefix)
	else:
		return (Vars.default_prefix + ' ', Vars.default_prefix)

def is_developer(user):
	return user in Vars.collection.find_one({'_id' : 'developer'})['developers']

async def is_banned(ctx, user):
	banned_users = await ctx.guild.bans()
	for ban_entry in banned_users:
		if ban_entry.user.id == user.id:
			return ban_entry.reason
	return False

def help_embed(client, guild):
	embed = discord.Embed(
		description = 'Spike is a simple moderation bot, with tons of\nuseful features to moderate a discord server.',
		color = Vars.color
	)
	embed.set_author(name = client.user.name, url = f'https://{Vars.invite_link}', icon_url = client.user.avatar_url)
	embed.add_field(name = 'Commands', value = 'For a full list of commands use `{}commands`'.format(custom_prefix(client, guild)[1]), inline = False)
	if guild != None:
		embed.add_field(name = 'Prefix', value = 'In this guild use the prefix `{}`'.format(custom_prefix(client, guild)[1]), inline = False)
	else:
		embed.add_field(name = 'Prefix', value = 'In dms the prefix is `{}`'.format(Vars.default_prefix), inline = False)
	embed.add_field(name = 'Support', value = '[Click here]({}) to join our support server'.format(Vars.support_server), inline = False)
	embed.set_footer(text = 'Type {}help [command] for more help'.format(custom_prefix(client, guild)[1]))
	return embed

async def update_users_count(client):
	while True:
		for guild in client.guilds:
			users = Vars.collection.find_one({'_id' : guild.id})['users']
			if users != False:
				users.append(len(guild.members))
				if len(users) > 9:
					del users[0]
			Vars.collection.update_one({'_id': guild.id}, {'$set': {'users' : users}})
		print('Users lists have been update successfully')
		await sleep(86400)#1 day

async def update_status(client):
	activity = {'listening' : discord.ActivityType.listening, 'watching' : discord.ActivityType.watching}
	status = {'online' : discord.Status.online, 'dnd' : discord.Status.dnd, 'idle' : discord.Status.idle}
	data = Vars.collection.find_one({'_id' : 'developer'})
	if data['type'] == 'playing':
		CustomActivity = discord.Game(name = data['name'])
	else:
		CustomActivity = discord.Activity(type = activity[data['type']], name = data['name'])
	await client.change_presence(status = status[data['status']], activity = CustomActivity)

def get_mute_role(guild, new_mute_role = None):
	settings = Vars.collection.find_one({'_id' : guild.id})['settings']
	if new_mute_role != None:
		settings.update({'muterole' : new_mute_role.id})
		Vars.collection.update_one({'_id' : guild.id}, {'$set': {'settings' : settings}})
		return new_mute_role
	if 'muterole' not in settings:
		return None
	return guild.get_role(Vars.collection.find_one({'_id' : guild.id})['settings']['muterole'])

async def create_mute_role(guild):
	mute_role = await guild.create_role(name = "muted", colour = discord.Colour(0x010101), reason = f"Role for Spike.")
	for channel in guild.channels:
		try:
			await channel.set_permissions(mute_role, send_messages = False, add_reactions = False, connect = False)
		except:
			pass
	await guild.edit_role_positions({mute_role : guild.me.top_role.position - 1})
	return get_mute_role(guild, mute_role)