import discord
import config
from discord import app_commands
from discord.ext import commands

# Define command function
class LoadNamesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 
    @app_commands.command(name="rollback_igns", description="Role names back into the channel")
    async def load_names(self, interaction: discord.Interaction):
        number = 0
        if interaction.user.id == config.OWNER_ID:      # Only owner is allowed to use command
            await interaction.response.defer(thinking=True, ephemeral=False)
    
            messages = []

            # Strip for Minecraft & Discord Name & ID
            with open("NameData.json", "r") as file:
                lines = file.readlines()
                for line in lines:
                    parts = line.strip().split(":")
                    if len(parts) == 3:
                        minecraft_name = parts[0].strip('"')
                        discord_name = parts[1].strip('"')
                        id = parts[2].strip('"')

                        # Create message
                        message = f"**Minecraft:** ``{minecraft_name}``\n**Discord:** <@{id}>"
                        messages.append(message)
    
                        print(minecraft_name, discord_name, number)
    

            await interaction.followup.send("rollback", ephemeral=True)

            # Send all the messages into the channel
            for message in messages:
                await interaction.followup.send(message)
                number += 1
                print (number)
    
            await interaction.followup.send("Finished", ephemeral=True)

# Setup-Function
async def setup(bot):
    await bot.add_cog(LoadNamesCommand(bot))