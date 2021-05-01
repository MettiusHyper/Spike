import discord
import traceback

from discord.ext import commands
from Global import Emoji, logger, collection, Data, Functions

async def errorFormat(client, exception):
    #logging in private, dev only, channel
    await client.get_channel(748894459118354532).send(f"{Emoji.cross} Check console for errors")
    
    logger.error(exception) 
    for el in traceback.format_exception(type(exception), exception, exception.__traceback__):
        print(el.strip())

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.MemberNotFound):
            return await ctx.send("{cross} I couldn't find this member".format(cross = Emoji.cross))

        elif isinstance(exception, commands.UserNotFound):
            return await ctx.send("{cross} I couldn't find this user".format(cross = Emoji.cross))

        elif isinstance(exception, commands.MissingRequiredArgument):
            if ctx.command == self.client.get_command("ban") or ctx.command == self.client.get_command("unban"):
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

def setup(client):
    client.add_cog(Events(client))
