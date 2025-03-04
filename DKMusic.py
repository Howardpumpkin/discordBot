import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

# 設置機器人前綴指令
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True  # 確保能讀取訊息內容
bot = commands.Bot(command_prefix="!", intents=intents)

def getKey(keyword): #從Keys文件讀取金鑰或token
    with open('token.txt', 'r') as file:
        key = f"{keyword}:"
        for line in file:
            if key in line:
                pos = line.find(key)
                return line[pos + len(key):].strip()

TOKEN = getKey("DKMusic")

# 全域變量儲存播放狀態
queues = {}

# 音樂播放功能
@bot.command()
async def join(ctx):
    """加入語音頻道"""
    if ctx.author.voice is None:
        await ctx.send("你必須先進入語音頻道！")
        return
    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command()
async def leave(ctx):
    """離開語音頻道"""
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()
    else:
        await ctx.send("機器人不在語音頻道內！")

@bot.command()
async def play(ctx, url: str):
    """播放音樂"""
    # yt-dlp 選項
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,  # 不顯示下載過程訊息
    }

    # 嘗試抓取影片資訊並播放音樂
    try:
        voice_client = ctx.voice_client
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # 不下載，直接串流
            url2 = info['url']
            title = info.get('title', '無標題')  # 確保獲取標題，避免空值

            # 使用 FFmpeg 播放音樂
            source = discord.FFmpegPCMAudio(source=url2)
            voice_client = ctx.voice_client
            try:
                voice_client.play(source, after=lambda e: check_queue(ctx))
            except Exception as e:
                await ctx.send(f"播放时发生错误：{e}")

        await ctx.send(f"正在播放：**{title}**")

    except Exception as e:
        await ctx.send(f"播放失敗：{e}")


def check_queue(ctx):
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        next_song = queues[ctx.guild.id].pop(0)
        ctx.voice_client.play(next_song, after=lambda e: check_queue(ctx))

@bot.command()
async def pause(ctx):
    """暫停播放"""
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("目前沒有音樂正在播放！")

@bot.command()
async def resume(ctx):
    """繼續播放"""
    voice_client = ctx.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("目前音樂已經在播放中！")

@bot.command()
async def stop(ctx):
    """停止播放"""
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("目前沒有音樂正在播放！")

@bot.command()
async def queue(ctx, url: str):
    """添加歌曲到隊列"""
    voice_client = ctx.voice_client
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        source = discord.FFmpegPCMAudio(url2, executable="ffmpeg")

    guild_id = ctx.guild.id
    if guild_id in queues:
        queues[guild_id].append(source)
    else:
        queues[guild_id] = [source]

    await ctx.send("歌曲已添加到播放列表！")

# 啟動機器人
bot.run(TOKEN)
