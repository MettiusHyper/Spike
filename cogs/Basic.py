import time
import discord

from discord.ext import commands
from Global import Data, collection, Commands, Emoji, Functions, Dev

class Basic(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(name = Commands.Ping["name"], description = Commands.Ping["description"], aliases = Commands.Ping["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    async def ping(self, ctx):
        #ping of the database
        dbPing = time.monotonic()
        data = collection.insert_one({})
        dbPing = round((time.monotonic() - dbPing) * 1000)
        collection.delete_one({"_id" : data.inserted_id})

        #ping of messages
        messagePing = time.monotonic()
        msg = await self.client.get_channel(832671016236351538).send(Emoji.ping_pong)
        messagePing = round((time.monotonic() - messagePing) * 1000)
        await msg.delete()

        #sending embed
        await Functions.sendEmbed(
            ctx,
            discord.Embed(
                color = Functions.color(ctx),
                description = "**Ping** {pong} {ping} ms\n**Message Ping** {message} {mPing} ms\n**Database Ping** {db} {dPing} ms"
                .format(pong = Emoji.ping_pong, ping = round(self.client.latency*1000), message = Emoji.message, mPing = messagePing, db = Emoji.mongodb, dPing = dbPing)
            )
        )
    
    @commands.command(name = Commands.Info["name"], description = Commands.Info["description"], aliases = Commands.Info["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    async def info(self, ctx):
        
        #sending embed
        await Functions.sendEmbed(
            ctx,
            discord.Embed(
                color = Functions.color(ctx),
                description = "This is a very simple moderation bot, with some other very useful features\nand its also hugely customisable."
            )
            .add_field(name = "Version {emoji}".format(emoji = Emoji.version), value = f"v. {Data.version}")
            .add_field(name = "Servers {emoji}".format(emoji = Emoji.online), value = "{bot}'s in {guilds} servers".format(bot = self.client.user.name, guilds = len(self.client.guilds)))
            .add_field(name = "Developer {emoji}".format(emoji = Emoji.botdev), value = self.client.get_user(707165674845241344).mention)
            .add_field(name = "Bot Invite {emoji}".format(emoji = Emoji.bot), value = "[Click here to invite me]({invite})".format(invite = Data.invite_link))
            .add_field(name = "WebSite {emoji}".format(emoji = Emoji.website), value = f"[netbot.yolasite.com]({Data.website})")
            .add_field(name = "\u200C", value = "\u200C", inline = True)
        )

    @commands.command(name = Commands.Link["name"], description = Commands.Link["description"], aliases = Commands.Link["aliases"])
    async def link(self, ctx):
        #sending embed
        await Functions.sendEmbed(ctx, embed = discord.Embed(
            colour = Functions.color(ctx), title = "Links {0}".format(Emoji.link),
            description = "[**Bot Invite**]({invite}) {bot}\n[**Bug Report**]({gLink}) {bug}\n[**Support Server**]({dInvite}) {discord}\n[**Website**]({site}) {web}"
            .format(
                invite = Data.invite_link, bot = Emoji.bot,
                gLink = Data.bugReportLink, bug = Emoji.bug,
                dInvite = Data.discordInvite, discord = Emoji.discordLogo,
                web = Emoji.website, site = Data.website
            ))
        )

    @commands.command(name = Commands.Prefix["name"], description = Commands.Prefix["description"], aliases = Commands.Prefix["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.guild_only()
    async def prefix(self, ctx, prefix : str = None):
        if prefix == None or ctx.author.guild_permissions.administrator == False:
            return await ctx.send(embed = Functions.prefixEmbed(self, ctx))
        embed = discord.Embed(color = Functions.color(ctx), title = "Prefix {pencil}".format(pencil = Emoji.pencil))
        if prefix == Dev.prefix(self.client, ctx)[1]:
            embed.description = "\nThis is already the server's prefix (`{p}`).".format(p = Dev.prefix(self.client, ctx)[1])
            return await ctx.send(embed = embed)
        collection.update_one({"_id" : ctx.guild.id}, {"$set" : {"prefix" : prefix}})
        embed.description = "\nPrefix setted correcty, the new prefix is `{p}`.".format(p = Dev.prefix(self.client, ctx)[1])
        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Basic(client))