import discord
import asyncio

from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL

class music_cog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

        # Track play and pause
        self.is_playing = False
        self.is_paused = False

        # Track song, song quality, and queue
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

        # Track bot in voice channel
        self.vc = None

    # Search the song on Youtube
    def search_yt(self, name):
        # URL
        if name.startswith("https://"):
            title = self.ytdl.extract_info(name, download=False)["title"]
            return {'source': name, 'title': title}
        
        # Song name
        else:
            song = VideosSearch(name, limit=1, region='IN')
            return {'source': song.result()["result"][0]["link"], 'title': song.result()["result"][0]["title"]}
        
    # Join voice channel and play song
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            song_url = self.music_queue[0][0]['source']
            
            # Connect to voice channel
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc == None:
                    await ctx.send("```Unable to connect to voice channel````")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            # Pop
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(song_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # Play next song in queue
    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # Get url of first song and pop it from queue
            song_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(song_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # Command: Play
    @commands.command(name="play", aliases=["p"], help="Plays the selected song from Youtube")
    async def play(self, ctx, *args):
        # Get song name
        query = " ".join(args)

        # Check if user is in voice channel
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        
        # Resume if song is paused
        if self.is_paused:
            self.vc.resume()
            self.is_paused = False
            self.is_playing = True
        else:

            # Search and play song
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("```Unable to play the song!```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue) + 2} - '{song['title']}'** added to the queue")
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")
                self.music_queue.append([song, voice_channel])
                if self.is_playing == False:
                    await self.play_music(ctx)

    # Command: Pause
    @commands.command(name="pause", aliases=["stop"], help="Pauses the playing song")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.vc.pause()
            self.is_playing = False
            self.is_paused = True

    # Command: Resume
    @commands.command(name="resume", aliases=["r"], help="Resumes the paused song")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.vc.resume()
            self.is_paused = False
            self.is_playing = True

    # Command: Skip
    @commands.command(name="skip", aliases=["s"], help="Skips the current song")
    async def skip(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.play_music(ctx)

    # Command: Queue
    @commands.command(name="queue", aliases=["q"], help="Displays the music queue")
    async def queue(self, ctx, *args):
        current_queue = ""
        for i in range(1, len(self.music_queue)):
            current_queue += f"#{i+1} - " + self.music_queue[i][0]['title'] + "\n"

        if current_queue == "":
            await ctx.send("```Your music queue is empty!```")
        else:
            await ctx.send(f"```Queue:\n{current_queue}```")

    # Command: Clear
    @commands.command(name="clear", aliases=["c"], help="Clears the queue")
    async def clear(self, ctx, *args):
        if len(self.music_queue) == 0:
            await ctx.send("```Your music queue is empty!```")
        else:
            await ctx.send("```Your music queue has been cleared!```")

    # Command: Leave
    @commands.command(name="leave", aliases=["l", "disconnect", "d"], help="Disconnects the bot from the voice channel")
    async def leave(self, ctx, *args):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    # Command: Kick
    @commands.command(name="kick", aliases=["k"], help="Kicks the bot from the voice channel")
    async def kick(self, ctx, *args):
        self.is_playing = False
        self.is_paused = False
        await ctx.send("```OUCH!!```")
        await self.vc.disconnect()

    # Command: Connect
    @commands.command(name="connect", aliases=["join"], help="Connects the bot to the voice channel")
    async def connect(self, ctx):
        # Check if user is in voice channel
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        
        # Connect to voice channel
        if self.vc == None:
            self.vc = await voice_channel.connect()
        