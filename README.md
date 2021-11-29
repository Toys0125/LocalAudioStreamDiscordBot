# LocalAudioStreamDiscordBot
<string>NOT INTENDED FOR PRODUCTION</strong>
```
python -m pip install discord.py python-dotenv
```
.env
```
discord_token=TOKEN
modsid=ID
```
Install FFMPEG as well.

VLC stream command
`:sout=#http{mux=mp3,dst=127.0.0.1:9000/} :no-sout-all :sout-keep`