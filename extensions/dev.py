import os, ast, requests, datetime
from discord.ext import commands

from core import *

def insert_returns(body):
	if isinstance(body[-1], ast.Expr):
		body[-1] = ast.Return(body[-1].value)
		ast.fix_missing_locations(body[-1])
	if isinstance(body[-1], ast.If):
		insert_returns(body[-1].body)
		insert_returns(body[-1].orelse)
	if isinstance(body[-1], ast.With):
		insert_returns(body[-1].body)

class Dev(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def eval(self, ctx, *, code : str = None):
		if is_developer(ctx.author.id):
			if code == None:
				return await ctx.send("**Enviroment variables**\n'self': self\n'ctx': ctx\n'collection': collection")
			code = code.strip('` ')
			code = '\n'.join(f'	{i}' for i in code.splitlines())
			result = str(None)
			env = {'self': self, 'ctx': ctx, 'collection': Vars.collection}
			env.update(globals())
			try:
				body = f'async def _eval_expr():\n{code}'
				parsed = ast.parse(body)
				body = parsed.body[0].body
				insert_returns(body)
				exec(compile(parsed, filename='<ast>', mode='exec'), env)
				result = (await eval('_eval_expr()', env))
			except Exception as e:
				return await ctx.send('```py\n{}\n```'.format(type(e).__name__ + ': ' + str(e)))
			await ctx.message.add_reaction(Emoji.tick)
			while len(str(result)) > 0:
				await ctx.send('```py\n{}\n```'.format(str(result)[:1988]))
				result = str(result)[1988:]

	@commands.command()
	async def logs(self, ctx):
		if is_developer(ctx.author.id):
			async with ctx.channel.typing():
				request = requests.get(
					'https://papertrailapp.com/api/v1/events/search.json?limit=20',
					headers={'X-Papertrail-Token': os.environ['PAPERTRAIL_API_TOKEN']})
				data = request.json()['events']
				data.reverse()
				logs = ''
				for el in data:
					if len(logs) <= 1994:
						logs += f"{datetime.datetime.strptime(el['generated_at'][:-6], '%Y-%m-%dT%H:%M:%S').strftime('%d/%m %H:%M:%S')} | {el['message']}"
				logs = logs[-1991:] + '...'
				#more formatting
				for word in logs:
					if word.endswith('@gmail.com'):
						logs = logs.replace(word, 'e-mail')
				logs = logs.replace('*', '∗')

				await ctx.send(f'```{logs}```')

	@commands.command()
	async def status(self, ctx, status : str, activity : str = '', *,  game : str = None):
		if is_developer(ctx.author.id):
			if status.lower() in ('online', 'dnd', 'idle'):
				Vars.collection.update_one({'_id' : 'developer'}, {'$set' : {'status' : status}})
			else:
				return await ctx.send(f'{Emoji.cross} Not a valid customstatus name, choose from [online, dnd, idle]')
			if activity.lower() in ('playing', 'listening', 'watching'):
				Vars.collection.update_one({'_id' : 'developer'}, {'$set' : {'type' : activity}})
			if game != None:
				Vars.collection.update_one({'_id' : 'developer'}, {'$set' : {'name' : game}})
			await update_status(self.client)
			await ctx.send(f'{Emoji.tick} Status modified to {status}, activity setted to {activity} | {str(game)}')

	@status.error
	async def status_error(self, ctx, error):
		if is_developer(ctx.author.id):
			await ctx.send(str(error) + '\n`%status [online|dnd|idle] [playing|listening|watching] [text]`')

def setup(client):
	client.add_cog(Dev(client))
