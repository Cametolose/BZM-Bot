import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from typing import Literal, Optional

# Constants
CRIMSONITE_YIELD = 40
DERELICT_ASH_PER_CRAFT = 128
TAX_RATE = 0.98875  # 1.125% tax

class MoltenPowderCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def fetch_bazaar_data() -> Optional[dict]:
        url = 'https://api.hypixel.net/skyblock/bazaar'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return None
                    return await resp.json()
        except Exception:
            return None

    @staticmethod
    def get_prices(data: dict) -> Optional[dict]:
        try:
            return {
                'mycelium_cube': data["products"]["ENCHANTED_MYCELIUM_CUBE"]["quick_status"]["sellPrice"],
                'blaze_rod': data["products"]["ENCHANTED_BLAZE_ROD"]["quick_status"]["sellPrice"],
                'glowstone': data["products"]["ENCHANTED_GLOWSTONE"]["quick_status"]["sellPrice"],
                'whipped_magma_cream': data["products"]["WHIPPED_MAGMA_CREAM"]["quick_status"]["sellPrice"],
                'mutant_nether_wart': data["products"]["MUTANT_NETHER_STALK"]["quick_status"]["sellPrice"],
                'red_sand_cube': data["products"]["ENCHANTED_RED_SAND_CUBE"]["quick_status"]["sellPrice"],
                'derelict_ash': data["products"]["DERELICT_ASHE"]["quick_status"]["sellPrice"],
                'molten_powder_sell': data["products"]["MOLTEN_POWDER"]["quick_status"]["buyPrice"] * TAX_RATE,
            }
        except KeyError:
            return None

    def format_number(self, num: float, exact: bool = False) -> str:
        """
        Formats numbers with k/m/b suffixes or exact with commas
        :param num: Number to format
        :param exact: If True, shows exact value with commas
        """
        num = float(num)
        if exact:
            return f"{num:,.0f}"

        abs_num = abs(num)
        if abs_num >= 1_000_000_000:
            return f"{num/1_000_000_000:.2f}b"
        elif abs_num >= 1_000_000:
            return f"{num/1_000_000:.2f}m"
        elif abs_num >= 10_000:  # Only format 10k+ with suffix
            return f"{num/1_000:.2f}k"
        return f"{int(num):,}"  # Below 10k, show exact with commas


    @staticmethod
    def calculate_prices(prices: dict) -> dict:
        crimsonite_craftprice = (
            prices['mycelium_cube'] +
            prices['red_sand_cube'] +
            4 * prices['blaze_rod'] +
            4 * prices['glowstone'] +
            4 * prices['whipped_magma_cream'] +
            4 * prices['mutant_nether_wart']
        ) / CRIMSONITE_YIELD
        molten_powder_craftprice = prices['derelict_ash'] * DERELICT_ASH_PER_CRAFT + crimsonite_craftprice
        craft_profit = prices['molten_powder_sell'] - molten_powder_craftprice
        return {
            'crimsonite_craftprice': crimsonite_craftprice,
            'molten_powder_craftprice': molten_powder_craftprice,
            'craft_profit': craft_profit
        }

    

    @app_commands.command(name="molten_powder", description="Calculate profit of crafting molten powder")
    @app_commands.describe(
        mode="Calculation mode",
        value="Budget amount or powder amount (depending on mode)"
    )
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="Budget", value="budget"),
            app_commands.Choice(name="Amount", value="amount"),
        ]
    )
    async def molten_powder(
        self,
        interaction: discord.Interaction,
        mode: Literal["budget", "amount"],
        value: app_commands.Range[int, 1]
    ) -> None:
        """
        Calculate molten powder crafting profit
        """
        await interaction.response.defer()
        
        # Get bazaar data
        data = await self.fetch_bazaar_data()
        if not data:
            await interaction.followup.send("❌ Failed to fetch bazaar data", ephemeral=True)
            return
            
        prices = self.get_prices(data)
        if not prices:
            await interaction.followup.send("❌ Missing price data", ephemeral=True)
            return
            
        calc = self.calculate_prices(prices)
        molten_powder_craftprice = calc['molten_powder_craftprice']
        craft_profit = calc['craft_profit']

        # Calculate based on mode
        if mode == "budget":
            budget = value
            max_amount = int(budget // molten_powder_craftprice)
            amount = max_amount - (max_amount % CRIMSONITE_YIELD)
            
            if amount == 0:
                embed = discord.Embed(
                    title="❌ Budget Too Small",
                    description=f"Your budget is not even enough to craft {CRIMSONITE_YIELD} powder!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
        else:  # amount mode
            amount = value
            if amount % CRIMSONITE_YIELD != 0:
                amount = ((amount // CRIMSONITE_YIELD) + 1) * CRIMSONITE_YIELD
            budget = molten_powder_craftprice * amount

        # Calculate results
        total_profit = craft_profit * amount
        total_cost = amount * molten_powder_craftprice
        profit_percentage = (total_profit / total_cost * 100) if total_cost else 0

        # Build embed
        embed = discord.Embed(
            title="Molten Powder Crafting Calculator",
            color=discord.Color.orange()
        )
        
        if mode == "budget":
            embed.add_field(name="💰 Budget", value=f"{self.format_number(budget)} coins", inline=False)
            
        embed.add_field(name=":scales: Amount", value=f"{self.format_number(amount)} powder", inline=False)
        embed.add_field(name="💸 Total Cost", value=f"{self.format_number(total_cost)} coins", inline=False)
        embed.add_field(
            name="📈 Estimated Profit", 
            value=f"{self.format_number(total_profit)} coins ({profit_percentage:.2f}%)", 
            inline=False
        )
        
        # Add footer with credit
        # embed.set_footer(
        #     text="Coded by Cametolose", 
        #     icon_url="https://avatars.githubusercontent.com/u/102823827"
        # )
        embed.url = "https://github.com/cametolose"

        # Materials section
        materials = discord.Embed(
            title="📦 Required Materials",
            color=discord.Color.blue()
        )


        # Add footer with credit
        materials.set_footer(
            text="Coded by Cametolose", 
            icon_url="https://avatars.githubusercontent.com/u/102823827"
        )

        
        materials.add_field(name="<:derelict_ash:1392855294006005781> Derelict Ash", 
                           value=f"{self.format_number(DERELICT_ASH_PER_CRAFT * amount)} ({self.format_number(prices['derelict_ash'] * DERELICT_ASH_PER_CRAFT * amount)} coins)")
        materials.add_field(name="<:Enchanted_Mycelium_Cube:1392855840763019264> Ench Mycelium Cube", 
                           value=f"{self.format_number(amount / CRIMSONITE_YIELD)} ({self.format_number(prices['mycelium_cube'] * amount / CRIMSONITE_YIELD)} coins)")
        materials.add_field(name="<:Enchanted_Blaze_Rod:1392855369361002668> Ench Blaze Rod", 
                           value=f"{self.format_number(4 * amount / CRIMSONITE_YIELD)} ({self.format_number(prices['blaze_rod'] * 4 * amount / CRIMSONITE_YIELD)} coins)")
        materials.add_field(name="<:Enchanted_Glowstone:1392855764632080527> Ench Glowstone", 
                           value=f"{self.format_number(4 * amount / CRIMSONITE_YIELD)} ({self.format_number(prices['glowstone'] * 4 * amount / CRIMSONITE_YIELD)} coins)")
        materials.add_field(name="<:Whipped_Magma_Cream:1392855229871161394> Whipped Magma Cream", 
                           value=f"{self.format_number(4 * amount / CRIMSONITE_YIELD)} ({self.format_number(prices['whipped_magma_cream'] * 4 * amount / CRIMSONITE_YIELD)} coins)")
        materials.add_field(name="<:Mutant_Nether_Wart:1392855201068617818> Mutant Nether Wart", 
                           value=f"{self.format_number(4 * amount / CRIMSONITE_YIELD)} ({self.format_number(prices['mutant_nether_wart'] * 4 * amount / CRIMSONITE_YIELD)} coins)")
        materials.add_field(name="<:Enchanted_Red_Sand_Cube:1392855270555779142> Ench Red Sand Cube", 
                           value=f"{self.format_number(amount / CRIMSONITE_YIELD)} ({self.format_number(prices['red_sand_cube'] * amount / CRIMSONITE_YIELD)} coins)")

        await interaction.followup.send(embeds=[embed, materials])

async def setup(bot: commands.Bot):
    await bot.add_cog(MoltenPowderCommand(bot))
