import logging
import pymongo
import discord
import datetime
import sys
import os

logger = logging.getLogger('Spike')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s:%(name)s: %(message)s', datefmt="%d/%m/%Y %H:%M:%S"))
logger.addHandler(handler)

collection = pymongo.MongoClient(os.environ['MONGO'])["Bots"]["SpikeDatabase"]

class Data:
    version = "0.1.0"
    prefix = "s!"
    default_color = 0x177e45
    empty_color = 0x2f3136
    invite_link = "https://cutt.ly/netbot-spike"
    website = "https://netbot.yolasite.com/"
    bugReportLink = "https://forms.gle/rE1uq4pHKr82Sc1j9"
    discordInvite = "https://discord.com/invite/WVr852CRpW"

class Emoji:
    tick = "<a:tick:763083389217144852>"
    cross = "<a:across:763083473396301854>"
    ban = ":hammer:"
    ping_pong = ":ping_pong:"
    warning = ":warning:"
    warn = ":radioactive:"
    unban = ":dove:"
    mute = ":mute:"
    kick = ":boot:"
    message = "<:mail:768126419963346959>"
    mongodb = "<:mongodb:768126166732636181>"
    botdev = "<:botdev:768126563605676082>"
    version = "<:version:768126836014055465>"
    online = "<:online:768127882932256859>"
    bot = "<:bot:768127528862482433>"
    website = "<:website:768128391256866817>"
    link = ":link:"
    bug = "<:bug:772133734841057321>"
    discordLogo = "<:discord_logo:772138358641524817>"
    website = "<:website:768128391256866817>"
    members = "<:members:772528856187666443>"
    boost = "<:boost:772528846775648258>"
    channels = "<:channels:772528907156586537>"
    owner = "<:owner:772528832804290620>"
    clear = ":soap:"
    help = "<:info:838005178287915059>"
    setup = ":gear:"
    pencil = ":pencil:"

class Functions:
    def dmEmbed(guild, title, description, reason):
        if reason == None:
            reason = "No reason provided"

        embed = discord.Embed(
            title = title,
            description = description,
            timestamp = datetime.datetime.now(),
            color = Data.empty_color
        )
        if reason != False:
            embed.add_field(name = "Reason:", value = reason)
        embed.set_footer(text = guild.name, icon_url = guild.icon_url)
        if "ban" in title.lower():
            try:
                embed.set_field(name = "BanAppeal:", value = f"https://docs.google.com/forms{collection.find_one({'_id' : guild.id})['banappeal']}")
            except:
                pass

        return embed

    def logEmbed(guild, title, staff, member, reason, Id = None):
        if reason == None:
            reason = "No reason provided"
        description = "**Member:** {member}\n**Staff:** {staff}".format(member = member, staff = staff)
        if Id != None:
            if "-" in Id:
                description = "**Id:** {d}\n".format(d = Id) + description
            else:
                description = "**Duration:** {d}\n".format(d = Id) + description
        if reason != False:
            description += "\n**Reason:** {reason}".format(reason = reason)

        embed = discord.Embed(
            title = title,
            description = description,
            timestamp = datetime.datetime.now(),
            color = Functions.color(guild)
        )
        embed.set_footer(text = guild.name, icon_url = guild.icon_url)

        return embed

    def color(ctx):
        try:
            guild = ctx.guild
        except:
            guild = ctx
        if guild == None:
            return Data.default_color

        for role in guild.me.roles:
            if role.color != discord.Colour.default():
                return role.color

        return Data.default_color

    async def isUserBanned(ctx, member):
        banned = False
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            if ban_entry.user.id == member.id:
                banned = True
        return banned

    async def banReason(ctx, member):
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            if ban_entry.user.id == member.id:
                return ban_entry.reason
        return None

    async def sendEmbed(ctx, embed):
        try:
            await ctx.send(embed = embed)
        except:
            await ctx.author.send(content = "{0} I can't send messages in the command's channel.".format(Emoji.cross), embed = embed)

    def isDev(user):
        if user.id in collection.find_one({"_id" : "developer"})["developers"]:
            return True
        return False

    async def updateStatus(client):
        activity = {
        "listening" : discord.ActivityType.listening,
        "watching" : discord.ActivityType.watching
        }
        status = {
            "online" : discord.Status.online,
            "dnd" : discord.Status.dnd,
            "idle" : discord.Status.idle
        }
        data = collection.find_one({"_id" : "developer"})
        if data["type"] == "playing":
            CustomActivity = discord.Game(name = data["name"])
        else:
            CustomActivity = discord.Activity(type = activity[data["type"]], name = data["name"]) 
        await client.change_presence(status = status[data["status"]], activity = CustomActivity)

    def prefixEmbed(self, message):
        prefix = Dev.prefix(self.client, message)[1]
        embed = discord.Embed(colour = Functions.color(message), description = "For {guild} server the prefix is **{p}**\n\nUse `{p}help` for more help.".format(guild = message.guild, p = prefix))
        embed.set_author(name = "Server Prefix", icon_url = self.client.user.avatar_url)
        return embed
    
    async def createMuteRole(self, ctx):
        role = await ctx.guild.create_role(name = "muted", colour = discord.Colour(0x010101), reason = f"Role for {self.client.user.name}.")
        for channel in ctx.guild.channels:
            try:
                await channel.set_permissions(role, send_messages = False, add_reactions = False, connect = False)
            except:
                pass
        positions = {role : ctx.guild.me.top_role.position}
        await ctx.guild.edit_role_positions(positions)
        settings = collection.find_one({"_id" : ctx.guild.id})["settings"]
        settings.update({"muterole" : role.id})
        collection.update_one({"_id" : ctx.guild.id}, {"$set" : {"settings" : settings}})
        return role

    def convertToTimedelta(timeStr):
        timeStr = (''.join(timeStr.split())).lower()
        if timeStr.startswith("in"):
            timeStr = timeStr[2:]
        days, hours, minutes, seconds = 0, 0, 0, 0
        for x in ["days", "day", "d"]:
            if x in timeStr:
                index = timeStr.index(x[0])
                try:
                    days = int(f"{timeStr[index - 2]}{timeStr[index - 1]}")
                    timeStr = timeStr[2 + len(x):]
                except:
                    days = int(timeStr[index - 1])
                    timeStr = timeStr[1 + len(x):]
        for x in ["hours", "hour", "h"]:
            if x in timeStr:
                index = timeStr.index(x[0])
                try:
                    hours = int(f"{timeStr[index - 2]}{timeStr[index - 1]}")
                    timeStr = timeStr[2 + len(x):]
                except:
                    hours = int(timeStr[index - 1])
                    timeStr = timeStr[1 + len(x):]
        for x in ["minutes", "minute", "mins", "min", "m"]:
            if x in timeStr:
                index = timeStr.index(x[0])
                try:
                    minutes = int(f"{timeStr[index - 2]}{timeStr[index - 1]}")
                    timeStr = timeStr[2 + len(x):]
                except:
                    minutes = int(timeStr[index - 1])
                    timeStr = timeStr[1 + len(x):]
        for x in ["seconds", "second", "secs", "sec", "s"]:
            if x in timeStr:
                index = timeStr.index(x[0])
                try:
                    seconds = int(f"{timeStr[index - 2]}{timeStr[index - 1]}")
                    timeStr = timeStr[2 + len(x):]
                except:
                    seconds = int(timeStr[index - 1])
                    timeStr = timeStr[1 + len(x):]
        return datetime.timedelta(days = days, hours = hours, minutes= minutes, seconds = seconds)

    def formatDelta(timeDelta):
        if timeDelta > datetime.timedelta(days = 1):
            returnObj = "{d} day {h} hours".format(d = round(timeDelta.days), h = round(timeDelta.seconds/3600))
        elif timeDelta > datetime.timedelta(hours= 1.5):
            returnObj = "{h} hours {m} minutes".format(h = round(timeDelta.seconds/3600), m = round(timeDelta.seconds % 3600 / 60.0))
        else:
            returnObj = "{m} minutes".format(m = round(timeDelta.seconds / 60))
        return returnObj

class Dev:
    #prefix function, used for custom prefix
    def prefix(client, message):
        try:
            prefix = collection.find_one({"_id" : message.guild.id})["prefix"]
            return (f"{prefix} ", prefix)
        except:
            return (f"{Data.prefix} ", Data.prefix)

#for commands type
#1: moderation
#2: utility

#for options type
#1: string
#2: integer
#3: member
#4: user
#5: channel
#6: role
class Commands:
    Help = {
        "name" : "Help",
        "short" : "This command",
        "description" : "Help command, returns a list of commands or information about the specified command.",
        "options" : [
            {
                "name" : "command",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : None,
        "type" : 2,
        "aliases" : []
    }
    Mute = {
        "name" : "Mute",
        "short" : "Mutes a member for a determined amount of time.",
        "description" : "Mutes a member of the server for a determined amount of time, you can also specify a reason for the moderation action.",
        "options" : [
            {
                "name" : "member",
                "required" : True,
                "type" : 3
            },
            {
                "name" : "duration",
                "required" : True,
                "type" : 1
            },
            {
                "name" : "reason",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : "Mute Members",
        "type" : 1,
        "aliases" : []
    }
    UnMute = {
        "name" : "UnMute",
        "short" : "UnMutes a member of the server",
        "description" : "UnMutes a member that has previusly been muted in the server, you can also specify a reason for the moderation action.",
        "options" : [
            {
                "name" : "member",
                "required" : True,
                "type" : 3
            },
            {
                "name" : "reason",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : "Mute Members",
        "type" : 1,
        "aliases" : []
    }
    Kick = {
        "name" : "Kick",
        "short" : "Kicks a member from the server.",
        "description" : "Kicks a member from the server, you can also specify a reason for the moderation action.",
        "options" : [
            {
                "name" : "member",
                "required" : True,
                "type" : 3
            },
            {
                "name" : "reason",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : "Kick Members",
        "type" : 1,
        "aliases" : []
    }
    Ban = {
        "name" : "Ban",
        "short" : "Bans a member from the server.",
        "description" : "Bans a member from the server, you can also specify a reason for the moderation action. If setted, a link for appealing the ban gets sent in the ",
        "options" : [
            {
                "name" : "user",
                "required" : True,
                "type" : 4
            },
            {
                "name" : "reason",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : "Ban Members",
        "type" : 1,
        "aliases" : []
    }
    UnBan = {
        "name" : "UnBan",
        "short" : "UnBans a user from the server.",
        "description" : "UnBans a user from the server, you can also specify a reason for the moderation action.",
        "options" : [
            {
                "name" : "user",
                "required" : True,
                "type" : 4
            },
            {
                "name" : "reason",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : "Ban Members",
        "type" : 1,
        "aliases" : []
    }
    Warn = {
        "name" : "Warn",
        "short" : "Adds a warn to a member of the server.",
        "description" : "Adds a warn to a member of the server, also gives moderators an uuid to remove the warn if necessary. You can also specify a reason for the moderation action.",
        "options" : [
            {
                "name" : "member",
                "required" : True,
                "type" : 3
            },
            {
                "name" : "reason",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : "Manage Messages",
        "type" : 1,
        "aliases" : []
    }
    UnWarn = {
        "name" : "UnWarn",
        "short" : "Removes a warn from a member of the server.",
        "description" : "Removes a warn from a member of the server. You can specify the warn uuid to remove the specific warn and also a reason for the moderation action.",
        "options" : [
            {
                "name" : "member",
                "required" : True,
                "type" : 3
            },
            {
                "name" : "warn id",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : "Manage Messages",
        "type" : 1,
        "aliases" : []
    }
    Userinfo = {
        "name" : "Userinfo",
        "short" : "Gives informations about the specified user.",
        "description" : "Gives informations about the specified user, if the one executing the command has the manage_messages permission the bot will also return some moderation info.",
        "options" : [
            {
                "name" : "user",
                "required" : False,
                "type" : 4
            }
        ],
        "permissions" : None,
        "type" : 1,
        "aliases" : ["infouser"]
    }
    Ping = {
        "name" : "Ping",
        "short" : "Returns the current ping of the bot.",
        "description" : "Returns the current ping of the bot.",
        "options" : [],
        "permissions" : None,
        "type" : 2,
        "aliases" : ["latency"]
    }
    Info = {
        "name" : "Info",
        "short" : "Returns some information about the bot.",
        "description" : "Returns some information about the bot.",
        "options" : [],
        "permissions" : None,
        "type" : 2,
        "aliases" : ["information", "informations", "informazioni", "informazione"]
    }
    Link = {
        "name" : "Link",
        "short" : "Returns every link related to the bot.",
        "description" : "rns every link related to the bot.",
        "options" : [],
        "permissions" : None,
        "type" : 2,
        "aliases" : ["errore", "problema", "links", "bug", "invito", "invita", "invite"]
    }
    Prefix = {
        "name" : "Prefix",
        "short" : "Allows the change the custom server's prefix.",
        "description" : "Allows the change the custom server's prefix.",
        "options" : [
            {
                "name" : "new prefix",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : "Administrator",
        "type" : 2,
        "aliases" : []
    }
    ServerInfo = {
        "name" : "ServerInfo",
        "short" : "Returns lots of information about the guild.",
        "description" : "Returns lots of information about the guild, and also a chart with the amount of users that were in the server in the last 9 days",
        "options" : [
            {
                "name" : "new prefix",
                "required" : False,
                "type" : 1
            }
        ],
        "permissions" : None,
        "type" : 2,
        "aliases" : []
    }
