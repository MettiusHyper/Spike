import discord

from discord.ext import commands
from Global import collection, Commands, Emoji, Functions

class Ban(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = Commands.Ban["name"], description = Commands.Ban["description"], aliases = Commands.Ban["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.has_permissions(ban_members = True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.User, *, reason: str = None): 

        if ctx.guild.get_member(member.id) != None:
            member = ctx.guild.get_member(member.id)

            #check if the member is owner
            if ctx.guild.owner == member:
                return await ctx.send("{cross} You can't ban the server owner".format(cross = Emoji.cross))

            #role check, so that moderators can't ban administrators
            if (ctx.author.top_role < member.top_role and ctx.guild.me.top_role < member.top_role):
                return await ctx.send("{cross} You can't ban someone that has an higher role than you or the bot".format(cross = Emoji.cross))

        #sending a message in the dms
        try:
            await member.send(
                embed = Functions.dmEmbed(
                    ctx, "{ban} | Ban from {server}".format(ban = Emoji.ban, server = ctx.guild.name),
                    "You've been banned from the `{server}` server permanently (a very long time).\nIn order to hop back in the server you will have to be unbanned from it.".format(server = ctx.guild.name), reason
                )
            )
        except:
            await ctx.send("{warning} I couldn't send a dm to the user, proceeding with the ban".format(warning = Emoji.warning))

        #ban
        await ctx.guild.ban(member, reason = str(reason)[:1024], delete_message_days = 0)

        #resets the database for the current guild
        data = collection.find_one({"_id" : ctx.guild.id})["members"]
        if str(member.id) in data:
            del data[str(member.id)]
            collection.update_one({"_id": ctx.guild.id}, {"$set": {"members" : data}})

        #sends log message
        try:
            await ctx.guild.get_channel(int(collection.find_one({"_id" : ctx.guild.id})["logs"]["ban"])).send(
                embed = Functions.logEmbed(
                    ctx, "{ban} | Ban Case".format(ban = Emoji.ban), ctx.author, member, reason
                )
            )
        except:
            pass

        #sends a confirmation message in ctx
        await ctx.send("{ban} {member}(`{memberId}`) has been banned from the server.".format(ban = Emoji.ban, member = member, memberId = member.id))

    @commands.command(name = Commands.UnBan["name"], description = Commands.UnBan["description"], aliases = Commands.Ban["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.has_permissions(ban_members = True)
    @commands.guild_only()
    async def unban(self, ctx, member: discord.User, *, reason: str = None):

        if await Functions.isUserBanned(ctx, member):

            await ctx.guild.unban(member, reason = str(reason)[:1024])

            #sends log message
            try:
                await ctx.guild.get_channel(int(collection.find_one({"_id" : ctx.guild.id})["logs"]["ban"])).send(
                    embed = Functions.logEmbed(
                        ctx, "{unban} | UnBan Case".format(unban = Emoji.ban), ctx.author, member, reason
                    )
                )
            except:
                pass

            # ctx message
            return await ctx.send("{unban} {member}(`{memberId}`) has been unbanned from the server.".format(unban = Emoji.unban, member = member, memberId = member.id))

        await ctx.send("{cross} This user is not banned in this server.".format(cross = Emoji.cross))

def setup(client):
    client.add_cog(Ban(client))
