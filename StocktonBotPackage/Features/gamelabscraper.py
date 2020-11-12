from StocktonBotPackage.DevUtilities import gsheetsAPI, seleniumbrowser, validators, configutil, utils
import discord
import asyncio


# -----------------------------------------+
config = configutil.get_parsed_config()  #
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
r    """

    debug_channel = utils.get_bot_commands_channel(client)
    await debug_channel.send(f"Started web scraping.")
    print(f"Web scraper starting...")

    # This loop will always run indefinitely.
    while True:

        # During this web scraping, first check if there was
        # any commands issued to force stop this functionality.
        if scraper.issued_off:
            game_lab_channel = utils.get_game_lab_channel(client)
            print(f"Successfully turned off webscraper")
            await debug_channel.send(f"Successfully turned off scraper.\n\nPlease go to {game_lab_channel.mention} and verify this action by comparing its edited timestamp.")
            scraper.issued_off = False
            scraper.is_scraping = False
            return

        # Secondly, check if the embeds exist.
        # It's possible someone may have deleted them mid-process.
        if not await validators.validate_pc_availability_embeds(client):
            print(f"...web scraping ending prematurely- embeds are missing! (This can be restarted with !scrape)")
            await debug_channel.send(f"ERROR: Machine availability panels must first exist in the channel `#{debug_channel}`! You can add these panels by entering `!gamelab` inside the channel, then start auto-updating PC availability with `!scrape`.")
            return

        scraper.is_scraping = True

        pc_statuses = await _get_scraped_pc_availability()
        if pc_statuses is None:
            print("Game Lab Availability is offline. Unable to get PC statuses. Restart bot with !restart.")
            break

        print(f"Updating PC availability with the following statuses:\n\t{pc_statuses}")
        await update_machine_availability_embed(client, pc_statuses)
        print(F"Trying again in 5 seconds")
        await asyncio.sleep(5)

    return None


async def _get_scraped_pc_availability():

    browser = seleniumbrowser.browser

    while True:
        try:

            pc_statuses = {}
            for i in range(1, int(config['lab']['pc_amount'])+1):  # Plus 1, because for i in range is inclusive
                element = browser.find_element_by_id(id_=config['lab-pc-tags'][f'{str(i)}'])
                attribute = element.get_attribute("style")
                if config['lab']['available'] in str(attribute):
                    pc_statuses[f'pc{i}'] = ['available']
                else:
                    pc_statuses[f'pc{i}'] = ['inuse']

            return pc_statuses

        except AttributeError as website_missing:
            print(f"AttributeError exception caught retrieving information from browser. Most probably, the website that contained the data has been moved, changed, or deleted:\n\t{website_missing}")
            return None
        except Exception as stale_reference_element:
            print(f"Exception caught retrieving information from browser. Possibly stale reference elemnts??:\n\t{stale_reference_element}")
            return None


async def update_machine_availability_embed(client: type(discord.Client()), pc_statuses: dict):

    """
    :param guild: A guild object, responsible for outputting updates
    :param pc_statuses: A list, grabbed from gaminglabAPI.get_pc_availability()
    :return:
    """

    def _adjust_embed_for_errors():

        """
        :return: None

        Any errors encountered having retrieved PC statuses?
        If so, just update the embed with an error message.
        """

        nonlocal embed
        embed.description = pc_statuses
        for j in range(int(config['lab']['pc_amount'])):
                embed.set_field_at(index=j, name=f"ERROR", value="❕")

    def _adjust_embed_for_reservations():

        """
        :return: None

        Self explanatory: Make rounds of iterations as necessary.
        There shouldn't be any errors encountered along the way
        if this is the case.
        """

        reservations = [reservation for reservation in config['lab-blue-reservations'].values()]
        description = config['lab-blue-description']['content']

        for i, status in enumerate(pc_statuses):

            if status.pop() == "available":
                value = config['lab-icons']['available']
            else:
                value = config['lab-icons']['inuse']

            if reservations[i] == "TRUE":
                value += " " + config['lab-icons']['reserved']
                value = value[::-1]  # Reverse the string, so that reserved comes first

            embed.set_field_at(index=i, name=f"{i + 1} 🖥️", value=value, inline=True)

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

    game_lab_channel = utils.get_game_lab_channel(client)
    messages = [msg async for msg in game_lab_channel.history(limit=int(config['lab']['num_rooms']))]

    for msg in messages:  # There's only 2 of these embeds, meaning the worst time complexity is irrelevant
        embed = msg.embeds[0]

        if not isinstance(pc_statuses, list):  # The string here is an error message, of any data type not list
            _adjust_embed_for_errors()
        else:
            _adjust_embed_for_reservations()
        await msg.edit(embed=embed)