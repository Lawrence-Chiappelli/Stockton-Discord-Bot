# Abstract the command content away from bot.py and keep it clean.

from StocktonBotPackage.DevUtilities import configparser, validators, gaminglabAPI, gsheetsAPI
from datetime import datetime
import discord
import asyncio
import re

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


async def force_off(client):

    bot_commands_channel_name = gsheetsAPI.get_bot_commands_channel_name()
    bot_channel = discord.utils.get(client.get_all_channels(), name=bot_commands_channel_name)

    try:
        scraper.is_scraping = False
        await bot_channel.send("Web scraper successfully turned off!")
    except Exception as e:
        print(f"Unable to force off!")
        await bot_channel.send(f"Exception caught tyring to turn off webscraper:\n\n{e}")


async def scrape_website(client):

    """
    :param client: client bot is connected to
    :return: only if there's an issue
    Type '!scrape' to restart the scraping process.
    """

    # TODO: Pull channel names from gsheets config

    try:
        bot_commands_channel_name = gsheetsAPI.get_bot_commands_channel_name()
    except (NameError, Exception) as e:

        """
        Generally speaking, I'd like to use the channel name from
        Google sheets, but in the case it's down, it's critical
        that we look for a default name.
        """

        print(f"USING DEFAULT GAME LAB CHANNEL! Error:\n{e}")
        bot_commands_channel_name = config['channel']['botcommands']
    bot_channel = discord.utils.get(client.get_all_channels(), name=bot_commands_channel_name)

    if scraper.is_scraping:
        await bot_channel.send("Aborting - There is already one running instance of the web scraper.")
        return

    while True:

        if not await validators.machine_availabilty_embed_exists(client):
            await bot_channel.send(f"Machine availability panels must first exist in the channel `#{bot_commands_channel_name}`! You can add these panels by entering `!gamelab` inside the channel, then start auto-updating PC availability with `!scrape`.")
            scraper.is_scraping = False
            return

        scraper.is_scraping = True
        print(f"Checking for machine availability...")
        try:
            pc_statuses = await gaminglabAPI.get_pc_availability()
        except Exception as e:
            print(f"Unable to scrape data!:\n{e}")
            await bot_channel.send(f"Exception caught scraping data:\n{e}\n\nTrying again in `25` seconds")
            await asyncio.sleep(25)
            continue

        print(f"Updating the embed with the following statuses:\n{pc_statuses}")
        await update_machine_availability_embed(client, pc_statuses)
        print(F"Trying again in 25 seconds")
        await asyncio.sleep(25)


async def update_machine_availability_embed(guild, pc_statuses):

    """
    :param guild: A guild object, responsible for outputting updates
    :param pc_statuses: A list, grabbed from gaminglabAPI.get_pc_availability()
    :return:
    """

    game_lab_channel_name = gsheetsAPI.get_game_lab_channel_name()
    channel = discord.utils.get(guild.get_all_channels(), name=game_lab_channel_name)
    messages = [msg async for msg in channel.history(limit=int(config['lab']['num_rooms']))]

    reservations_sheet = gsheetsAPI.get_sheet_blue_room_reservations()  # TODO: Gold room support
    reservations = reservations_sheet.col_values(2)
    description = reservations_sheet.col_values(3)

    del reservations[0:4]
    del description[0:4]

    for msg in messages:  # There's only 2 of these embeds, meaning the worst time complexity is irrelevant
        embed = msg.embeds[0]
        for i, status in enumerate(pc_statuses.values()):

            if status.pop() == "available":
                value = config['lab-icons']['available']
            else:
                value = config['lab-icons']['inuse']

            if reservations[i] == "TRUE":
                value += " " + config['lab-icons']['reserved']
                value = value[::-1]  # Reverse the string, so that reserved comes first

            embed.set_field_at(index=i, name=f"{i+1} 🖥️", value=value, inline=True)

        if embed.title == config['lab']['blueroomnumber']:
            room = config['lab']['blueroom']
        elif embed.title == config['lab']['goldroomnumber']:
            room = config['lab']['goldroom']
        else:
            room = "Room 0"

        if description:
            description = room + "\n\n`" + description[0] + "`"
        else:
            description = room

        embed.description = description
        await msg.edit(embed=embed)


async def send_authentication_embed(context):
    await context.message.delete()
    role = discord.utils.get(context.message.guild.roles, name=config['role']['authed'])

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


async def send_event_panel(context, client):

    await context.message.delete()
    events_sheet = gsheetsAPI.get_sheet_events_subscriptions()
    role_names = events_sheet.col_values(1)
    emojis = events_sheet.col_values(2)  # These are already default, raw emojis
    description_values = events_sheet.col_values(3)

    del role_names[0:4]
    del emojis[0:4]
    del description_values[0:4]

    embed = discord.Embed(
        description="Interested in participating in one or more of our events? Check out below what we have to offer and you'll be pinged with the corresponding role when an event is happening!",
        color=0xff4d4d)
    embed.set_author(name="📆 Role Menu: Event Subscriptions")
    embed.set_thumbnail(url="https://image.flaticon.com/icons/png/512/1458/1458512.png")
    embed.set_footer(
        text="By reacting below, you will receive one of the corresponding event roles above! You will be pinged when an event is happening.")

    for i, role_name in enumerate(role_names):

        role = discord.utils.get(context.guild.roles, name=role_name)
        embed.add_field(name=f"{emojis[i]} - {role_name}", value=f"{role.mention} | {description_values[i]}", inline=True)

    await context.send(embed=embed)
    last_message = [msg async for msg in context.message.channel.history(limit=1)].pop()
    for emoji in emojis:
        await last_message.add_reaction(emoji)


async def send_machine_availability_embed(context):

    await context.message.delete()

    embed = discord.Embed(title=config['lab']['blueroomnumber'], description=config['lab']['blueroom'], color=0x5294ff)
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
    embed.set_footer(text=f"Available {config['lab-icons']['available']} | In-Use {config['lab-icons']['inuse']} | Reserved [{config['lab-icons']['reserved']}]\n\nStockton Discord Bot developed by ChocolateThunder#5292 • Lawrence Chiappelli.")
    await context.send(embed=embed)

    """
    Uncomment the following when the gold room
    is added on website
    """

    # embed = discord.Embed(title=config['lab']['goldroomnumber'],description=config['lab']['goldroom'], color=0xf1ff33)
    # embed.set_author(name="💻 Gaming Lab Machine Availability", url=config['website']['url'])
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
    # embed.set_footer(text=f"Available {config['lab-icons']['available']} | In-Use {config['lab-icons']['inuse']} | Reserved [{config['lab-icons']['reserved']}]\n\nStockton Discord Bot developed by ChocolateThunder#5292 • Lawrence Chiappelli.")
    # await context.send(embed=embed)

    return None


async def send_game_selection_panel(context):

    await context.message.delete()

    embed = discord.Embed(
        title="Participate in one of our supported game selections by reaction to the corresponding reaction!",
        color=0x24b6ff)
    embed.set_footer(text="By reacting below, you will receive one of the corresponding roles above!")
    embed.set_author(name="🎮 Role Menu: Game Assignment")
    embed.set_thumbnail(url="https://stockton.edu/relations/brand-guide/images/osprey-head-full.png")

    game_selection_sheets = gsheetsAPI.get_sheet_supported_games()
    game_roles = game_selection_sheets.col_values(1)
    game_emojis = game_selection_sheets.col_values(2)
    del game_roles[0:4]
    del game_emojis[0:4]

    for i, _ in enumerate(game_roles):

        role = discord.utils.get(context.guild.roles, name=game_roles[i])
        emoji = discord.utils.get(context.guild.emojis, name=str(game_emojis[i]))
        title = role.name
        if title == "Smash Brothers Ultimate":
            title = "Smash Bros. Ultimate"

        embed.add_field(name=f"{emoji} {title}", value=role.mention, inline=True)

    await context.send(embed=embed)
    last_message = [msg async for msg in context.message.channel.history(limit=1)].pop()

    for i, emoji_name in enumerate(game_emojis):
        emoji = discord.utils.get(context.message.guild.emojis, name=emoji_name)
        await last_message.add_reaction(emoji)


async def execute_bot_reaction_directory(emoji, channel, member, is_add=True):

    """
    :param emoji: the emoji being reacted
    :param channel: the channel with reaction
    :param member: the user to perform functionality to, if applicable
    :return: nothing
    """

    auth_emoji = config['emoji']['authed']
    auth_channel = gsheetsAPI.get_landing_channel_name()
    gameselection_channel = gsheetsAPI.get_game_selection_channel_name()
    events_channel = gsheetsAPI.get_event_subscriptions_channel_name()
    game_emojis = dict(config.items('emoji-games'))
    event_emojis = gsheetsAPI.get_event_emojis()

    if isinstance(emoji, discord.partial_emoji.PartialEmoji):
        emoji = emoji.name

    if str(emoji) == auth_emoji and str(channel) == auth_channel:
        auth_role = discord.utils.get(member.guild.roles, name=config['role']['authed'])
        await member.add_roles(auth_role)
        message = [msg async for msg in channel.history(limit=1)].pop()
        embed = message.embeds[0]
        await asyncio.sleep(1)
        embed.set_field_at(index=1, name=f"Users Authorized:", value=get_num_members_with_role(auth_role), inline=True)
        await message.edit(embed=embed)
    elif str(emoji) in game_emojis.values() and str(channel) == gameselection_channel:

        converted_name = convert_emoji_name_to_role(str(emoji))
        game_role = discord.utils.get(member.guild.roles, name=converted_name)

        if is_add and game_role not in member.roles:
            await member.add_roles(game_role)
        else:
            if game_role in member.roles:
                await member.remove_roles(game_role)
    elif str(emoji) in event_emojis and str(channel) == events_channel:  # Event emojis here is list and not dict

        event_sheet = gsheetsAPI.get_sheet_events_subscriptions()
        event_role_names = event_sheet.col_values(1)
        event_emojis = event_sheet.col_values(2)
        del event_role_names[0:4]
        del event_emojis[0:4]

        role_name = None
        """
        For built-in emojis, we have to iterate through
        our list of wanted emojis and extract
        the corresponding role name
        """
        for i, event_role_name in enumerate(event_role_names):
            if emoji == event_emojis[i]:
                role_name = event_role_name
                break

        if role_name is None:
            return None

        event_role = discord.utils.get(member.guild.roles, name=role_name)

        if is_add and event_role not in member.roles:
            await member.add_roles(event_role)
        else:
            if event_role in member.roles:
                await member.remove_roles(event_role)

    return None


async def send_calendar(context):

    await context.message.delete()

    events_channel_name = gsheetsAPI.get_event_subscriptions_channel_name()
    events_channel = discord.utils.get(context.guild.channels, name=events_channel_name)

    events_calendar_sheet = gsheetsAPI.get_sheet_calendar()
    calendar_link = events_calendar_sheet.col_values(1)
    calendar_image_thumbnail = events_calendar_sheet.col_values(2)
    calendar_embed_color = events_calendar_sheet.col_values(3)
    del calendar_link[0:4]
    del calendar_image_thumbnail[0:4]
    del calendar_embed_color[0:4]

    link = calendar_link.pop(0)
    embed = discord.Embed(title="Official Event Calendar",
                          url=link,
                          description="", color=int(calendar_embed_color.pop(0), 16))
    embed.set_author(name="Stockton Esports",
                     url=link,
                     icon_url="https://i.pinimg.com/originals/62/d9/c0/62d9c02a5ba072fdd8ce0ad05782ea1a.jpg")
    embed.set_thumbnail(
        url=calendar_image_thumbnail.pop(0))
    embed.add_field(name="Link:",
                    value=link,
                    inline=False)
    embed.add_field(name="Event subscriptions channel:", value=events_channel.mention, inline=True)
    embed.set_footer(text=f"Occasionally check #{events_channel.name} for new event subscriptions.")
    await context.send(embed=embed)


async def send_boosters_panel(context):

    boosters = context.guild.premium_subscribers
    today = datetime.today()

    embed = discord.Embed(color=0xff8080)
    embed.set_thumbnail(url="https://pbs.twimg.com/media/EWdeUeHXkAQgJh7.png")

    all_boosters = {}
    for booster in boosters:
        delta = today - booster.premium_since

        if delta.days in all_boosters:  # If duplicate amount of days
            all_boosters[delta.days] += f", {booster.mention}"  # Don't overwrite key
        else:
            all_boosters[delta.days] = booster.mention

    sorted_boosters = sorted(all_boosters.items(), reverse=True)
    for key, value in sorted_boosters:  # Note the () after items!
        embed.set_author(name="Server Boosters", icon_url="https://ponyvilleplaza.com/files/img/boost.png")
        embed.add_field(name=f"{key} days", value=value, inline=False)

    await context.send(embed=embed)


async def send_faq_panel(context):

    await context.message.delete()

    faq_sheet = gsheetsAPI.get_sheet_faq()
    questions = faq_sheet.col_values(1)
    answers = faq_sheet.col_values(2)
    del questions[0:4]
    del answers[0:4]

    faq_channel_name = gsheetsAPI.get_faq_channel_name()
    help_dir_channel_name = gsheetsAPI.get_help_directory_channel_name()

    faq_channel = discord.utils.get(context.guild.channels, name=faq_channel_name)
    help_dir_channel = discord.utils.get(context.guild.channels, name=help_dir_channel_name)

    if faq_channel is None:
        bot_channel_name = gsheetsAPI.get_bot_commands_channel_name()
        bot_channel = discord.utils.get(context.guild.channels, name=bot_channel_name)
        await bot_channel.send(f"Missing FAQ channel!")

    try:
        questions_channel = discord.utils.get(context.guild.channels, name="questions")
    except Exception:
        questions_channel = None

    if questions_channel is None or help_dir_channel is None:
        embed = discord.Embed(title=" ",
                              description="Please view our available resources for more help.",
                              color=0x52fffc)
    else:
        embed = discord.Embed(title=" ",
                              description=f"For any additional questions, please see {questions_channel.mention} or {help_dir_channel.mention}!",
                              color=0x52fffc)
    embed.set_author(name="❔ FAQ")
    embed.set_thumbnail(url="https://lh3.googleusercontent.com/proxy/NuskMuMLeEstVyxBKL5OLLQ4V-rULdK0fygraiaeqFaWVclGTaxCXz7RjVurr2GsZvS2ijr5H9_3wZPuPPRAYd5Vg-Q")

    for i in range(len(questions)):
        embed.add_field(name=questions[i], value=answers[i], inline=False)

    await context.send(embed=embed)


def get_num_members_with_role(role):

    num_members_with_role = 0
    for member in role.guild.members:
        if role in member.roles and not member.bot:
            num_members_with_role += 1

    return num_members_with_role


def convert_emoji_name_to_role(emoji):

    if str(emoji).isupper():
        if "SG" in str(emoji):
            converted_name = str(emoji).replace("SG", "S:G")  # Insert colon for CS:GO
        else:
            converted_name = str(emoji)  # And ignore if FIFA or otherwise all caps

    else:
        converted_name = re.sub(r"(\w)([A-Z])", r"\1 \2", str(emoji))
        if "of" in converted_name:  # space before the 'of' in League of Legends
            converted_name = str(converted_name).replace("of", " of")

    return converted_name
