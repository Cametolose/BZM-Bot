import discord
import json
import requests
from . import config
from discord import app_commands
from discord.ext import commands


# Function to load grieferlist
def load_player_names():
    try:
        with open("grieferlist.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save grieferlist
def save_player_names(player_names):
    with open("grieferlist.json", "w") as file:
        json.dump(player_names, file)

staff_role_id = config.STAFF_ROLE_ID

# Define command function
class GrieferCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Griefer commands
    @app_commands.command(name="griefer", description="Check status of griefers")
    async def griefer(self, interaction: discord.Interaction, add: str = None, remove: str = None):
        # Only staff is allowed to add/remove griefer from the list
        staff_role = discord.utils.get(interaction.guild.roles, id=staff_role_id)

        # Add griefer to the list
        if add is not None:
            if staff_role in interaction.user.roles:

                # Find UUID in mojang API
                response_add = requests.get(config.MOJANG_API + add)

                if response_add.status_code == 200:
                    player_names = load_player_names()
                    uuid = response_add.json()["id"]

                    if not isinstance(player_names, list):
                        player_names = []  # Ensure player_names is a list

                    # Only add if the name doesn't exist yet
                    if add not in player_names:
                        player_names.append(f"{add}:{uuid}")
                        save_player_names(player_names)

                        # Responses based on errors, unallowed usage or success
                        await interaction.response.send_message(f"**{add}** got added to the griefer list")
                    else:
                        await interaction.response.send_message(f"**{add}** is already in the griefer list")
                else:
                    await interaction.response.send_message(f"**{add}** isn't an existing Minecraft name")
            else:
                await interaction.response.send_message(f"Only staff is allowed to use this command!", ephemeral=True)

        # Remove griefer from the list
        elif remove is not None:
            if staff_role in interaction.user.roles:
                player_names = load_player_names()

                remove_list = [player_name.split(":", 1)[0] for player_name in player_names]

                # Remove the name from the list
                if remove in remove_list:
                    index_to_remove = remove_list.index(remove)
                    player_names.pop(index_to_remove)
                    save_player_names(player_names)

                    # Responses based on errors, unallowed usage or success
                    await interaction.response.send_message(f"**{remove}** has been removed from the griefer list")
                else:
                    await interaction.response.send_message(f"**{remove}** is not in the griefer list")
            else:
                await interaction.response.send_message(f"Only staff is allowed to use this command!", ephemeral=True)

        # Check status of griefers
        else:
            #await interaction.response.send_message(f"This command is down for now!")
            await interaction.response.defer(thinking=True)
            names = load_player_names()

            # Make a list for the griefer
            griefers = []
            online_griefers = 0
            offline_griefers = 0

            # Go through each name in the list
            for name in names:
                player_name, uuid = name.rsplit(":", 1)

                # Get the link for the API
                response_status = requests.get(f"{config.HYPIXEL_STATUS_URL}?key={config.API_KEY}&uuid={uuid}")
                data = response_status.json()

                # Get the status of the player
                if data["success"]:
                    online = data["session"].get("online", False) # Default to False if "online" is not found
                    if online == True:
                        online_griefers += 1
                    else:
                        offline_griefers += 1
                    griefers.append((player_name, online))

                else:
                    griefers.append((player_name, "error"))
                    print(f"{config.API_KEY}?key={config.API_KEY}&uuid={uuid}")

            # Sort griefer list by online first
            griefers.sort(key=lambda x: x[1] == "online", reverse=True)  # online first

            # create embed message
            embed = discord.Embed(title="Griefer List", description=f"**Online Griefers: ({online_griefers}/{online_griefers+offline_griefers})**", color=discord.Color.red())

            # Add griefer
            for player_name, online in griefers:
                if online == True:
                    embed.add_field(name = f"{player_name} :green_circle:", value= "", inline=False)

                elif online == "error":
                    embed.add_field(name=player_name, value="Error retrieving status", inline=False)


            if any(status == True or status == "error" for _, status in griefers):
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(content="No griefers found in the list.")

# Setup-Function
async def setup(bot):
    await bot.add_cog(GrieferCommand(bot))