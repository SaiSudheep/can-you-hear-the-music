import discord
from discord.ext import commands

class help_cog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

        self.help_message = """
```

Basic commands:
-play   -> Plays the selected song from Youtube
-pause  -> Pauses the playing song
-resume -> Resumes the paused song
-queue  -> Displays the music queue
-skip   -> Skips the current song
-clear  -> Clears the queue
-leave  -> Disconnects the bot from the voice channel

Are there any more commands? Find out! \N{grinning face with smiling eyes}
```
"""

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game("music | -help"))

    @commands.command(name="help", aliases=["HELP", "Help", "Help!", "HELP!"], help="Displays basic commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)