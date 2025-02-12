import discord
import config
from discord import app_commands
from discord.ext import commands

# Discord
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Define command function
class LoadRolesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to load/rollback roles of the verified user
    @app_commands.command(name="rollback_roles", description="Roll verify role back")

    async def load_roles (self, interaction=discord.Interaction):
        if interaction.user.id == config.OWNER_ID:     # Only owner is allowed to use command
            await interaction.response.defer(thinking=True, ephemeral=True)
            guild = client.guilds[0]
            Verified = guild.get_role(config.VERIFY_ROLE_ID)

            # Extract for names in the NameData
            with open("NameData.json", "r") as file:
                lines = file.readlines()
                for line in lines:
                    parts = line.strip().split(":")
                    if len(parts) == 3:
                        id = parts[2].strip('"')

                        member = guild.get_member(int(id))
                        if member is not None:      # Skip if member is not found
                            await member.add_roles(Verified)
                            print(f"Assigned role to {member.name} with ID {id}")

            await interaction.followup.send("Finished", ephemeral=True)


# Setup-Function
async def setup(bot):
    await bot.add_cog(LoadRolesCommand(bot))