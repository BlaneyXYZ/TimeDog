import json
from datetime import datetime
import discord
import pytz
from discord.ext import commands, tasks
import logging

logging.basicConfig(level=logging.ERROR)

CONFIG_FILE = json.loads(open("config.json").read())
client = commands.Bot(command_prefix='!')
bot_timezone = "Australia/Melbourne"


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    change_time.start()
    await client.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = (CONFIG_FILE["now_playing"])))


@tasks.loop(seconds=10)
async def change_time():
    guild = client.get_guild(int(CONFIG_FILE["guild_id"]))
    await guild.me.edit(
        nick=pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone(bot_timezone)).strftime('%a - %I:%M %p'))


@client.command()
async def servers(message):
    servers = list(client.guilds)
    await message.channel.send(f"Connected on {str(len(servers))} servers:")
    await message.channel.send('\n'.join(server for server in servers))


@client.command(name="timezone", help="Changes the current timezone used by the bot, format is Country/City i.e "
                                      "Australia/Melbourne")
@commands.is_owner()
async def cmd_tz(message, timezone):
    await message.channel.send("Timezone changed to {}".format(timezone))
    global bot_timezone
    bot_timezone = timezone


@cmd_tz.error
async def info_error(message, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await message.channel.send(
            'Timezone missing, please enter one in the format Country/City i.e Australia/Melbourne')

client.run(CONFIG_FILE["api_key"])
