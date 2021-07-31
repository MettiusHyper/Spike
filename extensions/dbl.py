#import os, dbl
from discord.ext import commands

class TopGG(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
#		self.token = os.environ['DSL_TOKEN']
#		self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

def setup(bot):
	bot.add_cog(TopGG(bot))