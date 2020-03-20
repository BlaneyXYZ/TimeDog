from datetime import datetime
import discord
import pytz
from discord.ext import commands, tasks
from itertools import cycle
import logging

logging.basicConfig(level=logging.ERROR)

client = commands.Bot(command_prefix='!')
timezone = "Australia/Melbourne"

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    change_time.start()
    await client.change_presence(activity=discord.Game("with father time ;)"))

@tasks.loop(seconds=10)
async def change_time():
        guild = client.get_guild('server here as guild')
        await guild.me.edit(
            nick=pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone(timezone)).strftime('%a - %I:%M %p'))

@client.command()
async def servers(message):
    servers = list(client.guilds)
    await message.channel.send(f"Connected on {str(len(servers))} servers:")
    await message.channel.send('\n'.join(server for server in servers))

client.run('your key here')