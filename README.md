# LocalAudioStreamDiscordBot
<string>NOT INTENDED FOR PRODUCTION</strong>
```
python -m pip install discord.py python-dotenv discord.py[voice] requests
```
.env
```
discord_token=TOKEN
modsid=ID
volume=0.2
vlcpassword=test
```
Install FFMPEG as well.

VLC stream command
`:sout=#http{mux=mp3,dst=127.0.0.1:9000/} :no-sout-all :sout-keep`