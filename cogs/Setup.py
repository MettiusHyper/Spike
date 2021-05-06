import discord

from discord.ext import commands
from Global import collection, Commands, Emoji, Functions

class Setup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name = Commands.Setup["name"], description = Commands.Setup["description"], aliases = Commands.Setup["aliases"], invoke_without_command = True, case_insensitive = True, enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.guild_only()
    async def setup(self, ctx):
        pass

def setup(client):
    client.add_cog(Setup(client))