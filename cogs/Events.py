import discord
import datetime
import traceback

from asyncio import sleep
from discord.ext import commands
from Global import Emoji, logger, collection, Data, Functions

async def errorFormat(client, exception):
    #logging in private, dev only, channel
    await client.get_channel(748894459118354532).send(f"{Emoji.cross} Check console for errors")

    logger.error(exception) 
    for el in traceback.format_exception(type(exception), exception, exception.__traceback__):
        print(el.strip())

def updateLists(self):
    for el in collection.find({}):
        guild = self.client.get_guild(el["id"])
        if guild != None:
            users = el["users"]
            if users != False:
                del users[0]
                users.append(len(guild.members))
                collection.update_one({"_id": el["id"]}, {"$set": {"users" : users}})
    logger.info("users lists have been update successfully")

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.datetime.now()
        if now.hour < 12:
            await sleep((datetime.datetime(now.year, now.month, now.day, 12) - now).seconds)
        else:
            await sleep(((datetime.datetime(now.year, now.month, now.day, 12) + datetime.timedelta(days=1)) - now).seconds)
        updateLists(self)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.MemberNotFound):
            return await ctx.send("{cross} I couldn't find this member".format(cross = Emoji.cross))

        elif isinstance(exception, commands.CommandNotFound):
            return

        elif isinstance(exception, commands.UserNotFound):
            return await ctx.send("{cross} I couldn't find this user".format(cross = Emoji.cross))

        elif isinstance(exception, commands.MissingRequiredArgument):
            if ctx.command == self.client.get_command("ban") or ctx.command == self.client.get_command("unban") or ctx.command == self.client.get_command("kick"):
                return await ctx.send("{cross} Please specify a valid member".format(cross = Emoji.cross))
            elif ctx.command == self.client.get_command("status"):
                return await ctx.send("{cross} Specify the arguments for the status command `%status [online, dnd, idle] [playing, listening, watching] [name]`".format(cross = Emoji.cross))

        elif isinstance(exception, commands.MissingPermissions):
            if ctx.command == self.client.get_command("ban") or ctx.command == self.client.get_command("unban"):
                return await ctx.send("{cross} You don't have the required permissions (Ban Members)".format(cross = Emoji.cross))

        elif isinstance(exception, commands.DisabledCommand):
            return await ctx.send("{cross} This command is currently disabled, try again later".format(cross = Emoji.cross))
        await errorFormat(self.client, exception)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower().strip() in (f"<@!{self.client.user.id}>", f"<@{self.client.user.id}>"):
            if message.guild == None:
                return await message.author.send("{cross} Use this command in a server, in dms the prefix is `{prefix}` (only some commands can be used here)".format(cross = Emoji.cross, prefix = Data.prefix))
            await message.channel.send(embed = Functions.prefixEmbed(self, message))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        collection.insert_one({
            "_id" : guild.id,
            "prefix" : "s!",
            "users" : [],
            "logs" : {},
            "members" : {}
        })
        await self.client.get_channel(748894459118354532).send(f":partying_face: **{self.client.user.name} has been added to a new server! ({guild.name})**\n{self.client.user.name}'s now in {len(self.client.guilds)} servers")

        def check(event):
            return event.target.id == self.client.user.id
        bot_entry = await guild.audit_logs(action=discord.AuditLogAction.bot_add).find(check)
        embed = discord.Embed(colour = Data.default_color, description = f"You have just added me into {guild} server, in this message I will give you some informations to get started.")
        embed.set_author(name = "Thanks for inviting me!", icon_url = self.client.user.avatar_url)
        embed.add_field(name = "Commands :gear:", value = f"Those are just the commands to setup {self.client.user.mention} use {Data.prefix}help for a detailed list and description\n**{Data.prefix}setup** | `Will enable you to setup logs channels and other features.`\n**{Data.prefix}prefix** | `Use this command to change the prefix of {self.client.user.name}`", inline = False)
        embed.add_field(name = f"Links {Emoji.link}", value = f"""If you want to invite me in another server [this is the link to do so]({Data.invite_link}).\n\u200C\nIf you want to report a bug in the bot, a writing error or if you just want to talk to the developers you can just send a message here, in the bot's dms.""", inline = False)
        embed.set_footer(text = f"The {self.client.user.name} Developer team")
        await bot_entry.user.send(embed = embed)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.client.get_channel(748894459118354532).send(f"<a:sad_blob:762295363868426240> **{self.client.user.name} has been removed from a server! ({guild.name})**\n{self.client.user.name}'s now in {len(self.client.guilds)} servers")
        data = collection.find_one({"_id" : guild.id})
        if data != None:
            collection.delete_one({"_id" : guild.id})

def setup(client):
    client.add_cog(Events(client))
