from re import I
import discord
import asyncio

from discord.ext import commands
from Global import Dev, collection, Commands, Emoji, Functions

class Setup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name = Commands.Setup["name"], description = Commands.Setup["description"], aliases = Commands.Setup["aliases"], invoke_without_command = True, case_insensitive = True, enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def setup(self, ctx):
        await ctx.send(embed = discord.Embed(
                color = Functions.color(ctx), title = "Setup {emoji}".format(emoji = Emoji.setup)
            )
            .add_field(name = "{} Logs".format(Emoji.channels), value="Use `{prefix}settings logs`".format(prefix = Dev.prefix(self.client, ctx.message)[1]))
            .add_field(name = "{} BanAppeal".format(Emoji.ban), value="Use `{prefix}settings banappeal`".format(prefix = Dev.prefix(self.client, ctx.message)[1]))
            .add_field(name = "\u200C", value = "\u200C")
            .add_field(name = "{} MuteRole".format(Emoji.mute), value="Use `{prefix}settings muterole`".format(prefix = Dev.prefix(self.client, ctx.message)[1]))
            .add_field(name = "{} Prefix".format(Emoji.pencil), value="Use `{prefix}prefix`".format(prefix = Dev.prefix(self.client, ctx.message)[1]))
            .add_field(name = "\u200C", value = "\u200C")
        )
    
    @setup.command(name = "logs")
    async def logs(self, ctx):
        await ctx.send("This command will soon be implemented")

    @setup.command(name = "banappeal")
    async def banappeal(self, ctx):
        settings = collection.find_one({"_id" : ctx.guild.id})["settings"]
        if "banappeal" in settings:
            link = settings["banappeal"]
        else:
            link = "`Not setted`"
        msg = await ctx.send(
            embed = discord.Embed(
                color = Functions.color(ctx),
                title = "BanAppeal {emoji}".format(emoji = Emoji.ban),
                description = "React with:\n{green} to specify a new link\n{red} to remove the current link".format(green = Emoji.greenSq, red = Emoji.redSq)
            )
            .add_field(name = "Setted link", value = link)
        )
        await msg.add_reaction("🟩")
        await msg.add_reaction("🟥")
        try:
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ("🟥", "🟩")
            reaction, user = await self.client.wait_for('reaction_add', timeout = 60.0, check = check)
            if str(reaction) == "🟩":
                await ctx.send("Send a message with only the new **link** to be used to appeal bans.")
                def check(m):
                    return m.author == ctx.author
                try:
                    command = await self.client.wait_for('message', timeout = 60.0, check=check)
                    command = command.content
                    if command.startswith("https://docs.google.com/forms"):
                        settings.update({"banappeal" : command.strip()})
                        collection.update_one({"_id": ctx.guild.id}, {"$set": {"settings" : settings}})
                        await ctx.send("{} Link has been setted".format(Emoji.tick))
                    else:
                        await ctx.send("{} Please specify a valid link (only link starting with <https://docs.google.com/forms> are allowed)".format(Emoji.cross))
                except:
                    raise asyncio.TimeoutError
            elif str(reaction) == "🟥":
                if link.startswith("`"):
                    await ctx.send("{} No link has been previusly setted.".format(Emoji.cross))
                else:
                    del settings['banappeal']
                    collection.update_one({"_id": ctx.guild.id}, {"$set": {"settings" : settings}})
                    await ctx.send("{} Link has been removed from the bot's settings".format(Emoji.tick))
            raise asyncio.TimeoutError
        except asyncio.TimeoutError:
            message = await ctx.channel.fetch_message(msg.id)
            await message.clear_reactions()
    
    @setup.command(name = "muterole")
    @commands.has_permissions(administrator = True)
    @commands.guild_only()
    async def muterole(self, ctx):
        settings = collection.find_one({"_id" : ctx.guild.id})["settings"]
        if "muterole" in settings and ctx.guild.get_role(settings["muterole"]) != None:
            role = ctx.guild.get_role(settings["muterole"]).mention
        else:
            role = "`Not setted`"
        msg = await ctx.send(
            embed = discord.Embed(
                color = Functions.color(ctx),
                title = "MuteRole {emoji}".format(emoji = Emoji.mute),
                description = "React with:\n{green} to specify a custom role\n{red} to remove the current role\n{mute} to create a standard one".format(green = Emoji.greenSq, red = Emoji.redSq, mute = Emoji.mute)
            )
            .add_field(name = "Setted role", value = role)
        )
        await msg.add_reaction("🟩")
        await msg.add_reaction("🟥")
        await msg.add_reaction("🔇")
        try:
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ("🟥", "🔇", "🟩")
            reaction, user = await self.client.wait_for('reaction_add', timeout = 60.0, check = check)
            if str(reaction) == "🟩":
                await ctx.send("Send a message with only the **mention** or the **id** of the role.")
                def check(m):
                    return m.author == ctx.author
                try:
                    command = await self.client.wait_for('message', timeout = 60.0, check=check)
                    command = command.content
                    try:
                        if command.startswith("<@&") and command.endswith(">"):
                            command = int(command.strip()[-19:-1])
                        else:
                            command = int(command)
                    except:
                        pass
                    if (type(command) == int and len(str(command)) == 18) and ctx.guild.get_role(command) != None:
                        settings.update({"muterole" : command})
                        collection.update_one({"_id": ctx.guild.id}, {"$set": {"settings" : settings}})
                        await ctx.send("{} Role has been setted".format(Emoji.tick))
                    else:
                        await ctx.send("{} Please specify a valid role".format(Emoji.cross))
                except:
                    raise asyncio.TimeoutError
            elif str(reaction) == "🟥":
                if role.startswith("`"):
                    await ctx.send("{} No role has been previusly setted.".format(Emoji.cross))
                else:
                    del settings['muterole']
                    collection.update_one({"_id": ctx.guild.id}, {"$set": {"settings" : settings}})
                    await ctx.send("{} Role has been removed from the bot's settings".format(Emoji.tick))
            elif str(reaction) == "🔇":
                nRole = await Functions.createMuteRole(self, ctx)
                await ctx.send("{tick} New role has been created ({role})".format(tick = Emoji.tick, role = nRole.mention))
            raise asyncio.TimeoutError
        except asyncio.TimeoutError:
            message = await ctx.channel.fetch_message(msg.id)
            await message.clear_reactions()
                
def setup(client):
    client.add_cog(Setup(client))