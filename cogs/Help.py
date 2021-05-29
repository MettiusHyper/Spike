import discord

from discord.ext import commands
from Global import collection, Commands, Emoji, Functions, Dev

def getAllCommands():
    returnObj = {}
    spikeCommands = vars(Commands).items()
    for el in spikeCommands:
        if el[0].startswith("__") == False:
            returnObj.update({el[0] : el[1]})
    returnObj = sorted(returnObj.items(), key=lambda kv : kv[1]["type"])
    return returnObj

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = Commands.Help["name"], description = Commands.Help["description"], aliases = Commands.Help["aliases"], enabled = collection.find_one({"_id":"developer"})["commands"])
    async def help(self, ctx, arg: str = None):
        embed = discord.Embed(color = Functions.color(ctx))
        spikeCommands = getAllCommands()
        if arg == None:
            embed.title = "Help {emoji}".format(emoji = Emoji.help)
            description = ""
            for el in spikeCommands:
                description += f"**{el[1]['name']}** | `{el[1]['short']}`\n"
            embed.description = description
        else:
            for el in spikeCommands:
                if el[1]['name'].lower() == arg.lower():
                    embed.title = f"{el[1]['name']} {Emoji.help}"
                    embed.description = el[1]['description']
                    if el[1]['permissions'] != None:
                        embed.add_field(name = "Permission Level", value=str(el[1]['permissions']))
                    else:
                        embed.add_field(name = "Permission Level", value="None")
                    if el[1]['aliases'] != []:
                        embed.add_field(name = "Aliases", value=str(el[1]['aliases']))
                    else:
                        embed.add_field(name = "Aliases", value="None")
        embed.set_footer(icon_url=self.client.user.avatar_url, text = "Type {prefix}help [command] for more info on a command.".format(prefix = Dev.prefix(self.client, ctx.message)[1]))
        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Help(client))
