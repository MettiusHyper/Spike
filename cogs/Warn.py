import uuid
import discord
import datetime

from discord.ext import commands
from Global import collection, Commands, Emoji, Functions

class Warn(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = Commands.Warn["name"], description = Commands.Warn["description"], aliases = Commands.Warn["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.has_permissions(manage_messages = True)
    @commands.guild_only()
    async def warn(self, ctx, member: discord.Member, *, reason: str = None):

        #role check, so that moderators can't warn administrators
        if ctx.author.top_role < member.top_role:
            return await ctx.send("{cross} You can't warn someone that has an higher role than yours.".format(cross = Emoji.cross))
        
        #generating id
        warnId = str(uuid.uuid4())[:18]

        #logging in the database
        data = collection.find_one({"_id" : ctx.guild.id})["members"]

        #if the user was warned in the past
        if str(member.id) in data:
            dbMember = data[str(member.id)]
            dbMember["warns"].append({
                "id" : warnId,
                "date" : datetime.datetime.now(),
                "reason" : reason
            })
            data.update({str(member.id) : dbMember})

        #if the user was never warned
        else:
            data.update({
                str(member.id) : {
                    "warns" : [
                        {
                            "id" : warnId,
                            "date" : datetime.datetime.now(),
                            "reason" : reason
                        }
                    ]
                }
            })
        
        #updating the database
        collection.update_one({"_id": ctx.guild.id}, {"$set": {"members" : data}})

        #sends a dm to the user
        try:
            await member.send(
                embed = Functions.dmEmbed(
                    ctx, "{warn} | Warn from {server}".format(warn = Emoji.warn, server = ctx.guild.name),
                    "You've been warned from the `{server}` server, this waring will remain logged until a moderator removes it.\n**Warn id:** {warnId} (This id identifies the warn, could be useful to moderators).".format(server = ctx.guild.name, warnId = warnId), reason
                )
            )
        except:
            await ctx.send("{warning} I couldn't send a dm to the user, proceeding with the warn".format(warning = Emoji.warning))

        #sends an embed in the selected logging channel
        try:
            await ctx.guild.get_channel(int(collection.find_one({"_id" : ctx.guild.id})["logs"]["warn"])).send(
                embed = Functions.logEmbed(
                    ctx, "{warn} | Warn Case".format(warn = Emoji.warn), ctx.author, member, reason, warnId
                )
            )
        except:
            pass
        
        #sends a confirmation message in ctx
        await ctx.send("{warn} {member}(`{memberId}`) has been warned succesfully.".format(warn = Emoji.warn, member = member, memberId = member.id))
        
    @commands.command(name = Commands.UnWarn["name"], description = Commands.UnWarn["description"], aliases = Commands.UnWarn["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.has_permissions(manage_messages = True)
    @commands.guild_only()
    async def unwarn(self, ctx, member: discord.Member, warnId = None):
        #role check, so that moderators can't ban administrators
        if ctx.author.top_role < member.top_role:
            return await ctx.send("{cross} You can't warn someone that has an higher role than yours.".format(cross = Emoji.cross))

        data = collection.find_one({"_id" : ctx.guild.id})["members"]

        #role check
        if str(member.id) not in data or "warns" not in data[str(member.id)] or len(data[str(member.id)]["warns"]) == 0:
            return await ctx.send("{cross} This member doesn't have any warns.".format(cross = Emoji.cross))

        #removes the warn from the database
        dbMember = data[str(member.id)]

        #without id takes the last warn that has been done
        if warnId == None:
            el = dbMember["warns"][-1]
            dbMember["warns"].pop()
            data.update({str(member.id) : dbMember})
        
        #if an id is specified tries to find it in the database
        else:
            for el in dbMember["warns"]:
                if el["id"] == warnId:
                    dbMember["warns"].pop(dbMember["warns"].index(el))
                    data.update({str(member.id) : dbMember})
                
        #if nothing has changed it means that didn't find the specified id
        if data == collection.find_one({"_id" : ctx.guild.id})["members"]:
            return await ctx.send("{cross} Couldn't find the specified warn id.".format(cross = Emoji.cross))

        #updating database
        collection.update_one({"_id": ctx.guild.id}, {"$set": {"members" : data}})
        
        #sends a dm to the user
        try:
            await member.send(
                embed = Functions.dmEmbed(
                    ctx, "{warn} | UnWarn from {server}".format(warn = Emoji.warn, server = ctx.guild.name),
                    "One of your previus warns were removed from the `{server}` server.\n**Previus Warn id:** {Id}\n**Previus Warn Reason:** {reason}.".format(server = ctx.guild.name, Id = el["id"], reason = el["reason"]), False
                )
            )
        except:
            await ctx.send("{warning} I couldn't send a dm to the user, proceeding with the unwarn".format(warning = Emoji.warning))

        #sends an embed in the selected logging channel
        try:
            await ctx.guild.get_channel(int(collection.find_one({"_id" : ctx.guild.id})["logs"]["warn"])).send(
                embed = Functions.logEmbed(
                    ctx, "{warn} | UnWarn Case".format(warn = Emoji.warn), ctx.author, member, False, el["id"]
                )
            )
        except:
            pass
        
        #sends a confirmation message in ctx
        await ctx.send("{warn} the warn with id {Id} ha been removed from {member}(`{memberId}`).".format(warn = Emoji.warn, member = member, memberId = member.id, Id = el["id"]))

def setup(client):
    client.add_cog(Warn(client))