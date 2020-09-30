from StocktonBotPackage.DevUtilities import gsheetsAPI, gaminglabAPI, validators, configparser, utils
import discord
import asyncio


# -----------------------------------------+
config = configparser.get_parsed_config()  #
# -----------------------------------------+


class Scraper:

    def __init__(self, scraping):
        self.is_scraping = scraping
        self.issued_off = False


# ------------------------+
scraper = Scraper(False)  #
# ------------------------+
# Will help prevent multiple instances of scrapers.
# Only one should be allowed at any given time.


async def force_off(guild: discord.guild):

    debug_channel = utils.get_bot_commands_channel(guild)

    try:
        scraper.issued_off = True
        await debug_channel.send(f"Turning off webscraper, please wait...")
    except Exception as e:
        print(f"Unable to force off!")
        await debug_channel.send(f"Exception caught trying to turn off webscraper:\n\n{e}")


async def scrape_website(client):

    """
    :param client: client bot is connected to
    :return: only if there's an issue
    Type '!scrape' to restart the scraping process.

    Note: this function is executed on bot_ready, so
    I have to work around not having a convenient
    guild object.
    """

    debug_channel = utils.get_bot_commands_channel(client)
    await debug_channel.send(f"Started web scraping.")
    print(f"Web scraper starting...")

    while True:

        if scraper.issued_off:
            game_lab_channel = utils.get_game_lab_channel(client)
            print(f"Successfully turned off webscraper")
            await debug_channel.send(f"Successfully turned off scraper.\n\nPlease go to {game_lab_channel.mention} and verify this action by comparing its edited timestamp.")
            scraper.issued_off = False
            scraper.is_scraping = False
            return

        if not await validators.machine_availabilty_embed_exists(client):
            await debug_channel.send(f"Machine availability panels must first exist in the channel `#{debug_channel_name}`! You can add these panels by entering `!gamelab` inside the channel, then start auto-updating PC availability with `!scrape`.")
            return

        scraper.is_scraping = True
        print(f"Checking for machine availability...")
        try:
            pc_statuses = await gaminglabAPI.get_pc_availability()
        except Exception as API_error_429_or_500:  # 429 was NOT caught here
            print(f"Unable to scrape data!\n429 - Resource Quota Exhausted\n500 - Internal server error:\n{API_error_429_or_500}")
            await debug_channel.send(f"Exception caught scraping data! Retrying in 105 seconds. Error:\n{API_error_429_or_500}")
            await asyncio.sleep(105)
            continue

        print(f"Updating PC availability with the following statuses:\n{pc_statuses}")
        await update_machine_availability_embed(client, pc_statuses)
        print(F"Trying again in 25 seconds")
        await asyncio.sleep(25)


async def update_machine_availability_embed(client: type(discord.Client()), pc_statuses: dict):

    """
    :param guild: A guild object, responsible for outputting updates
    :param pc_statuses: A list, grabbed from gaminglabAPI.get_pc_availability()
    :return:
    """

    game_lab_channel = utils.get_game_lab_channel(client)
    messages = [msg async for msg in game_lab_channel.history(limit=int(config['lab']['num_rooms']))]

    reservations, description = gsheetsAPI.get_blue_room_reserves_and_desc()
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