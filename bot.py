import asyncio
import json
from datetime import datetime, timedelta
import discord
import pytz
from discord.ext import commands, tasks
import logging
import time
import humanize

logging.basicConfig(level=logging.ERROR)
description = "whats the time dog"
CONFIG_FILE = json.loads(open("config.json").read())
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix='!', description=description, intents=intents)

timezone_dict = {}
start_time = time.monotonic()

# Config
botname = CONFIG_FILE["botname"]
api_key = CONFIG_FILE["api_key"]
bot_timezone = CONFIG_FILE["timezone"]
now_playing = CONFIG_FILE["now_playing"]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    change_time.start()
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=now_playing))
    for i in CONFIG_FILE['servers']:
        timezone_dict[i["guild_id"]] = i["timezone"]
    for guild in client.guilds:
        if guild.id not in timezone_dict:
            add_guild(guild.id, bot_timezone)
            print(guild)
            print(guild.id)


def add_guild(guild_id, timezone):
    timezone_dict[guild_id] = timezone
    with open("config.json", "r+") as file:
        file_data = json.load(file)
        file_data["servers"].append({"guild_id": guild_id, "timezone": timezone})
        file.seek(0)
        json.dump(file_data, file, indent=4)


def update_guild(guild_id, timezone):
    timezone_dict[guild_id] = timezone
    with open("config.json", "r+") as file:
        json_data = json.load(file)
        for item in json_data["servers"]:
            if item["guild_id"] == guild_id:
                item["timezone"] = timezone
        with open("config.json", "w") as file:
            json.dump(json_data, file, indent=4)


@tasks.loop(seconds=10)
async def change_time():
    try:
        for guild in client.guilds:
            await guild.me.edit(nick=pytz.utc.localize(datetime.utcnow()).astimezone(
                pytz.timezone(timezone_dict.get(guild.id))).strftime('%a - %I:%M %p'))
    except Exception as e:
        print(e)


@client.command(name="servers", help=f"Show where the {botname} is currently been a nuisance")
async def servers(message):
    await message.channel.send(f"Connected on {len(client.guilds)} servers:")
    for guild in client.guilds:
        await message.channel.send(guild.name)


@client.command(name="uptime", help=f"Displays the current uptime of {botname}")
async def uptime(message):
    await message.channel.send(
        f"Current uptime is {humanize.precisedelta(timedelta(seconds=time.monotonic() - start_time))}")


@client.command(name="timezone",
                help=f"Changes the current timezone used by {botname}, format is Country/City i.e Australia/Melbourne")
@client.auto
@commands.is_owner()
async def cmd_tz(message, timezone):
    await message.channel.send(f"Timezone changed to {timezone}")
    update_guild(message.guild.id, timezone)


@cmd_tz.error
async def info_error(message, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await message.channel.send(
            'Timezone missing, please enter one in the format Country/City i.e Australia/Melbourne')

async def main():
    # start the client
    async with client:
        await client.start(api_key)

asyncio.run(main())
