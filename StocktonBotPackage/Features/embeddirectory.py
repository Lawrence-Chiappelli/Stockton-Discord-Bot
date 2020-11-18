# Abstract the command content away from bot.py and keep it clean.

from StocktonBotPackage.DevUtilities import configutil, utils
from datetime import datetime
import discord

# -----------------------------------------+
config = configutil.get_parsed_config()  #
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

    await context.send(embed=embed)
    last_message = await utils.get_last_message_from_channel(context.channel)
    await last_message.add_reaction("✅")

    return None


async def send_event_embed(context):

    await context.message.delete()
    event_info = utils.get_event_subscription_info()

    # Not critical that this information is stored

    embed = discord.Embed(
        description="Interested in participating in one or more of our events?\nCheck out below what we have to offer and react to receive relevant event pings!",
        color=0xff4d4d)
    embed.set_author(name="📆 Role Menu: Event Subscriptions")
    embed.set_thumbnail(url="https://image.flaticon.com/icons/png/512/1458/1458512.png")
    # embed.set_footer(text="React above to receive updates!")
    # The footer feels and reads redundant

    for i, role_name in enumerate(event_info[0]):  # All internal lists will be equivalent length

        role = discord.utils.get(context.guild.roles, name=role_name)
        num_subs = utils.get_num_members_with_role(role)
        embed.add_field(name=f"{event_info[1][i]} - {role_name}", value=f"About {role.mention}:\n\n`{event_info[2][i]}`", inline=False)

    last_message = await utils.get_last_message_from_channel(context.channel)
    if last_message:
        await last_message.edit(embed=embed)
    else:
        await context.send(embed=embed)

        # Need to check for last message again to
        # add reactions to the appropriate message
        last_message = await utils.get_last_message_from_channel(context.channel)
        for emoji in event_info[1]:
            await last_message.add_reaction(emoji)


async def send_machine_availability_embed(context):

    await context.message.delete()

    embed = discord.Embed(title=config['lab']['blueroomnumber'], description=config['lab']['blueroom'], color=0x5294ff)
    embed.set_author(name="💻 Gaming Lab Machine Availability", url=config['website']['url'])
    embed.set_thumbnail(url="https://i.imgur.com/eVqogAY.jpg")

    # TODO: Redo the following using some form of iteration

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

    """
    :param context: Command context
    :return: None

    Sends out the game selection panel.
    Overwrites any existing ones.
    """

    await context.message.delete()

    embed = discord.Embed(
        description="Interested in participating in one of our supported game selections? React to one of the below to receive relevant pings, such as in-house tournaments or events! \n\nThis extends to both casual and competitive interest. To play competitively in Stockton officially, please message a Game Manager. See the Game Manager Hub on the left hand-side.\n",
        color=0x24b6ff)
    embed.set_footer(text="React to the above for updates!")
    embed.set_author(name="🎮 Role Menu: Game Assignment")
    embed.set_thumbnail(url="https://stockton.edu/relations/brand-guide/images/osprey-head-full.png")

    role_games = [role for role in config['roles-games'].values()]
    emoji_games = [emoji for emoji in config['emoji-games'].values()]

    for i, _ in enumerate(role_games):

        role = discord.utils.get(context.guild.roles, name=role_games[i])
        emoji = discord.utils.get(context.guild.emojis, name=str(emoji_games[i]))
        title = role.name
        if title == "Smash Brothers Ultimate":
            title = "Smash Bros. Ultimate"

        embed.add_field(name=f"{emoji} {title}", value=role.mention, inline=True)

    last_message = await utils.get_last_message_from_channel(context.channel)
    if last_message:
        await last_message.edit(embed=embed)
    else:
        await context.send(embed=embed)
        last_message = await utils.get_last_message_from_channel(context.channel)

    for i, emoji_name in enumerate(emoji_games):
        emoji = discord.utils.get(context.message.guild.emojis, name=emoji_name)
        if emoji not in last_message.reactions:  # Don't spend time adding old ones
            await last_message.add_reaction(emoji)


async def send_calendar_embed(context):

    """
    :param context: Command context
    :return: None

    Sends out the calendar embed panel.
    Overwrites any existing ones.
    """

    await context.message.delete()
    events_channel = utils.get_event_subscriptions_channel(context.guild)
    calendar = utils.get_calendar_info()  # See index signature

    embed = discord.Embed(title="Official Event Calendar",
                          url=calendar[0],
                          description="", color=int(calendar[2], 16))
    embed.set_author(name="Stockton Esports",
                     url=calendar[0],
                     icon_url="https://i.pinimg.com/originals/62/d9/c0/62d9c02a5ba072fdd8ce0ad05782ea1a.jpg")
    embed.set_thumbnail(url=calendar[1])
    embed.add_field(name="Link:",
                    value=calendar[0],
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

    faq = utils.get_faq_and_a()
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

    for q_and_a in faq:
        embed.add_field(name=q_and_a[0].capitalize(), value=q_and_a[1], inline=False)

    await context.send(embed=embed)
