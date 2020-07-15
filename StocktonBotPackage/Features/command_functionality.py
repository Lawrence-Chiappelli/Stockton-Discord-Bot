# Abstract the command content away from bot.py and keep it clean.

from StocktonBotPackage.DevUtilities import configparser, validators
from StocktonBotPackage.Features import gaming_lab_api
import threading
import discord
import asyncio

# -----------------------------------------+
config = configparser.get_parsed_config()  #
# -----------------------------------------+


class Scraper:

    def __init__(self, scraping):
        self.is_scraping = scraping


# ------------------------+
scraper = Scraper(False)  #
# ------------------------+
# Will help prevent multiple instances of scrapers.
# Only one should be allowed at any given time.


async def scrape_website(client):

    bot_channel = discord.utils.get(client.get_all_channels(), name=config['channel']['botcommands'])
    if scraper.is_scraping:
        await bot_channel.send("Aborting - There is already one running instance of the web scraper.")
        return

    while True:
        if not await validators.machine_availabilty_embed_exists(client):
            await bot_channel.send(f"Machine availability panels must first exist in the channel `#{config['channel']['gamelabavailability']}`! You can add these panels by entering `!machineavailability` inside the channel.")
            return

        scraper.is_scraping = True
        await bot_channel.send(f"Checking for machine availability...")
        try:
            pc_statuses = gaming_lab_api.get_pc_availability()
        except Exception as e:
            print(f"Unable to scrape data!:\n{e}")
            await bot_channel.send(f"Exception caught scraping data:\n{e}")
            scraper.is_scraping = False
            return

        await bot_channel.send(f"Updating the embed with the following statuses:\n{pc_statuses}")
        await update_machine_availability_embed(client, pc_statuses)
        await asyncio.sleep(5)


async def update_machine_availability_embed(guild, pc_statuses):

    game_lab_channel_name = config['channel']['gamelabavailability']
    channel = discord.utils.get(guild.get_all_channels(), name=game_lab_channel_name)
    messages = [msg async for msg in channel.history(limit=int(config['lab']['num_rooms']))]

    for msg in messages:  # There's only 2 of these embeds, meaning the worst time complexity is irrelevant
        embed = msg.embeds[0]
        for i, status in enumerate(pc_statuses.values()):

            if status.pop() == "available":
                value = config['lab-icons']['available']
            else:
                value = config['lab-icons']['inuse']

            embed.set_field_at(index=i, name=f"{i+1} 🖥️", value=value, inline=True)
        await msg.edit(embed=embed)


async def send_authentication_embed(context):
    await context.message.delete()
    role = discord.utils.get(context.message.guild.roles, name="Auth-ed")

    embed = discord.Embed(title="React to the below checkmark to access the full Stockton Esports Discord!",
                          description="`Disclaimer`: By reacting to the below checkmark, you understand the aforementioned rules and agree to be kind and amenable with the community here. Once you have gained access to the server, carefully browse the server directory to get where you need to be. ",
                          color=0x73ff61)
    embed.set_author(name="Confirmation")
    embed.set_thumbnail(
        url="https://images.vexels.com/media/users/3/157931/isolated/preview/604a0cadf94914c7ee6c6e552e9b4487-curved-check-mark-circle-icon-by-vexels.png")
    embed.add_field(name="You will receive this role:", value=role.mention, inline=True)
    embed.add_field(name="Users Authorized:", value=str(get_num_members_with_role(role)), inline=True)
    embed.set_footer(text="Stockton Discord Bot developed by ChocolateThunder#5292 • Lawrence Chiappelli.")
    await context.message.channel.send(embed=embed)
    last_message = [msg async for msg in context.message.channel.history(limit=1)].pop()
    await last_message.add_reaction("✅")

    return None


async def send_machine_availability_embed(context):

    await context.message.delete()

    embed = discord.Embed(title="Room 1", description="🔵 Blue room 🔵", color=0x5294ff)
    embed.set_author(name="💻 Gaming Lab Machine Availability", url=config['website']['url'])
    embed.set_thumbnail(url="https://i.imgur.com/eVqogAY.jpg")

    embed.add_field(name="1 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="2 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="3 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="4 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="5 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="6 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="7 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="8 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="9 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="10 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="11 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="12 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="13 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="14 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.add_field(name="15 🖥️", value=config['lab-icons']['waiting'], inline=True)
    embed.set_footer(text=f"Available {config['lab-icons']['available']} | In-Use {config['lab-icons']['inuse']} | Error {config['lab-icons']['waiting']}\n\nStockton Discord Bot developed by ChocolateThunder#5292 • Lawrence Chiappelli.")
    await context.send(embed=embed)

    """
    Uncomment the following when the gold room
    is added on website
    """

    # embed = discord.Embed(title="Room 2", description="🟡 Gold room 🟡", color=0xf1ff33)
    # embed.set_author(name="💻 Gaming Lab Machine Availability")
    # embed.set_thumbnail(url="https://i.imgur.com/eVqogAY.jpg")
    # embed.add_field(name="1 🖥️", value="✅", inline=True)
    # embed.add_field(name="2 🖥️", value="✅", inline=True)
    # embed.add_field(name="3 🖥️", value="✅", inline=True)
    # embed.add_field(name="4 🖥️", value="✅", inline=True)
    # embed.add_field(name="5 🖥️", value="✅", inline=True)
    # embed.add_field(name="6 🖥️", value="✅", inline=True)
    # embed.add_field(name="7 🖥️", value="✅", inline=True)
    # embed.add_field(name="8 🖥️", value="✅", inline=True)
    # embed.add_field(name="9 🖥️", value="✅", inline=True)
    # embed.add_field(name="10 🖥️", value="✅", inline=True)
    # embed.add_field(name="11 🖥️", value="✅", inline=True)
    # embed.add_field(name="12 🖥️", value="✅", inline=True)
    # embed.add_field(name="13 🖥️", value="✅", inline=True)
    # embed.add_field(name="14 🖥️", value="✅", inline=True)
    # embed.add_field(name="15 🖥️", value="✅", inline=True)
    # embed.set_footer(text="Available ✅ | In-Use ❌")
    # await context.send(embed=embed)

    return None


async def execute_bot_reaction_directory(emoji, channel, member):

    """
    :param emoji: the emoji being reacted
    :param channel: the channel with reaction
    :param member: the user to perform functionality to, if applicable
    :return: nothing
    """

    auth_emoji = config['emoji']['authed']
    auth_channel = config['channel']['landing']

    if str(emoji) == auth_emoji and str(channel) == auth_channel:
        auth_role = discord.utils.get(member.guild.roles, name=config['role']['authed'])
        await member.add_roles(auth_role)
        message = [msg async for msg in channel.history(limit=1)].pop()
        embed = message.embeds[0]
        embed.set_field_at(index=1, name=f"Users Authorized:", value=get_num_members_with_role(auth_role), inline=True)
        await message.edit(embed=embed)

    return None


def get_num_members_with_role(role):

    num_members_with_role = 0
    for member in role.guild.members:
        if role in member.roles and not member.bot:
            num_members_with_role += 1

    return num_members_with_role
