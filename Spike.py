import os
import discord

from discord.ext import commands
from Global import logger, Dev, Functions

#intents, everything except presence (not enabled in discord developer portal)
intents = discord.Intents.default()
intents.members = True

#creating client with discord.ext.commands
client = commands.Bot(command_prefix = Dev.prefix, intents = intents, case_insensitive = True)
client.remove_command("help")

#loads every cog in the cogs folder
for cog in os.listdir("./cogs"):
    try:
        client.load_extension(f"cogs.{cog[:-3]}")
    except Exception as e:
        logger.error(f"exception in {cog}: {e}")

#login confirmation
@client.event
async def on_ready():
    await Functions.updateStatus(client)
    logger.info(f'We have logged in as {client.user}')

client.run(os.environ["TOKEN"])
