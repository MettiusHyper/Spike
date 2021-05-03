import io
import os
import discord
import datetime

from discord.ext import commands
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import StrMethodFormatter
from Global import Data, collection, Commands, Emoji, Functions, Dev

blue = "#677BC4"
gray = "#B9BBBE"
black = "#292B2F"

class ServerInfo(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name = Commands.ServerInfo["name"], description = Commands.ServerInfo["description"], aliases = Commands.ServerInfo["aliases"], invoke_without_command = True, case_insensitive = True, enabled = collection.find_one({"_id":"developer"})["commands"])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        embed = discord.Embed(colour = Functions.color(ctx))
        embed.set_author(name = f"{ctx.guild.name} ({ctx.guild.id})", icon_url = ctx.guild.icon_url)
        owner = await self.client.fetch_user(ctx.guild.owner_id)
        embed.add_field(name = "Users {}".format(Emoji.members), value = str(ctx.guild.member_count))
        embed.add_field(name = "Roles", value = str(len(ctx.guild.roles)))
        embed.add_field(name = "Boosts {}".format(Emoji.boost), value = str(ctx.guild.premium_subscription_count))
        embed.add_field(name = "Channels {}".format(Emoji.channels), value = str(len(ctx.guild.text_channels) + len(ctx.guild.voice_channels)))
        embed.add_field(name = "Owner {}".format(Emoji.owner), value = owner.mention)
        embed.add_field(name = "Bots {}".format(Emoji.bot), value = sum(member.bot for member in ctx.guild.members))
        embed.set_footer(text = "Data for the cart obtained every day at 12:00 UTC")
        try:
            data = collection.find_one({"_id" : ctx.guild.id})["users"]
            if data == False:
                embed.add_field(name = "\u200C", value = "{cross} Graph has been disabled. Use `{p}userinfo on`".format(cross = Emoji.cross, p = Dev.prefix(self.client, ctx)[1]))
                return await ctx.send(embed = embed)
        except:
            data = []

        if len(data) == 0:
            embed.add_field(name = "\u200C", value = "{} Not enough data to create a chart! Please try again tomorrow.".format(Emoji.cross))
            return await ctx.send(embed = embed)
        #getting x, the date part
        x = []
        if datetime.datetime.now().hour > 12:
            date = datetime.date.today() - datetime.timedelta(days = len(data) - 1)
        else:
            date = datetime.date.today() - datetime.timedelta(days = len(data))
        for el in data:
            x.append(date.strftime("%d/%m"))
            date = date + datetime.timedelta(days = 1)

        data_stream = io.BytesIO()
        #trowing in the golden ratio's number just because it'cool (then proceeding to break it by moltipling with different factors :)
        plt.figure(figsize=(1.618*4,1*3), facecolor = black)
        # plotting the points
        plt.plot(x, data, color = blue)

        file = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        file = str(file) + "/font/Roboto.ttf"
        #font = fm.FontProperties(fname=file)

        #setting colors       
        ax = plt.gca()
        ax.set_facecolor(black)
        ax.tick_params(colors =  gray)
        ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        for el in ax.spines:
            ax.spines[el].set_color(gray)
        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        data_stream.seek(0)
        chart = discord.File(data_stream,filename="image.png")
        embed.set_image(url="attachment://image.png")
        await ctx.send(embed = embed, file = chart)

    @serverinfo.command(name = "off")
    async def serverinfo_off(self, ctx):
        collection.update_one({"_id" : ctx.guild.id}, {"$set" : {"users" : False}})
        await ctx.send(f"{Emoji.tick} We will not collect data for the graph on this server anymore.")
    
    @serverinfo.command(name = "on")
    async def serverinfo_on(self, ctx):
        collection.update_one({"_id" : ctx.guild.id}, {"$set" : {"users" : []}})
        await ctx.send(f"{Emoji.tick} From now on the data for the graph will be collected.")

def setup(client):
    client.add_cog(ServerInfo(client))