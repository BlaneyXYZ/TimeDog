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

timezone_dict = {}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    change_time.start()
    await client.change_presence(activity=discord.Activity(type = discord.ActivityType.watching, name = (CONFIG_FILE["now_playing"])))
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
            await guild.me.edit(nick=pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone(timezone_dict.get(guild.id))).strftime('%a - %I:%M %p'))
    except Exception as e:
        print(e)

@client.command()
async def servers(message):
    await message.channel.send(f"Connected on {len(client.guilds)} servers:")
    for guild in client.guilds:
        await message.channel.send(guild.name)


@client.command(name="timezone", help="Changes the current timezone used by the bot, format is Country/City i.e Australia/Melbourne")
@commands.is_owner()
async def cmd_tz(message, timezone):
    await message.channel.send("Timezone changed to {}".format(timezone))
    update_guild(message.guild.id, timezone)


@cmd_tz.error
async def info_error(message, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await message.channel.send(
            'Timezone missing, please enter one in the format Country/City i.e Australia/Melbourne')

client.run(CONFIG_FILE["api_key"])
