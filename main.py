import discord
from discord.ext import commands,tasks
import os
from discord.ext.commands.core import check
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("discord_token")
MODID = int(os.getenv("modsid"))


def owner_or_role(ctx):
    for item in ctx.author.roles:
        if item.id == MODID:
            return True
    if ctx.author.id == ctx.guild.owner_id:
        return True
    return False

def owner(ctx):
    if ctx.author.id == ctx.guild.owner_id:
        return True
    return False

intents = discord.Intents.default()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='+!',intents=intents)
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}



@bot.command(name='ping', help='Latency')
async def ping(ctx):
    if not owner(ctx):
        return
    await ctx.send("Current ping is: {}ms".format(round(bot.latency*1000)))

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not owner(ctx):
        return
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    if not owner(ctx):
        return
    if ctx.message.guild.voice_client:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='play', help='Start')
async def play(ctx):
    if not owner(ctx):
        return
    join(ctx)
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            voice_channel.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source="http://127.0.0.1:9000",**FFMPEG_OPTIONS),0.8))
        await ctx.send('**Now connected:**)')
    except BaseException as err:
        print(err)
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    if not owner(ctx):
        return
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='volume', help='sets volume of bot')
async def volume(ctx,volume:int):
    if not owner(ctx):
        return
    """Changes the player's volume"""
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.volume=volume / 100
    except:
        pass
    if ctx.voice_client is None:
        return await ctx.send("Not connected to a voice channel.")

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Changed volume to {volume}%")
if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN,bot=True)