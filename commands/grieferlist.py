import discord
import json
from discord import app_commands
from discord.ext import commands

# Define command function
class GrieferlistCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to see all current griefers in a list
    @app_commands.command(name="grieferlist", description="See the list of all current griefers")
    async def grieferlist(self, interaction: discord.Interaction):
        # Open the grieferlist file and read the names
        with open("grieferlist.json", "r") as file:
            data = json.load(file)

            # Extract the names from the data
            griefer_names = [item.split(":")[0] for item in data]

        # Create and send embed message
        embed = discord.Embed(title="Griefer List", description="\n".join(griefer_names), color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

# Setup-Function
async def setup(bot):
    await bot.add_cog(GrieferlistCommand(bot))
