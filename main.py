import discord
from discord.ext import commands
import os
import json
import random
from datetime import datetime, timedelta

XP_RANGE = (5, 15)
XP_COOLDOWN = 10
DATA_FILE = "levels.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

cooldowns = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    data = load_data()
    user_id = str(message.author.id)

    if user_id not in data:
        data[user_id] = {"xp": 0, "level": 1}

    now = datetime.utcnow()

    if user_id in cooldowns and now < cooldowns[user_id]:
        await bot.process_commands(message)
        return

    cooldowns[user_id] = now + timedelta(seconds=XP_COOLDOWN)

    xp_gain = random.randint(*XP_RANGE)
    data[user_id]["xp"] += xp_gain

    level = data[user_id]["level"]
    xp_needed = 100 * level

    if data[user_id]["xp"] >= xp_needed:
        data[user_id]["level"] += 1
        data[user_id]["xp"] -= xp_needed
        await message.channel.send(
            f"🎉 {message.author.mention} leveled up to Level {data[user_id]['level']}!"
        )

    save_data(data)
    await bot.process_commands(message)

@bot.command()
async def rank(ctx):
    data = load_data()
    user_id = str(ctx.author.id)

    if user_id not in data:
        await ctx.send("You have no XP yet.")
        return

    xp = data[user_id]["xp"]
    level = data[user_id]["level"]
    xp_needed = 100 * level

    await ctx.send(f"Level: {level} | XP: {xp}/{xp_needed}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(os.getenv("TOKEN"))
