from StocktonBotPackage.Features import customcommands, helpcontactinfo, twitterfeed
from StocktonBotPackage.DevUtilities import configparser, validators
from discord.ext.commands import has_permissions, CheckFailure
from discord.ext import commands
import os
import time
import asyncio
import discord

# -----------------------------------------+
client = commands.Bot(command_prefix='!')  #
# -----------------------------------------+
config = configparser.get_parsed_config()  #
# -----------------------------------------+
twitter_poller = twitterfeed.Poll()        #
# -----------------------------------------#


@client.event
async def on_connect():
    print(F"Bot is successfully connected! Getting ready...")


before = time.time()


@client.event
async def on_ready():
    after = time.time()
    print(f"Bot ready! (in {1000 * (after - before)} milliseconds!)")

    if await validators.machine_availabilty_embed_exists(client):
        print(f"Checks passed! Scraping for website and polling for tweets...")
        # ----------------------------------------------------- #
        await asyncio.wait(
            [
                customcommands.scrape_website(client),
                twitter_poller.poll_for_data_from_stream(client),
                twitter_poller.poll_for_tweet_updates()
            ]
        )
        # ----------------------------------------------------- #
    else:
        print(f"Not pinging for lab updates, visual PC availability interface missing.")


@client.event
async def on_raw_reaction_add(payload):

    emoji = payload.emoji
    channel = client.get_channel(payload.channel_id)
    member = payload.member

    if member.bot:
        return

    if validators.is_bot_reaction_function(emoji, channel):
        await customcommands.execute_bot_reaction_directory(emoji, channel, member)


@client.event
async def on_raw_reaction_remove(payload):

    emoji = payload.emoji
    channel = client.get_channel(payload.channel_id)
    member = discord.utils.get(client.get_all_members(), id=payload.user_id)
    # Attribute member "Only available if event_type is REACTION_ADD."

    if member.bot:
        return

    if validators.is_bot_reaction_function(emoji, channel):
        await customcommands.execute_bot_reaction_directory(emoji, channel, member, False)


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


@client.command(name='auth', pass_context=True)
@has_permissions(administrator=True)
async def auth(ctx):

    """
    Send out the visual authentication panel (in #landing)
    :param ctx: context
    :return: None
    """

    await customcommands.send_authentication_embed(ctx)


@auth.error
async def auth_error(error, ctx):
    print(f"This user does not have perms does not have permissions to enter this command!: {error}")


@client.command(name='gamelab', pass_context=True)
@has_permissions(administrator=True)
async def gamelab(ctx):

    """
    Send out the visual interface for live gaming lab PC updates.
    :param ctx: context
    :return: None
    """
    await customcommands.send_machine_availability_embed(ctx)


@gamelab.error
async def gamelab_error(error, ctx):
    print(f"This user does not have perms does not have permissions to enter this command!: {error}")


@client.command(name='scrape', pass_context=True)
@has_permissions(administrator=True)
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
            customcommands.scrape_website(client)
        ]
    )


@scrape.error
async def scrape_error(error, ctx):
    print(f"This user does not have perms does not have permissions to enter this command!: {error}")


@client.command(name='gameselection', pass_context=True)
@has_permissions(administrator=True)
async def gameselection(ctx):

    """
    Send out the visual game selection panel
    :param ctx: Context
    :return: None
    """

    await customcommands.send_game_selection_panel(ctx)


@client.command(name='helppanel', pass_context=True)
@has_permissions(administrator=True)
async def helppanel(ctx):

    """
    Send out the default help panel for navigational help.
    :return: None
    """

    await helpcontactinfo.send_help_panel(ctx, client)


@helppanel.error
async def helppanel_error(error, ctx):
    print(f"This user does not have perms does not have permissions to enter this command!: {error}")


@client.command(name='populate', pass_context=True)
@has_permissions(administrator=True)
async def populate(ctx):

    """
    Populate the social media feed with last 20 tweets
    :param ctx: context
    :return: None
    """

    await twitterfeed.populate_channel_with_tweets(ctx)


@populate.error
async def populate_error(error, ctx):
    print(f"This user does not have perms does not have permissions to enter this command!: {error}")


@client.command(name="tweet", pass_context=True)
@has_permissions(administrator=True)
async def tweet(ctx):

    """
    Send out the last tweet (if the auto retriever fails)
    :param ctx: context
    :return: None
    """

    await twitterfeed.get_last_tweet()


@tweet.error
async def tweet_error(error, ctx):
    print(f"This user does not have perms does not have permissions to enter this command!: {error}")

client.run(os.environ['TOKEN'])