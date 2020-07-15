from StocktonBotPackage.Features import command_functionality
from StocktonBotPackage.DevUtilities import configparser, validators
from discord.ext import commands
import os
import time
import asyncio

# -----------------------------------------+
client = commands.Bot(command_prefix='!')  #
# -----------------------------------------+
config = configparser.get_parsed_config()  #
# -----------------------------------------#


before = time.time()


@client.event
async def on_connect():
    print(F"Bot is successfully connected! Getting ready...")


@client.event
async def on_ready():
    after = time.time()
    print(f"Bot ready! (in {1000 * (after - before)} milliseconds!)")

    if await validators.machine_availabilty_embed_exists(client):
        print(f"Pinging for lab updates...")
        # ----------------------------------------------------- #
        await asyncio.wait(
            [
                await command_functionality.scrape_website(client)
            ]
        )
        # ----------------------------------------------------- #
    else:
        print(f"Not pinging for lab updates, visual interface missing.")



@client.event
async def on_raw_reaction_add(payload):

    emoji = payload.emoji
    channel = client.get_channel(payload.channel_id)
    member = payload.member

    if validators.is_bot_reaction_function(emoji, channel):
        await command_functionality.execute_bot_reaction_directory(emoji, channel, member)


@client.event
async def on_message(message):

    if message.author.bot:
        # TODO: Accommodate for social media feed
        return

    await client.process_commands(message)


async def get_emoji_from_bot(message):

    if [item[0] for item in message.embeds]:
        await message.channel.send("Found an embed")
        return None
    else:
        await message.channel.send("Did not find an embed")
        return None


@client.command()
async def auth(ctx):

    """
    Send out the visual authentication panel (in #landing)
    :param ctx: content
    :return: None
    """

    await command_functionality.send_authentication_embed(ctx)


@client.command()
async def gamelab(ctx):

    """
    Send out the visual interface for live gaming lab PC updates.
    :param ctx: context
    :return: None
    """
    await command_functionality.send_machine_availability_embed(ctx)


@client.command()
async def scrape(ctx):

    """
    Begin updating the gaming lab's PC usage (!gamelab required).
    :param ctx: context (not needed here)
    :return: None

    Context was intentionally omitted as a
    parameter due to the asynchronous nature
    of the Discord.
    """

    await asyncio.wait(
        [
            await command_functionality.scrape_website(client)
        ]
    )


client.run(os.environ['TOKEN'])
