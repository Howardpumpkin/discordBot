import discord
from discord import Intents
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import asyncio
from googletrans import Translator

translator = Translator()

TOKEN = "MTI5NjMwMzgwODI5NjY0ODcyNQ.GxMRBb.8asVs3G2p1F1t-yN97LHWVxoB_U6BVckXWU00E"  # 记得更换为你的实际TOKEN
CHANNEL_ID = 814846083628269612

intents = Intents.default()
intents.message_content = True
intents.guilds = True  
client = discord.Client(intents=intents)

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

@client.event
async def fetch_and_send_perks(channel):
    url = "https://nightlight.gg/shrine"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        shrine_div = soup.find('div', id='shrine')

        if shrine_div:
            perks = shrine_div.find_all('div', class_='perk')
            for perk in perks:
                name = perk.find('a').text
                img_src = perk.find('img')['src']
                img_response = requests.get(img_src)

                if img_response.status_code == 200:
                    img_data = Image.open(BytesIO(img_response.content))
                    img_data = img_data.resize((100, 100))
                    img_buffer = BytesIO()
                    img_data.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    await channel.send(f'**{name}**', file=discord.File(img_buffer, filename='perk_image.png'))
                    perk_detail_URL = f'https://nightlight.gg/perks/{name.replace(" ", "_")}'
                    perk_d_response = requests.get(perk_detail_URL, headers=headers)
                    if perk_d_response.status_code == 200:
                        perk_d_soup = BeautifulSoup(perk_d_response.text, 'html.parser')
                        perk_d_div = perk_d_soup.find('div', role='tabpanel')
                        if perk_d_div:
                            text_content = perk_d_div.get_text(separator=" ").strip().replace('\n', ' ')
                            text_content = wrap_text(text_content, 500)
                            translated_text = translator.translate(text_content, dest='zh-tw').text
                            await channel.send(translated_text)

                await asyncio.sleep(1)
        else:
            await channel.send("Cannot find div")
    else:
        await channel.send(f"Error code: {response.status_code}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    await fetch_and_send_perks(channel)

client.run(TOKEN)