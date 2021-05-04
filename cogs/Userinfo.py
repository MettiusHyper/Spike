import discord
import datetime

from discord.ext import commands
from Global import collection, Commands, Emoji, Functions

class Userinfo(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = Commands.Userinfo["name"], description = Commands.Userinfo["description"], aliases = Commands.Userinfo["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.User = None):
        if member == None:
            member = ctx.author
        
        if ctx.guild.get_member(member.id) != None:
            member = ctx.guild.get_member(member.id)
            
        embed = discord.Embed(title = "Userinfo", color = Functions.color(ctx))
        embed.add_field(name = member, value = f"<@{member.id}> | {member.id}", inline = False)
        embed.set_thumbnail(url = member.avatar_url)
        embed.add_field(name = "Joined Discord:", value = "{}\n({} days ago)".format(member.created_at.strftime('%d %B %Y, %H:%M'), (datetime.datetime.utcnow() - member.created_at).days))
        if isinstance(member, discord.Member):
            embed.add_field(name = "Joined Server:", value = "{}\n({} days ago)".format(member.joined_at.strftime('%d %B %Y, %H:%M'), (datetime.datetime.utcnow() - member.joined_at).days))
            embed.add_field(name = "Highest Role", value = member.top_role.mention, inline = False)
        else:
            embed.add_field(name = "Joined Server:", value = "This user is not in the server.")
            embed.add_field(name = "Highest Role", value = "No role", inline = False)
        if ctx.message.author.guild_permissions.manage_messages == True:
            if await Functions.isUserBanned(ctx, member):
                embed.add_field(name = "Infractions", value = Functions.banReason(ctx, member), inline = False)
            else:
                data = collection.find_one({"_id" : ctx.guild.id})["members"]
                if str(member.id) not in data:
                    warn = mute = kick = 0
                else:
                    dbMember = data[str(member.id)]
                    warn, mute, kick = 0, 0, 0
                    if "warns" in dbMember:
                        warn = len(dbMember["warns"])
                    if "mutes" in dbMember:
                        mute = (dbMember["mutes"])
                    if "kicks" in dbMember:
                        kick = (dbMember["kicks"])
                embed.add_field(name = "Infractions", value = "**Kicks** | User has got `{}` kicks\n**Mutes** | User has got `{}` mutes\n**Warns** | User has got `{}` warns".format(kick, mute, warn), inline = False)
        try:
            vc = ctx.author.voice
            if vc == None:
                vc = "Not connected"
        except:
            vc = "Not connected"
        embed.add_field(name = "Voice Channel", value = vc)
        if ctx.message.author.guild_permissions.manage_messages == True:
            data = collection.find_one({"_id" : "muted"})
            muteTime = None
            for el in data["muted"]:
                if el["user"] == member.id and el["guild"] == ctx.guild.id:
                    muteTime = Functions.formatDelta(el["date"] - datetime.datetime.now())
                    embed.add_field(name = "Mute", value = muteTime)
            if muteTime == None:
                embed.add_field(name = "Mute", value = "No active mute")
        else:
            if ctx.message.author.bot == True:
                embed.add_field(name = "Is Bot?", value="Yes")
            else:
                embed.add_field(name = "Is Bot?", value="No")
        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Userinfo(client))