scord
from discord.ext import commands
import random
import json
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

LEVEL_FILE = "levels.json"

def load_levels():
    if os.path.exists(LEVEL_FILE):
        with open(LEVEL_FILE, "r") as f:
            return json.load(f)
    return {}

def save_levels(data):
    with open(LEVEL_FILE, "w") as f:
        json.dump(data, f)

levels = load_levels()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Καλωσόρισες {member.mention} στο server!")

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Ο/Η {member.name} έφυγε από το server.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()
    if "καλημερα" in content:
        await message.channel.send("Καλημέρα!")
    if "γεια" in content:
        await message.channel.send("Γεια σου!")

    user_id = str(message.author.id)
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}
    levels[user_id]["xp"] += random.randint(5, 15)

    xp_needed = levels[user_id]["level"] * 100
    if levels[user_id]["xp"] >= xp_needed:
        levels[user_id]["xp"] = 0
        levels[user_id]["level"] += 1
        await message.channel.send(f"{message.author.mention} ανέβηκε στο level {levels[user_id]['level']}!")

    save_levels(levels)
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send("Hey there!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def dice(ctx):
    await ctx.send(f"Έριξες: {random.randint(1, 6)}")

@bot.command()
async def eightball(ctx, *, question=None):
    answers = ["Ναι.", "Οχι.", "Ισως.", "Σιγουρα!", "Δεν νομιζω.", "Ρωτα ξανα αργοτερα."]
    await ctx.send(random.choice(answers))

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(member.display_avatar.url)

@bot.command()
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    if user_id in levels:
        await ctx.send(f"{member.mention} ειναι level {levels[user_id]['level']} με {levels[user_id]['xp']} XP.")
    else:
        await ctx.send(f"{member.mention} δεν εχει ακομα level.")

@bot.command()
async def giveaway(ctx, seconds: int, *, prize):
    await ctx.send(f"GIVEAWAY! Επαθλο: {prize}. Γραψε το emoji reaction για να συμμετασχεις! Ληγει σε {seconds} δευτερολεπτα.")
    msg = await ctx.fetch_message(ctx.channel.last_message_id)
    await msg.add_reaction("🎉")
    await asyncio.sleep(seconds)
    msg = await ctx.channel.fetch_message(msg.id)
    users = [user async for user in msg.reactions[0].users() if not user.bot]
    if users:
        winner = random.choice(users)
        await ctx.send(f"Ο νικητης ειναι {winner.mention}! Κερδιζει: {prize}")
    else:
        await ctx.send("Κανεις δεν συμμετειχε στο giveaway.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member} εφυγε απο το server.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member} εγινε ban.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Διαγραφηκαν {amount} μηνυματα.", delete_after=3)

bot.run(os.environ["Discord_Token"])
