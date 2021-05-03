import os
import dbl
import datetime

from discord.ext import commands

class TopGG(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.token = os.environ["DSL_TOKEN"]
        self.dblpy = dbl.DBLClient(self.client, self.token, autopost=True)

    @commands.Cog.listener()
    async def on_guild_post(self):
        channel = self.client.get_channel(748894459118354532)
        msg = "Server count posted successfully"
        async for message in channel.history(limit = 1):
            if message.content.startswith(msg):
                time = datetime.datetime.now().strftime("%d/%m-%H:%M")
                return await message.edit(content = f"{msg} ({str(len(self.client.guilds))}) [{time}]")
        async for message in channel.history(limit = 20):
            if message.content.startswith(msg):
                await message.delete()
        time = datetime.datetime.now().strftime("%d/%m-%H:%M")
        await channel.send(content = f"{msg} ({str(len(self.client.guilds))}) [{time}]")

def setup(client):
    client.add_cog(TopGG(client))
