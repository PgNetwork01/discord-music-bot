import os
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variable
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Suppress yt-dlp console output
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # Bind to IPv4 since IPv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    
    # Debugging information
    print(f'Voice state update for {member.name}: {before.channel} -> {after.channel}')
    
    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    if voice_client and voice_client.channel and len(voice_client.channel.members) == 1:
        await voice_client.disconnect()
        print(f'Left {voice_client.channel} because it was empty.')

@bot.tree.command(name='join', description='Joins the voice channel')
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message(f'{interaction.user.name} is not connected to a voice channel')
    else:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f'Joined {channel.name}')

@bot.tree.command(name='leave', description='Leaves the voice channel')
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message('Left the voice channel')
    else:
        await interaction.response.send_message('Not connected to a voice channel')

@bot.tree.command(name='play', description='Plays a song from YouTube')
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message('You are not connected to a voice channel')
        return

    if not interaction.guild.voice_client:
        channel = interaction.user.voice.channel
        await channel.connect()

    await interaction.response.send_message('Processing your request...')

    voice_client = interaction.guild.voice_client
    async with interaction.channel.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
    
    await interaction.followup.send(f'Now playing: {player.title}')

@bot.tree.command(name='pause', description='Pauses the current song')
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("Playback paused")
    else:
        await interaction.response.send_message("No audio is playing")

@bot.tree.command(name='resume', description='Resumes the paused song')
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("Playback resumed")
    else:
        await interaction.response.send_message("Audio is not paused")

@bot.tree.command(name='stop', description='Stops the current song')
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("Playback stopped")
    else:
        await interaction.response.send_message("No audio is playing")

bot.run(DISCORD_BOT_TOKEN)
