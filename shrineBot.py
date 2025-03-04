import discord
import aiohttp
from discord.ext import commands
from bs4 import BeautifulSoup
from googletrans import Translator
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import asyncio
import os

translator = Translator()

def getKey(keyword): #從Keys文件讀取金鑰或token
    with open('token.txt', 'r') as file:
        key = f"{keyword}:"
        for line in file:
            if key in line:
                pos = line.find(key)
                return line[pos + len(key):].strip()

TOKEN = getKey("shrineBot")
CHANNEL_ID = 701445252384424051

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

message = []
perkImg = []
perkNames = []

def wrap_text(text, max_length):
    words = text.split(' ')
    wrapped_text = ''
    current_line_length = 0

    for word in words:
        if current_line_length + len(word) + 1 > max_length:
            wrapped_text += '\n'
            current_line_length = 0
        else:
            if current_line_length > 0:
                wrapped_text += ' '
            wrapped_text += word
            current_line_length += len(word) + 1

    return wrapped_text

async def fetch_and_send_perks(channel):
    url = "https://nightlight.gg/shrine"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                shrine_div = soup.find('div', id='shrine')

                if shrine_div:
                    perks = shrine_div.find_all('div', class_='perk')
                    for perk in perks:
                        name = perk.find('a').text
                        img_src = perk.find('img')['src']

                        async with session.get(img_src) as img_response:
                            if img_response.status == 200:
                                img_data = Image.open(BytesIO(await img_response.read()))
                                img_data = img_data.resize((100, 100))
                                img_buffer = BytesIO()
                                img_data.save(img_buffer, format='PNG')
                                img_buffer.seek(0)

                                # 将图片数据和名称存入列表
                                perkImg.append(img_buffer)
                                perkNames.append(name)  # 存储图片名称

                                perk_detail_URL = f'https://nightlight.gg/perks/{name.replace(" ", "_")}'
                                async with session.get(perk_detail_URL, headers=headers) as perk_d_response:
                                    if perk_d_response.status == 200:
                                        perk_d_soup = BeautifulSoup(await perk_d_response.text(), 'html.parser')
                                        perk_d_div = perk_d_soup.find('div', role='tabpanel')
                                        if perk_d_div:
                                            text_content = perk_d_div.get_text(separator=" ").strip().replace('\n', ' ')
                                            text_content = wrap_text(text_content, 500)
                                            translated_text = translator.translate(text_content, dest='zh-tw').text
                                            message.append(translated_text)  # 存储图片描述
                        await asyncio.sleep(0.1)

                    # 发送所有消息、图片名称和图片
                    for i in range(len(message)):
                        await channel.send(content=f'**{perkNames[i]}**', file=discord.File(perkImg[i], filename=f'image_{i+1}.png'))
                        await channel.send(content=message[i]) 
                    await bot.close()
                else:
                    await channel.send("Cannot find div")
            else:
                await channel.send(f"Error code: {response.status}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    await fetch_and_send_perks(channel)

bot.run(TOKEN)