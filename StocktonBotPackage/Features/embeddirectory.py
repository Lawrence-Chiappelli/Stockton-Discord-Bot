# Abstract the command content away from bot.py and keep it clean.

from StocktonBotPackage.DevUtilities import configparser, gsheetsAPI, utils
from datetime import datetime
import discord

# -----------------------------------------+
config = configparser.get_parsed_config()  #
# -----------------------------------------+


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
    embed.add_field(name="Users Authorized:", value=utils.get_num_members_with_role(role), inline=True)
    embed.set_footer(text="Stockton Discord Bot developed by ChocolateThunder#5292 • Lawrence Chiappelli.")
    await context.message.channel.send(embed=embed)
    last_message = [msg async for msg in context.message.channel.history(limit=1)].pop()
    await last_message.add_reaction("✅")

    return None


async def send_event_embed(context, client):  # TODO: Why did I have this client object here?

    await context.message.delete()
    role_names, emojis, description_values = gsheetsAPI.get_event_subscriptions()

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


async def send_game_selection_embed(context):

    await context.message.delete()

    embed = discord.Embed(
        title="Participate in one of our supported game selections by reaction to the corresponding reaction!",
        color=0x24b6ff)
    embed.set_footer(text="By reacting below, you will receive one of the corresponding roles above!")
    embed.set_author(name="🎮 Role Menu: Game Assignment")
    embed.set_thumbnail(url="https://stockton.edu/relations/brand-guide/images/osprey-head-full.png")

    game_roles, game_emojis = gsheetsAPI.get_sheet_supported_games()
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


async def send_calendar_embed(context):

    await context.message.delete()

    events_channel_name = gsheetsAPI.get_event_subscriptions_channel_name()
    events_channel = discord.utils.get(context.guild.channels, name=events_channel_name)

    calendar_link, calendar_image_thumbnail, calendar_embed_color = gsheetsAPI.get_calendar()

    link = calendar_link.pop(0)  # TODO: Why did I pop these? Experimentation?
    thumbnail = calendar_image_thumbnail.pop(0)
    color = calendar_embed_color.pop(0)

    embed = discord.Embed(title="Official Event Calendar",
                          url=link,
                          description="", color=int(color, 16))
    embed.set_author(name="Stockton Esports",
                     url=link,
                     icon_url="https://i.pinimg.com/originals/62/d9/c0/62d9c02a5ba072fdd8ce0ad05782ea1a.jpg")
    embed.set_thumbnail(url=thumbnail)
    embed.add_field(name="Link:",
                    value=link,
                    inline=False)
    embed.add_field(name="Event subscriptions channel:", value=events_channel.mention, inline=True)
    embed.set_footer(text=f"Occasionally check #{events_channel.name} for new event subscriptions.")
    await context.send(embed=embed)


async def send_boosters_embed(context):

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


async def send_faq_embed(context):

    await context.message.delete()

    questions, answers = gsheetsAPI.get_faq()
    faq_channel = utils.get_faq_channel(context.guild)
    help_dir_channel = utils.get_help_directory_channel(context.guild)

    if faq_channel is None:
        bot_channel = utils.get_bot_commands_channel(context.guild)
        await bot_channel.send(f"Missing FAQ channel!")

    try:  # Questions are not a part of the config file
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

