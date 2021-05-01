import os
import ast

from discord.ext import commands
from pypertrail.search import Search
from Global import Emoji, Functions, collection

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
        if Functions.isDev(ctx.author):
            python = "```py\n{}\n```"
            if code == None:
                return await ctx.send("**Enviroment variable**\n'self': self\n'ctx': ctx\n'collection': collection")
            code = code.strip("` ")
            code = "\n".join(f"    {i}" for i in code.splitlines())
            result = "None"

            env = {
                'self': self,
                'ctx': ctx,
                "collection": collection,
            }
            env.update(globals())

            try:
                fn_name = "_eval_expr"

                body = f"async def {fn_name}():\n{code}"

                parsed = ast.parse(body)
                body = parsed.body[0].body

                insert_returns(body)

                exec(compile(parsed, filename="<ast>", mode="exec"), env)

                result = (await eval(f"{fn_name}()", env))
            except Exception as e:
                return await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))

            try:
                result = str(result)
            except:
                pass
            
            await ctx.message.add_reaction(Emoji.tick)
            while len(result) > 0:
                await ctx.send(python.format(result[:1988]))
                result = result[1988:]

    @commands.command()
    async def logs(self, ctx):
        if Functions.isDev(ctx.author) == True:
            async with ctx.channel.typing():
                #gathering the logs
                search = Search(os.environ['PAPERTRAIL_API_TOKEN'])
                data = search.events()
                
                #formatting
                logs = ""
                for event in data["events"]:
                    if len(logs) <= 1994:
                        if logs == None:
                            logs = event['message']
                        else:
                            logs += event["message"]
                logs = logs[:1991] + "..."
                #more formatting
                for word in logs:
                    if word.endswith("@gmail.com"):
                        logs = logs.replace(word, "e-mail")
                logs = logs.replace("*", "∗")

                await ctx.send(f"```{logs}```")

    @commands.command()
    @commands.guild_only()
    async def status(self, ctx, status : str, activity : str = "", *,  game : str = None):
        if Functions.isDev(ctx.author):
            if status.lower() in ("online", "dnd", "idle"):
                collection.update_one({"_id" : "developer"}, {"$set" : {"status" : status}})
            else:
                return await ctx.send(f"{Emoji.cross} Not a valid customstatus name, choose from [online, dnd, idle]")
            if activity.lower() in ("playing", "listening", "watching"):
                collection.update_one({"_id" : "developer"}, {"$set" : {"type" : activity}})
            if game != None:
                collection.update_one({"_id" : "developer"}, {"$set" : {"name" : game}})
            await Functions.updateStatus(self.client)
            await ctx.send(f"{Emoji.tick} Status modified to {status}, activity setted to {activity} | {str(game)}")

def setup(client):
    client.add_cog(Dev(client))
