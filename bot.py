from StocktonBotPackage.Features import customcommands, helpcontactinfo, twitterfeed, servermetrics
from StocktonBotPackage.DevUtilities import configparser, validators, gsheetsAPI
from discord.ext.commands import has_permissions, CheckFailure
from discord.ext import commands
import os
import time
import asyncio
import discord
import datetime

# -----------------------------------------+
client = commands.Bot(command_prefix='!')  #
# -----------------------------------------+
config = configparser.get_parsed_config()  #
# -----------------------------------------+

@client.event
async def on_connect():
    print(F"Bot is successfully connected! Getting ready...")


before = time.time()


@client.event
async def on_ready():

    after = time.time()
    milliseconds = 1000 * (after - before)
    print(f"Bot ready! (in {milliseconds} milliseconds!)")

    try:
        server = client.get_guild(int(os.environ['DISCORD-ID-SERVER']))  # No client object to grab
        channel = discord.utils.get(server.channels, name=config['channel']['botcommands'])
    except KeyError as ke:
        server = None
        channel = None
        print(f"No Discord server ID has been provided. This is okay. Exception\n{ke}")

    if server and channel:
        await channel.send(f"Bot successfully restarted in `{milliseconds}` milliseconds.\n\nTwitter poller needs to be started with `!twitterpoll`. See `!metrics`.")

    if await validators.machine_availabilty_embed_exists(client):
        print(f"Checks passed! Turning on game lab availability...")
        await asyncio.wait([customcommands.scrape_website(client)])
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
        try:
            if message.embeds[0].author.name == config['embed']['messagedeleted']:  # For auditing
                await message.add_reaction(config['emoji']['audit'])
        except IndexError:
            return
        return

    await client.process_commands(message)


@client.event
async def on_raw_message_delete(payload):

    guild = client.get_guild(payload.guild_id)
    channel = discord.utils.get(guild.channels, id=payload.channel_id)
    message = payload.cached_message

    if channel.name == gsheetsAPI.get_audit_logs_channel_name():
        return

    embed = discord.Embed(title="Deleted by:", description="_react below_", color=0x2eff93)
    embed.set_author(name="Action: Message Deleted")
    embed.set_thumbnail(
        url="https://lh3.googleusercontent.com/KhigkfQKR3q9U0pSO5JV4XHKaqYykeRyXkPZe5pdeDbLQe8uDqb0eJAAeVX8SUCM7s1E")
    embed.add_field(name="Author", value=message.author, inline=False)
    embed.add_field(name="Content", value=f"`{message.content}`", inline=False)
    embed.add_field(name="Channel", value=channel.mention, inline=False)
    embed.add_field(name="Deleted", value=str(datetime.datetime.now().strftime("%I:%M:%S")), inline=False)

    audit_channel = discord.utils.get(guild.channels, name=config['channel']['auditlogs'])
    await audit_channel.send(embed=embed)


@client.event
async def on_member_remove(member):

    """
    :param member: the member that left the server
    :return: a message to the welcome channel indicating their absence.
    """

    welcome_channel_name = gsheetsAPI.get_welcome_channel_name()
    welcome_channel = discord.utils.get(member.guild.channels, name=welcome_channel_name)
    await welcome_channel.send(f"**{member.name} has left the server.")


async def get_emoji_from_bot(message):

    if [item[0] for item in message.embeds]:
        await message.channel.send("Found an embed")
        return None
    else:
        await message.channel.send("Did not find an embed")
        return None


def is_authed_user():

    async def predicate(ctx):

        user_ids = gsheetsAPI.get_authed_user_ids()
        return (ctx.author.id in user_ids) or (ctx.author.id == int(config['id']['owner']))

    return commands.check(predicate)


"""
Bot Commands:
"""


@client.command(name='auth', pass_context=True)
@is_authed_user()
async def auth(ctx):

    """
    Send out the visual authentication panel (in #landing)
    :param ctx: context
    :return: None
    """

    await customcommands.send_authentication_embed(ctx)


@auth.error
async def auth_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name='gamelab', pass_context=True)
@is_authed_user()
async def gamelab(ctx):

    """
    Send out the visual interface for live gaming lab PC updates.
    :param ctx: context
    :return: None
    """
    await customcommands.send_machine_availability_embed(ctx)


@gamelab.error
async def gamelab_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name='scrape', pass_context=True)
@is_authed_user()
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
async def scrape_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name='gameselection', pass_context=True)
@is_authed_user()
async def gameselection(ctx):

    """
    Send out the visual game selection panel
    :param ctx: Context
    :return: None
    """

    await customcommands.send_game_selection_panel(ctx)


@gameselection.error
async def gameselection_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name='helppanel', pass_context=True)
@is_authed_user()
async def helppanel(ctx):

    """
    Send out the default help panel for navigational help.
    :param ctx: Context
    :return: None
    """

    await helpcontactinfo.send_help_panel(ctx, client)


@helppanel.error
async def helppanel_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name='eventpanel', pass_context=True)
@is_authed_user()
async def eventpanel(ctx):

    """
    Send out the event selection panel.
    :param ctx: Context
    :return: None
    """

    await customcommands.send_event_panel(ctx, client)


@eventpanel.error
async def eventpanel_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name="twitterstream", pass_context=True)
@is_authed_user()
async def twitterstream(ctx):

    """
    Force stream auth *IF* 420 error. Wait 15 minutes!
    :param ctx:
    :return:
    """

    twitterfeed.force_thread_start_for_auth()


@twitterstream.error
async def faq_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name='twitterpoll', pass_context=True)
@is_authed_user()
async def twitterpoll(ctx):

    """
    Start the Twitter streaming process
    :param ctx: context
    :return: None
    """

    try:
        await asyncio.wait(
            [
                twitterfeed.twitter_poller.poll_for_data_from_stream(client),
                twitterfeed.twitter_poller.poll_for_tweet_updates(),
            ]
        )
    except Exception as last_resort:
        commands_channel_name = discord.utils.get(ctx.guild.channels, name=config['channel']['bot-commands'])
        owner = discord.utils.get(ctx.guild.channels, name=int(config['id']['owner']))
        await commands_channel_name.send(f"{owner.mention}, all exceptions were tried against the Twitter streamer. The following was captured:\n{last_resort}\n\nIt is highly recommended to execute `!twitterstream` again.")


@twitterpoll.error
async def stream_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name='populate', pass_context=True)
@is_authed_user()
async def populate(ctx):

    """
    Populate the social media feed with last 20 tweets
    :param ctx: context
    :return: None
    """

    await twitterfeed.populate_channel_with_tweets(ctx)


@populate.error
async def populate_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name="tweet", pass_context=True)
@is_authed_user()
async def tweet(ctx):

    """
    Send out the last tweet (if the auto retriever fails)
    :param ctx: context
    :return: None
    """

    await twitterfeed.get_last_tweet()


@tweet.error
async def tweet_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name="gmpanel", pass_context=True)
@is_authed_user()
async def gmpanel(ctx):

    """
    Send out the game manager's contact info panel.
    :param ctx: context
    :return: None
    """

    await helpcontactinfo.send_gm_panel(client, ctx)


@gmpanel.error
async def gmpanel(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name="forceoff", pass_context=True)
@is_authed_user()
async def forceoff(ctx):

    """
    Force turn off the web scraper (if exception caused API to break)
    :param ctx: context
    :return: None
    """

    await customcommands.force_off(client)


@forceoff.error
async def forceoff_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name="calendar", pass_context=True)
@is_authed_user()
async def calendar(ctx):

    """
    Send out the google docs calendar embed
    :param ctx:
    :return:
    """

    await customcommands.send_calendar(ctx)


@calendar.error
async def calendar_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name="boosters", pass_context=True)
@is_authed_user()
async def boosters(ctx):

    """
    Get server boosters
    :param ctx:
    :return:
    """

    await customcommands.send_boosters_panel(ctx)


@boosters.error
async def boosters_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name="faq", pass_context=True)
@is_authed_user()
async def faq(ctx):

    """
    Send out the FAQ panel
    :param ctx:
    :return:
    """

    await customcommands.send_faq_panel(ctx)


@faq.error
async def faq_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")


@client.command(name="metrics", pass_context=True)
@is_authed_user()
async def metrics(ctx):

    """
    Get server metrics
    :param ctx:
    :return:
    """

    await servermetrics.display_metrics(ctx)


@metrics.error
async def metrics_error(ctx, error):
    print(f"{ctx.author.name} is not authorized to use '{ctx.message.content}':\nError message: {error}")

client.run(os.environ['TOKEN'])