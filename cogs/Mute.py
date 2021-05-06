import datetime
import discord

from discord.ext import commands
from Global import collection, Commands, Emoji, Functions

class Mute(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = Commands.Mute["name"], description = Commands.Mute["description"], aliases = Commands.Mute["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.has_guild_permissions(mute_members = True)
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member, duration : str, *, reason: str = None):
        duration = Functions.convertToTimedelta(duration)

        #role check, so that moderators can't mute administrators
        if (ctx.author.top_role < member.top_role and ctx.guild.me.top_role < member.top_role):
            return await ctx.send("{cross} You can't mute someone that has an higher role than you or the bot".format(cross = Emoji.cross))

        settings = collection.find_one({"_id" : ctx.guild.id})["settings"]
        if "muterole" in settings and ctx.guild.get_role(settings["muterole"]) != None:
            role = ctx.guild.get_role(settings["muterole"])
        else:
            role = await Functions.createMuteRole(self, ctx)

        if role > ctx.guild.me.top_role:
            return await ctx.send("{cross} The setted muterole is higher than the bot's highest role".format(cross = Emoji.cross))

        if role in member.roles:
            return await ctx.send("{cross} The member already has the muterole".format(cross = Emoji.cross))

        #sending a message in the dms
        try:
            await member.send(
                embed = Functions.dmEmbed(
                    ctx.guild, "{emoji} | Mute from {server}".format(emoji = Emoji.mute, server = ctx.guild.name),
                    "You've been muted from the `{server}` server for {time}.\nFor this duration of time you won't be able to write or join voice channels in the server".format(server = ctx.guild.name, time = Functions.formatDelta(duration)), reason
                )
            )
        except:
            await ctx.send("{warning} I couldn't send a dm to the user, proceeding with the mute".format(warning = Emoji.warning))

        #adding the role
        await member.add_roles(role)

        #resets the database for the current guild
        data = collection.find_one({"_id" : ctx.guild.id})["members"]
        if str(member.id) in data:
            dbMember = data[str(member.id)]
            if "mutes" in dbMember:
                data[str(member.id)].update({"mutes" : (dbMember["mutes"] + 1)})
            else:
                data[str(member.id)].update({"mutes" : 1})
        else:
            data.update({str(member.id) : {"mutes" : 1}})
        collection.update_one({"_id": ctx.guild.id}, {"$set": {"members" : data}})

        #adds to muted
        data = collection.find_one({"_id" : "muted"})["muted"]
        data.append({
            "user" : member.id,
            "guild" : ctx.guild.id,
            "date" : datetime.datetime.now() + duration
        })
        collection.update_one({"_id" : "muted"}, {"$set": {"muted" : data}})

        #sends log message
        try:
            await ctx.guild.get_channel(int(collection.find_one({"_id" : ctx.guild.id})["logs"]["mute"])).send(
                embed = Functions.logEmbed(
                    ctx.guild, "{emoji} | Mute Case".format(emoji = Emoji.mute), ctx.author, member, reason, Functions.formatDelta(duration)
                )
            )
        except:
            pass

        #sends a confirmation message in ctx
        await ctx.send("{emoji} {member}(`{memberId}`) has been muted from the server for {time}.".format(emoji = Emoji.mute, member = member, memberId = member.id, time = Functions.formatDelta(duration)))

    @commands.command(name = Commands.UnMute["name"], description = Commands.UnMute["description"], aliases = Commands.UnMute["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.has_guild_permissions(mute_members = True)
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):

        settings = collection.find_one({"_id" : ctx.guild.id})["settings"]
        if "muterole" in settings and ctx.guild.get_role(settings["muterole"]) != None:
            role = ctx.guild.get_role(settings["muterole"])

            if role in member.roles:

                await member.remove_roles(role)

                #adds to muted
                data = collection.find_one({"_id" : "muted"})["muted"]
                for el in data:
                    if el["user"] == member.id:
                        data.remove(el)
                if data != collection.find_one({"_id" : "muted"})["muted"]:
                    collection.update_one({"_id" : "muted"}, {"$set": {"muted" : data}})
                else:
                    return await ctx.send("{cross} This user is not currently muted.".format(cross = Emoji.cross))

                #sending a message in the dms
                try:
                    await member.send(
                        embed = Functions.dmEmbed(
                            ctx.guild, "{emoji} | UnMute from {server}".format(emoji = Emoji.mute, server = ctx.guild.name),
                            "You've been unmuted from the `{server}` server.\nNow you can write and join voice channels in the guild".format(server = ctx.guild.name), reason
                        )
                    )
                except:
                    await ctx.send("{warning} I couldn't send a dm to the user, proceeding with the unmute".format(warning = Emoji.warning))

                #sends log message
                try:
                    await ctx.guild.get_channel(int(collection.find_one({"_id" : ctx.guild.id})["logs"]["mute"])).send(
                        embed = Functions.logEmbed(
                            ctx.guild, "{emoji} | UnMute Case".format(emoji = Emoji.mute), ctx.author, member, reason
                        )
                    )
                except:
                    pass

                # ctx message
                return await ctx.send("{emoji} {member}(`{memberId}`) has been unmuted from the server.".format(emoji = Emoji.mute, member = member, memberId = member.id))

        await ctx.send("{cross} This user is not currently muted.".format(cross = Emoji.cross))

def setup(client):
    client.add_cog(Mute(client))
