import discord
import asyncio
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput, Select

# Define command function
class TicketsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Button callback
    async def button_callback(self, interaction: discord.Interaction):
        # Menu to select tickets
        select = Select(
            placeholder="Choose the title of the ticket",
            options=[
                discord.SelectOption(label="Lootbox", description="Ticket to claim Lootboxes"),
                discord.SelectOption(label="Giveaway", description="Ticket to claim Giveaway wins"),
                discord.SelectOption(label="Support", description="Ticket for regular Support"),
                discord.SelectOption(label="Other", description="Ticket if none of the other options fit in")
            ]
        )

        # Callback for the menu
        async def select_callback(interaction: discord.Interaction):
            selected_option = select.values[0]  # Die gewählte Option
            modal = TicketModal(ticket_title=selected_option)  # Öffne das Modal mit der gewählten Option
            await interaction.response.send_modal(modal)

        select.callback = select_callback

        # Send the menu to choose tickets
        view = View()
        view.add_item(select)
        await interaction.response.send_message("Choose a title for the ticket:", view=view, ephemeral=True)

    # Define the button for creating tickets
    button = Button(label="Create Ticket", style=discord.ButtonStyle.green)
    button.callback = button_callback

    view = View()
    view.add_item(button)

    # Create embed message for support 
    @commands.command()
    async def ticket(self, ctx):
        embed = discord.Embed(title="Support", description="Press this button to create a ticket", color=discord.Color.gold())
        await ctx.send(embed=embed, view=view)

# Modal for user inputs
class TicketModal(Modal):
    def __init__(self, ticket_title: str):
        super().__init__(title="Create Ticket")
        self.ticket_title = ticket_title
        self.description = TextInput(label="Description", style=discord.TextStyle.long, placeholder="Enter more information about your ticket")
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        description = self.description.value
        guild = interaction.guild

        # Create permissions in new channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Create channel
        category = discord.utils.get(guild.categories, name="Tickets") or await guild.create_category("Tickets")
        ticket_channel = await guild.create_text_channel(name=f"{self.ticket_title}-{interaction.user.name}", category=category, overwrites=overwrites)

        # Button to close the ticket
        close_button = Button(label="Close Ticket", style=discord.ButtonStyle.red)

        # Define button to close the ticket
        async def close_button_callback(interaction: discord.Interaction):
            if interaction.channel.id == ticket_channel.id:
                await interaction.response.send_message("Ticket has been closed.")
                await asyncio.sleep(1)  # Wait 1s for the user to read the message
                await ticket_channel.delete()
            else:
                await interaction.response.send_message("This ticket does not exist.", ephemeral=True)

        close_button.callback = close_button_callback
        view = View()
        view.add_item(close_button)

        # Send message in ticket
        await ticket_channel.send(f"**Ticket created by {interaction.user.mention}**\n\n"
                                  f"**Title:** {self.ticket_title}\n"
                                  f"**Description:** {description}",
                                  view=view)

        await interaction.response.send_message(f"Your ticket was created: {ticket_channel.mention}", ephemeral=True)

# Setup function to add the Cog
async def setup(bot):
    await bot.add_cog(TicketsCommand(bot))
