from DiscordToken import *
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import subprocess

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("The bot is online!")
    try:
        synced = await bot.tree.sync()
        print(synced)
    except Exception as e:
        print(e)
    print("------------------")
    

@bot.tree.command(name='hello', description="Hello heloo!")
async def hello(interaction: discord.Interaction):
    print('[DEBUG] hello\n', interaction)
    await interaction.response.send_message(f"Hello {interaction.user.mention}!")

@bot.tree.command(name='countdown', description="Countdown from 10 to 1")
async def countdown(interaction: discord.Interaction):
    print('[DEBUG] countdown\n', interaction)
    await interaction.response.send_message('Countdown:')
    channel = bot.get_channel(interaction.channel_id)
    for i in range(10, 0, -1):
        await channel.send(str(i))
        await asyncio.sleep(1)
    await channel.send("Boom!")

@bot.tree.command(name='ping', description="Bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(bot.latency)

def get_output_of_main_cpp():
    if os.path.exists("temp/main.cpp"):
        os.system('g++ -o temp/main temp/main.cpp')
    if os.path.exists("temp/main.exe"):
        try:
            p = subprocess.run([os.getcwd() + '\\temp\\main.exe'], timeout=5, capture_output=True, text=True)
            return (0, p.stdout)
        except subprocess.TimeoutExpired:
            return (1, 'TLE!')
    else:
        return (1,'Compile error!')

def cleantemp():
    files = os.listdir('./temp/')
    for file in files:
        file_path = os.path.join('./temp/', file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error removing '{file}': {e}")
    return

@bot.event
async def on_message(message: discord.message):
    if message.author == bot.user:
        return
    print('[DEBUG] on_message\n', message.content)
    message_list = message.content.split('\n')
    PROCESSMAINCPP = 0
    if message_list[0]=='```c++':
        with open('temp/main.cpp', 'w') as output_file:
            output_file.write('\n'.join(message_list[1:len(message_list)-1]))
        PROCESSMAINCPP = 1

    if message.attachments:
        filename = message.attachments[0].filename
        if filename == "main.cpp":
            await message.attachments[0].save(fp=f"temp/{filename}")
            PROCESSMAINCPP = 1

    if PROCESSMAINCPP == 1:
        PROCESSMAINCPP = 0
        out = get_output_of_main_cpp()
        if out[0]!=0:
            await message.channel.send(out[1])
            cleantemp()
            return
        if len(out[1])==0:
            await message.channel.send('The program did not print anything!')
            cleantemp()
            return
        if len(out[1])<=3000:
            await message.channel.send(out[1])
        else:
            with open('temp/output.txt', 'w') as output_file:
                output_file.write(out[1])
            file = discord.File("./temp/output.txt")
            await message.channel.send("Output: ", file=file)
        cleantemp()
    return
            

bot.run(DISCORDTOKEN)