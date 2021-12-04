import sys
import traceback
import discord
from discord import embeds
from discord.ext import commands, tasks
import os
import typing
from discord.ext.commands.core import cooldown
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv


if not os.path.exists('.env'):
    f = open('.env', 'w')
    f.write("discord_token=\n\
        modsid=\n\
        volume=0.5\n\
        vlcpassword=\
            ")
    f.close()
load_dotenv()

DISCORD_TOKEN = os.getenv("discord_token")
MODID = int(os.getenv("modsid"))
VOLUME = float(os.getenv("volume"))
if not VOLUME:
    VOLUME=0.2

def owner_or_role(ctx):
    for item in ctx.author.roles:
        if item.id == MODID:
            return True
    if owner(ctx):
        return True
    return False


async def owner(ctx):
    if ctx.author.id == ctx.guild.owner_id:
        return True
    if await bot.is_owner(ctx.author):
        return True
    return False


intents = discord.Intents.default()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='+!', intents=intents)
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


async def errorOccured(ctx):
    errorEmbed = discord.Embed(title=bot.user.name+" Music Bot")
    errorEmbed.add_field(name="Error",value="Sorry exprenced an error, look at console to see what happened.")
    ctx.send(embed=errorEmbed)

@bot.event
async def on_command_error(ctx, error):
    # This prevents any commands with local handlers being handled here in on_command_error.
    if hasattr(ctx.command, 'on_error'):
        return

    # This prevents any cogs with an overwritten cog_command_error being handled here.
    cog = ctx.cog
    if cog:
        if cog._get_overridden_method(cog.cog_command_error) is not None:
            return

    ignored = (commands.CommandNotFound, )

    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, 'original', error)

    # Anything in ignored will return and prevent anything happening.
    if isinstance(error, ignored):
        return

    if isinstance(error, commands.DisabledCommand):
        await ctx.send(f'{ctx.command} has been disabled.')

    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except discord.HTTPException:
            pass

    # For this error example we check to see where it came from...
    elif isinstance(error, commands.BadArgument):
        if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
            await ctx.send('I could not find that member. Please try again.')
    elif isinstance(error, commands.CommandOnCooldown):
        try:
            await ctx.send(f'With the command {ctx.command} '+str(error))
        except discord.HTTPException:
            pass
    else:
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(
            ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)


@bot.command(name='ping', help='Latency')
async def ping(ctx):
    if not await owner(ctx):
        return
    await ctx.send("Current ping is: {}ms".format(round(bot.latency*1000)))


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not await owner(ctx):
        return
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()
    voice_client = ctx.message.guild.voice_client
    voice_client.stop()
    return


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    if not await owner(ctx):
        return
    if ctx.message.guild.voice_client:
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            voice_client.cleanup()
            return
    else:
        await ctx.send("The bot is not connected to a voice channel.")
        return


@bot.command(name='play', help='Start')
async def play(ctx):
    if not await owner(ctx):
        return
    await join(ctx)
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            voice_channel.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                source="http://127.0.0.1:9000", **FFMPEG_OPTIONS), VOLUME))
        await ctx.send('**Now connected:**)')
    except BaseException as err:
        print(err)
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    if not await owner(ctx):
        return
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

VLCPASSWORD=os.getenv("vlcpassword")
if not VLCPASSWORD:
    print("Missing VLCPAASSOWRD might want to add that...\n Make sure you enabled http in Prefrences (Turn on view all settings on bottom left) -> Main Interface and toggle http. Than go to the drop down of main interface\n\
         and click lua. Under Lua http set your http password there.")

@bot.command(name='playing', help="Current playing song", aliases=["rn", "queue", "song"])
@commands.cooldown(1, 30)
async def playing(ctx):
    status = None
    xmlroot = None
    try:
        status = requests.get(
            "http://localhost:8080/requests/status.xml", auth=("", VLCPASSWORD))
    except Exception as error:
        print(error)
    if (status.status_code == 200):
        xmlroot = ET.fromstring(status.text)
    else:
        await errorOccured(ctx)
        return
    embedmessage = discord.Embed(title=bot.user.name+" Current Playing", type="rich")
    for item in xmlroot.find("information").iter():
        if len(item.attrib) > 0 and item.text != "\n    ":
            #print(item.attrib["name"],item.text)
            embedmessage.add_field(name=item.attrib["name"],value=item.text)
    await ctx.send(embed=embedmessage)


@bot.command(name='volume', help='sets volume of bot', aliases=["vol"], require_var_positional=True)
async def volume(ctx, volume: typing.Union[int, float]):
    if not await owner(ctx):
        return
    """Changes the player's volume"""
    voice_channel = None
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        if(type(volume) == int):
            voice_channel.volume = volume / 100
        else:
            voice_channel.volume = volume
    except:
        pass
    if ctx.voice_client is None:
        return await ctx.send("Not connected to a voice channel.")
    if voice_channel is not None and voice_channel.is_playing():
        if (type(volume) == int):
            ctx.voice_client.source.volume = volume / 100
        else:
            ctx.voice_client.source.volume = volume
    if (type(volume) == float):
        volume = volume * 100
    await ctx.send(f"Changed volume to {volume}%")
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN, bot=True)
