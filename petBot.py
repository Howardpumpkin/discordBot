import discord
from discord.ext import commands
import json
import os
import random

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

#加載emoji
def load_emoji():
    with open("emoji.json", "r", encoding="utf-8") as f:
        return json.load(f)
Emoji = load_emoji()

#判斷是否升級
def experienceCal(pet):
    while pet["experience"] >= 100:
        pet["level"] += 1
        pet["experience"] -= 100
    return pet

#判斷心情與飽食的影響程度，回傳表情
def hunMood_impact(pet):
    hunger = pet['hunger']
    mood = pet['mood']

    # 計算飽食和心情的影響程度
    hun_impact = hunger / 150 if hunger >= 100 else (150 - hunger) / 150 if hunger <= 50 else 0
    hun_effect = 1 if hunger >= 100 else 2 if hunger <= 50 else None

    mood_impact = mood / 100 if mood >= 70 else (100 - mood) / 100 if mood <= 30 else 0
    mood_effect = 1 if mood >= 70 else 2 if mood <= 30 else None

    # 判斷主要影響
    if hun_effect and mood_effect:
        if hun_impact > mood_impact:
            effect_type = 'Full' if hun_effect == 1 else 'Hungry'
        else:
            effect_type = 'Happy' if mood_effect == 1 else 'Sad'
    elif hun_effect:
        effect_type = 'Full' if hun_effect == 1 else 'Hungry'
    elif mood_effect:
        effect_type = 'Happy' if mood_effect == 1 else 'Sad'
    else:
        effect_type = 'Normal'

    # 返回隨機表情
    return Emoji[effect_type][str(random.randint(1, 4))]
    

#判斷是否為授權頻道
def channel_check(ctx):
    if ctx.channel.id != CHANNEL_ID:
        return False
    return True

#系統訊息
SYSMES = {
    "channelWrong":"此指令只能在指定的頻道中使用！",
    "noPet":"你還沒有專屬寵物！使用 `!create [寵物名稱]` 來創建一隻吧！"
}

#指令的程式都放在這下面
#指令列表顯示
@bot.command()
async def helpInfo(ctx):
    if not channel_check(ctx):
        await ctx.send(SYSMES["channelWrong"])
        return
    embed = discord.Embed(
        title="指令清單"
    )
    embed.add_field(name="!create [寵物名稱]", value="創建一隻專屬寵物", inline=False)
    embed.add_field(name="!status", value="查看寵物的當前狀態", inline=False)
    embed.add_field(name="!feed", value="餵食你的寵物，增加飽食度(飽食過低無法訓練)", inline=False)
    embed.add_field(name="!pet", value="撫摸你的寵物，增加心情值(心情過低升等效率會下降)", inline=False)
    embed.add_field(name="!helpInfo", value="顯示此指令清單", inline=False)
    embed.add_field(name="!train", value="訓練寵物，增加經驗值(心情和飽食會下降)", inline=False)
    embed.add_field(name="!rename [新的名字]", value="重新命名寵物", inline=False)
    
    await ctx.send(embed=embed)

# 創建專屬寵物
@bot.command()
async def create(ctx, name: str):
    if not channel_check(ctx):
        await ctx.send(SYSMES["channelWrong"])
        return

    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        await ctx.send(f"你已經擁有一隻專屬的寵物了：{pets[user_id]['name']}！")
    else:
        pets[user_id] = {
            "name": name,
            "hunger": 80,
            "mood": 80,
            "level": 1,
            "experience": 0
        }
        save_pets(pets)
        emojCount = random.randint(1,4)
        await ctx.send(f"成功創建了你的專屬寵物：{name}！快來照顧它吧！")
        await ctx.send(f"{Emoji['Hi'][str(emojCount)]}")

#重新命名寵物
@bot.command()
async def rename(ctx, name: str):
    if not channel_check(ctx):
        await ctx.send(SYSMES["channelWrong"])
        return
    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        pet = pets[user_id]
        prevname = pet['name']
        pet['name'] = name
        save_pets(pets)
        await ctx.send(f"{prevname} 已成功改名為: {pet['name']}")
    else:
        await ctx.send(SYSMES["noPet"])
    
# 查看寵物數據
@bot.command()
async def status(ctx):
    if not channel_check(ctx):
        await ctx.send(SYSMES["channelWrong"])
        return

    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        pet = pets[user_id]
        embed = discord.Embed(
        title=f"{pet['name']} (LV.{pet['level']})"
        )
        embed.add_field(name="飽食度", value=pet['hunger'], inline=True)
        embed.add_field(name="心情值", value=pet['mood'], inline=True)
        embed.add_field(name="等級", value=pet['level'], inline=True)
        embed.add_field(name="經驗值", value=pet['experience'], inline=True)
        embed.add_field(name="", value=hunMood_impact(pet), inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send(SYSMES["noPet"])

# 餵食寵物
@bot.command()
async def feed(ctx):
    if not channel_check(ctx):
        await ctx.send(SYSMES["channelWrong"])
        return
    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        pet = pets[user_id]
        pet["hunger"] += 10
        if pet["hunger"] > 150:
            pet["hunger"] = 150 
        save_pets(pets)
        if pet["hunger"] < 100:
            await ctx.send(Emoji['Full'][str(random.randint(1, 4))])
        elif pet["hunger"] < 150:
            await ctx.send(f"{Emoji['Full'][str(random.randint(1, 4))]} 快要炸了~")
        else:
            await ctx.send(Emoji['Explode'])
    else:
        await ctx.send(SYSMES["noPet"])

# 撫摸寵物增加心情值
@bot.command()
async def pet(ctx):
    if not channel_check(ctx):
        await ctx.send(SYSMES["channelWrong"])
        return

    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        pet = pets[user_id]
        pet["mood"] += 10
        if pet["mood"] > 100:
            pet["mood"] = 100
        save_pets(pets)
        await ctx.send(Emoji['Happy'][str(random.randint(1, 4))])
    else:
        await ctx.send(SYSMES["noPet"])

#訓練寵物增加經驗值
@bot.command()
async def train(ctx):
    if not channel_check(ctx):
        await ctx.send(SYSMES["channelWrong"])
        return

    pets = load_pets()
    user_id = str(ctx.author.id)
    if user_id in pets:
        pet = pets[user_id]
        #判斷飽食是否過低
        if pet['hunger'] <= 30:
            await ctx.send(Emoji['Hungry'][str(random.randint(1, 4))])
            return
        # 隨機生成經驗值增加量，降低心情和飽食
        if pet['mood'] <= 30:
            exp_gain = random.randint(1, 5)
        else:
            exp_gain = random.randint(5, 20)
        pet['experience'] += exp_gain
        mood_down = random.randint(5, 20)
        pet['mood'] -= mood_down
        pet['hunger'] -= 10
        lvTmp = pet['level']
        # 檢查是否升級
        pet = experienceCal(pet)
        save_pets(pets)
        await ctx.send(
            f"{Emoji['Train'][str(random.randint(1, 4))]}\n"
            f"經驗值增加了 {exp_gain} 點！"
        )
        if pet['level'] != lvTmp:
            await ctx.send(
            f"{Emoji['LVup']} 升級了！\n"
            )
    else:
        await ctx.send(SYSMES["noPet"])

# 啟動 Bot
bot.run(TOKEN)
