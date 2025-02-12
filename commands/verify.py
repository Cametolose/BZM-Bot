import json
import discord
import requests
from . import config
from discord import app_commands
from discord.ext import commands

# Discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Define command function
class VerifyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Verification command
    @app_commands.command(name="verify", description="Type in your Minecraft Name to verify")
    async def verification(self, interaction: discord.Interaction, name: str):

        # Check if the person is already verified
        role = interaction.guild.get_role(config.VERIFY_ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message(
                f"You are already verified.", ephemeral=True)
        else:
            # Create API link
            MinecraftName = name
            responseMojang = requests.get(config.MOJANG_API + MinecraftName)

            # Get UUID
            if "id" in responseMojang.json():
                UUID = responseMojang.json()["id"]
            else:
                await interaction.response.send_message(
                    f"Are you sure that your Minecraft name ``{MinecraftName}`` is correct?", ephemeral=True)
                return

            # Get API data of the player with an API key & the UUID
            PlayerURL = f"https://api.hypixel.net/v2/player?key={config.API_KEY}&uuid={UUID}"

            responseHypixel = requests.get(PlayerURL)
            data = responseHypixel.json()

            # Check if Hypixel account is linked to Discord
            try:
                discordName = data["player"]["socialMedia"]["links"]["DISCORD"]
            except KeyError:
                print(f"Error: Discord not found in API data. URL: {PlayerURL}")
                await interaction.response.send_message(
                    f"Your Hypixel account ``{MinecraftName}`` might not be linked to Discord.", ephemeral=True)
                return

            if discordName == interaction.user.name:
                await interaction.response.send_message(f"Your account got successfully linked to ``{MinecraftName}``", ephemeral=True)

                # Add verified role to the user
                verify_role = interaction.guild.get_role(config.VERIFY_ROLE_ID)
                await interaction.user.add_roles(verify_role)

                # Send the Name and Discord to the name channel
                nameChannel = client.get_channel(config.IGN_CHANNEL)
                if nameChannel:
                    await nameChannel.send(f"**Minecraft:** ``{MinecraftName}``\n**Discord:** {interaction.user.mention}")

                # Save name data to a JSON file
                nameData = (f"{MinecraftName}:{discordName}:{interaction.user.id}")
                with open("NameData.json", "a") as name_json:
                    name_json.write(json.dumps(nameData) + "\n")
            
            # Error if the account is linked to a different Discord
            else:
                await interaction.response.send_message(
                    f"Is ``{MinecraftName}`` really your account? The account is linked to a different Discord.", ephemeral=True)


# Setup-Function
async def setup(bot):
    await bot.add_cog(VerifyCommand(bot))