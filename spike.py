import os, discord
from discord.ext import commands

from core import *

client = commands.Bot(command_prefix = custom_prefix, case_insensitive = True)

for file in os.listdir('./extensions'):
	client.load_extension(f'extensions.{file[:-3]}')

client.run(os.environ['TOKEN'])
