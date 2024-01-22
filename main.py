import discord
from discord.ext import commands
import asyncio
import os
import json

from config.help_config import help_cog
from config.music_config import music_cog

bot = commands.Bot(command_prefix="-", intents=discord.Intents.all())

bot.remove_command('help')

tokenJsonFile = open(os.path.join(os.getcwd(), 'resources\\token.json'))
tokenJson = json.loads(tokenJsonFile.read())

async def main():
    async with bot:
        await bot.add_cog(help_cog(bot))
        await bot.add_cog(music_cog(bot))
        await bot.start(tokenJson["key"])

asyncio.run(main())