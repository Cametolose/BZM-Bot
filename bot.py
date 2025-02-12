# Imports
import discord
from discord.ext import commands
import os
import importlib
from commands.config import BOT_TOKEN

# Discord intents
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load python files (commands) in sub folder
async def load_commands(path="commands"):
    for root, _, files in os.walk(path):
        for filename in files:
            if filename.endswith(".py") and not filename.startswith("__"):
                # Create a relative and module path
                relative_path = os.path.relpath(root, ".").replace(os.sep, ".")
                module_path = f"{relative_path}.{filename[:-3]}"
                
                module = importlib.import_module(module_path)
                if hasattr(module, "setup"):
                    await module.setup(bot) 

# Load commands on ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await load_commands()
    await bot.tree.sync()   # remove if many restarts are required
    print("Loaded commands!")


# Start bot
bot.run(BOT_TOKEN)
