import discord

from discord.ext import commands
from Global import collection, Commands, Emoji, Functions

class Kick(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = Commands.Kick["name"], description = Commands.Kick["description"], aliases = Commands.Kick["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.has_permissions(kick_members = True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason: str = None): 

        #check if the member is owner
        if ctx.guild.owner == member:
            return await ctx.send("{cross} You can't kick the server owner".format(cross = Emoji.cross))

        #role check, so that moderators can't kick administrators
        if (ctx.author.top_role < member.top_role and ctx.guild.me.top_role < member.top_role):
            return await ctx.send("{cross} You can't kick someone that has an higher role than you or the bot".format(cross = Emoji.cross))

        #sending a message in the dms
        try:
            await member.send(
                embed = Functions.dmEmbed(
                    ctx, "{emoji} | Kick from {server}".format(emoji = Emoji.kick, server = ctx.guild.name),
                    "You've been kicked from the `{server}` server.\nThis means that you can still join back the server.".format(server = ctx.guild.name), reason
                )
            )
        except:
            await ctx.send("{warning} I couldn't send a dm to the user, proceeding with the kick".format(warning = Emoji.warning))

        #kick
        await ctx.guild.kick(member, reason = str(reason)[:1024])

        #adds a kick in the database
        data = collection.find_one({"_id" : ctx.guild.id})["members"]
        if str(member.id) in data:
            dbMember = data[str(member.id)]
            if "kicks" in dbMember:
                data[str(member.id)].update({"kicks" : (dbMember["kicks"] + 1)})
            else:
                data[str(member.id)].update({"kicks" : 1})
        collection.update_one({"_id": ctx.guild.id}, {"$set": {"members" : data}})

        #sends log message
        try:
            await ctx.guild.get_channel(int(collection.find_one({"_id" : ctx.guild.id})["logs"]["kick"])).send(
                embed = Functions.logEmbed(
                    ctx, "{emoji} | Kick Case".format(emoji = Emoji.kick), ctx.author, member, reason
                )
            )
        except:
            pass

        #sends a confirmation message in ctx
        await ctx.send("{emoji} {member}(`{memberId}`) has been kicked from the server.".format(emoji = Emoji.kick, member = member, memberId = member.id))

def setup(client):
    client.add_cog(Kick(client))
