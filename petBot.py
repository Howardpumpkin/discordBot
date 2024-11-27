import discord
from discord.ext import commands
import json
import os

TOKEN = "MTMwOTA0Mjg4MzUwMzg1MzU3OA.GeIFqW.6nGAtnY7FZ2bB0bbzLHKHtn2xF2yWlHRiS_YUA"
CHANNEL_ID = 1309012372756631584

# Bot 初始化
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 檢查檔案是否存在
if not os.path.exists("pets.json"):
    with open("pets.json", "w", encoding="utf-8") as f:
        json.dump({}, f)

# 加載寵物資料
def load_pets():
    with open("pets.json", "r", encoding="utf-8") as f:
        return json.load(f)

# 保存寵物資料
def save_pets(data):
    with open("pets.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

#判斷是否升級
def experienceCal(pet):
    while pet["experience"] >= 100:
        pet["level"] += 1
        pet["experience"] -= 100
    return pet

#判斷是否為授權頻道
def channel_check(ctx):
    if ctx.channel.id != CHANNEL_ID:
        return False
    return True

# 創建專屬寵物
@bot.command()
async def create(ctx, name: str):
    if not channel_check(ctx):
        await ctx.send(f"{ctx.author.mention} 此指令只能在指定的頻道中使用！")
        return

    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        await ctx.send(f"{ctx.author.mention} 你已經擁有一隻專屬的寵物了：{pets[user_id]['name']}！")
    else:
        pets[user_id] = {
            "name": name,
            "hunger": 80,
            "mood": 80,
            "level": 1,
            "experience": 0
        }
        save_pets(pets)
        await ctx.send(f"{ctx.author.mention} 成功創建了你的專屬寵物：{name}！快來照顧它吧！")

# 查看寵物狀態
@bot.command()
async def status(ctx):
    if not channel_check(ctx):
        await ctx.send(f"{ctx.author.mention} 此指令只能在指定的頻道中使用！")
        return

    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        pet = pets[user_id]
        await ctx.send(
            f"{ctx.author.mention} {pet['name']}狀態：\n"
            f"飢餓值：{pet['hunger']}\n"
            f"心情值：{pet['mood']}\n"
            f"等級：{pet['level']}\n"
            f"經驗值：{pet['experience']}"
        )
    else:
        await ctx.send(f"{ctx.author.mention} 你還沒有專屬寵物！使用 `!create [寵物名稱]` 來創建一隻吧！")

# 餵食寵物
@bot.command()
async def feed(ctx):
    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        pet = pets[user_id]
        pet["hunger"] += 10
        if pet["hunger"] > 150:
            pet["hunger"] = 150 
        save_pets(pets)
        if pet["hunger"] < 100:
            await ctx.send(f"{ctx.author.mention} 你餵食了 {pet['name']}，飢餓值增加了！")
        elif pet["hunger"] < 150:
            await ctx.send(f"{ctx.author.mention} {pet['name']} 有點太飽了")
        elif pet["hunger"] == 150:
            await ctx.send(f"{ctx.author.mention} {pet['name']} 再吃就要炸了！")
    else:
        await ctx.send(f"{ctx.author.mention} 你還沒有專屬寵物！使用 /create [寵物名稱] 來創建一隻吧！")

# 撫摸寵物增加心情值
@bot.command()
async def pet(ctx):
    if not channel_check(ctx):
        await ctx.send(f"{ctx.author.mention} 此指令只能在指定的頻道中使用！")
        return

    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        pet = pets[user_id]
        pet["mood"] += 10
        if pet["mood"] > 100:
            pet["mood"] = 100
        save_pets(pets)
        await ctx.send(f"{ctx.author.mention} 你撫摸了 {pet['name']}，{pet['name']} 覺得開心！")
    else:
        await ctx.send(f"{ctx.author.mention} 你還沒有專屬寵物！使用 `!create [寵物名稱]` 來創建一隻吧！")

# 啟動 Bot
bot.run(TOKEN)
