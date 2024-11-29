import discord
from discord.ext import commands
import json
import os
import random

TOKEN = "MTMwOTA0Mjg4MzUwMzg1MzU3OA.GeIFqW.6nGAtnY7FZ2bB0bbzLHKHtn2xF2yWlHRiS_YUA"

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

#加載授權頻道
with open("channel.json", "r", encoding="utf-8") as f:
    CHANNEL_LIST = json.load(f)

#保存授權頻道
def save_channel(data):
    with open("channel.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

#判斷是否為授權頻道
def channel_check(ctx):
    if ctx.channel.id not in CHANNEL_LIST:
        return False
    return True

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

#系統訊息
SYSMES = {
    "channelWrong":"此指令只能在指定的頻道中使用！",
    "noPet":"你還沒有專屬寵物！使用 `!create [寵物名稱]` 來創建一隻吧！"
}

#status指令的按鈕
class StatusView(discord.ui.View):
    def __init__(self, ctx, pet, user_id, pets):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.pet = pet
        self.user_id = user_id
        self.pets = pets

    async def send_new_status(self, ctx, emoji):
        embed = discord.Embed(
            title=f"{self.pet['name']}       {emoji}",
            color=discord.Color.blue()
        )
        embed.add_field(name="飽食度", value=self.pet['hunger'], inline=True)
        embed.add_field(name="心情值", value=self.pet['mood'], inline=True)
        embed.add_field(name="等級", value=self.pet['level'], inline=True)
        embed.add_field(name="經驗值", value=self.pet['experience'], inline=True)

        view = StatusView(ctx, self.pet, self.user_id, self.pets)
        await ctx.send(embed=embed, view=view)

    @discord.ui.button(label="餵食", style=discord.ButtonStyle.green)
    async def feed_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.pet["hunger"] += 10
        if self.pet["hunger"] > 150:
            self.pet["hunger"] = 150
        save_pets(self.pets)
        if self.pet["hunger"] < 100:
            emoji = Emoji['Full'][str(random.randint(1, 4))]
        elif self.pet["hunger"] < 150:
            emoji = f"{Emoji['Full'][str(random.randint(1, 4))]} 快要炸了~"
        else:
            emoji = Emoji['Explode']
        await self.send_new_status(self.ctx,emoji)

    @discord.ui.button(label="撫摸", style=discord.ButtonStyle.blurple)
    async def pet_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.pet["mood"] += 10
        if self.pet["mood"] > 100:
            self.pet["mood"] = 100
        save_pets(self.pets)
        if self.pet["mood"] < 30:
            emoji = Emoji['Sad'][str(random.randint(1, 4))]
        elif self.pet["mood"] < 70:
            emoji = Emoji['Normal'][str(random.randint(1, 4))]
        else:
            emoji = Emoji['Happy'][str(random.randint(1, 4))]
        await self.send_new_status(self.ctx,emoji)

    @discord.ui.button(label="訓練", style=discord.ButtonStyle.red)
    async def train_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.pet['hunger'] <= 30:
            emoji = Emoji['Hungry'][str(random.randint(1, 4))]
        else:
            exp_gain = random.randint(1, 5) if self.pet['mood'] <= 30 else random.randint(5, 20)
            self.pet['experience'] += exp_gain
            mood_down = random.randint(5, 20)
            self.pet['mood'] = max(0, self.pet['mood'] - mood_down)
            self.pet['hunger'] = max(0, self.pet['hunger'] - 10)
            lvTmp = self.pet['level']
            self.pet = experienceCal(self.pet)
            save_pets(self.pets)
            if self.pet['level'] != lvTmp:
                emoji = Emoji['Train'][str(random.randint(1, 4))] + " " + Emoji['LVup']
            else:
                emoji = Emoji['Train'][str(random.randint(1, 4))]
        await self.send_new_status(self.ctx,emoji)

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
    embed.add_field(name="!helpInfo", value="顯示此指令清單", inline=False)
    embed.add_field(name="!rename [新的名字]", value="重新命名寵物", inline=False)
    embed.add_field(name="!activate", value="在此頻道上開啟寵物功能(僅頻道管理者可用)", inline=False)
    embed.add_field(name="!deactivate", value="在此頻道上關閉寵物功能(僅頻道管理者可用)", inline=False)
    
    await ctx.send(embed=embed)

#在頻道上開啟寵物機器人
@bot.command()
async def activate(ctx):
    # 檢查權限
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send(f"{ctx.author.mention} 你沒有權限執行此指令！")
        return

    if not channel_check(ctx):
        CHANNEL_LIST.append(ctx.channel.id)
        save_channel(CHANNEL_LIST)
        await ctx.send(f"寵物功能已新增至 {ctx.channel.name}")
    else:
        await ctx.send(f"{ctx.channel.name} 已經開啟過寵物功能")

# 在頻道上關閉寵物機器人功能
@bot.command()
async def deactivate(ctx):
    # 檢查權限
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send(f"{ctx.author.mention} 你沒有權限執行此指令！")
        return

    if channel_check(ctx):
        CHANNEL_LIST.remove(ctx.channel.id)
        save_channel(CHANNEL_LIST)
        await ctx.send(f"寵物功能已從 {ctx.channel.name} 關閉")
    else:
        await ctx.send(f"{ctx.channel.name} 未開啟寵物功能")

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
            title=f"{pet['name']}       {hunMood_impact(pet)}"
        )
        embed.add_field(name="飽食度", value=pet['hunger'], inline=True)
        embed.add_field(name="心情值", value=pet['mood'], inline=True)
        embed.add_field(name="等級", value=pet['level'], inline=True)
        embed.add_field(name="經驗值", value=pet['experience'], inline=True)
        view = StatusView(ctx, pet, user_id, pets)
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send(SYSMES["noPet"])

# 啟動 Bot
bot.run(TOKEN)
