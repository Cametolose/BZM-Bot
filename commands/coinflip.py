import discord
import random
from discord import app_commands
from discord.ext import commands

# Define command function
class CoinflipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Coinflip command
    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction, amount: int = 1):
        # Defer if user takes high amount of coinflips
        await interaction.response.defer(ephemeral=False)

        # Limit the amount of coinflips to 1 Million
        try:
            if not 1 <= amount <= 1000000:
                raise ValueError("Please enter a number between 1 and 1000000.")
            
            # Define values
            tail = 0
            head = 0
            throws = 0

            # Simulate coinflips
            for i in range(amount):
                value = random.randint(0, 1)
                if value == 0:
                    tail += 1
                    throws += 1
                else:
                    head += 1
                    throws += 1

            # Calculate percentage
            head_percentage = head / amount * 100.0
            tail_percentage = tail / amount * 100.0

        # Error handling
        except ValueError as e:
            await interaction.followup.send(f"**Error**: {e}")
            return

        # Create embed message
        embedMultiple = discord.Embed(title="Coinflip", description=f"{interaction.user} flipped {amount} coins.",
                                    color=0xd4af37)
        embedMultiple.add_field(name="Tails", value=f"{tail} ({tail_percentage:.2f}%)", inline=False)
        embedMultiple.add_field(name="Heads", value=f"{head} ({head_percentage:.2f}%)", inline=False)

        # Decide if the amount of coinflips is above 1 for different embed message
        if amount != 1:
            await interaction.followup.send(embed=embedMultiple)
        else:
            if tail == 1:
                drop = "Tails"
            else:
                drop = "Heads"
            
            # Embed message for 1 Coinflip
            embedOne = discord.Embed(title=f"{interaction.user} flipped a coin and got {drop}", color=0xd4af37)
            await interaction.followup.send(embed=embedOne)


# Setup-Function
async def setup(bot):
    await bot.add_cog(CoinflipCommand(bot))