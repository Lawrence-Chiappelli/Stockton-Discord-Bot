from StocktonBotPackage.Features import twitterfeed, embeddirectory, reactiondirectory, helpdirectory, servermetrics, gamelabscraper
from StocktonBotPackage.DevUtilities import configutil, herokuAPI, validators, utils, gsheetsAPI  # TODO: Relocate / invest in better solution for this unused import
from discord.ext import commands
from datetime import datetime
import os
import time
import asyncio
import discord


intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.

cmd_prefix = '!'  # Used in more than one place
# ----------------------------------------------------------+
client = commands.Bot(command_prefix=cmd_prefix, intents=intents)  #
# ---------------------------------------+------------------+
config = configutil.get_parsed_config()  #
# ---------------------------------------+


@client.event
async def on_connect():
    print(F"Bot is successfully connected! Getting ready...")


before = time.time()


@client.event
async def on_ready():

    print(f"On ready...")
    after = time.time()
    milliseconds = 1000 * (after - before)
    print(f"...bot ready! (in {milliseconds} milliseconds!)")

    channel = utils.get_bot_commands_channel(client)

    if channel:
        await channel.send(f"Bot successfully started in `{milliseconds}` milliseconds.\n\nTwitter poller needs to be started with `!twitterpoll`. See `!metrics`.")

    print(F"Checking everyone pings...")
    await servermetrics.display_ping_check(client)

    # TODO: Automatically update GM panels and leadership panels on setup

    print(f"Starting web scraper...")
    # await asyncio.wait([gamelabscraper.scrape_website(client)])


@client.event
async def on_raw_reaction_add(payload):

    emoji = payload.emoji
    channel = client.get_channel(payload.channel_id)
    member = payload.member
    message = await channel.fetch_message(payload.message_id)  # TODO: Investigate potential performance hits with this

    if member.bot:
        return

    if validators.is_bot_reaction_function(emoji, channel):
        await reactiondirectory.debug_reaction(emoji, channel, member)
        await reactiondirectory.find_reaction_function(emoji, channel, member, message)
    else:
        print(f"Adding is NOT bot reaction function!")


@client.event
async def on_raw_reaction_remove(payload):

    emoji = payload.emoji
    channel = client.get_channel(payload.channel_id)
    member = discord.utils.get(client.get_all_members(), id=payload.user_id)
    message = await channel.fetch_message(payload.message_id)

    # Attribute member "Only available if event_type is REACTION_ADD."

    if member.bot:
        return

    if validators.is_bot_reaction_function(emoji, channel):
        await reactiondirectory.debug_reaction(emoji, channel, member, False)
        await reactiondirectory.find_reaction_function(emoji, channel, member, message, False)
    else:
        print(f"Removing is NOT bot reaction function!")


@client.event
async def on_message(message):

    """
    :param message: Message from client
    :return: None

    Only serves one purpose- no need to abstract
    this away into a different function or module.

    Handles adding 2 reactions for audit messages.
    Also processes commands.
    """

    if message.author.bot:
        try:
            if message.embeds[0].author.name == config['embed']['messagedeleted']:
                await message.add_reaction(config['emoji']['audit'])
                await message.add_reaction(config['emoji']['author'])
        except IndexError:
            return
        return

    await client.process_commands(message)


@client.event
async def on_raw_message_delete(payload):

    """
    :param payload: Payload of message deleted
    :return: None

    Only serves one purpose- no need to abstract
    this away into a different function or module.
    """

    if herokuAPI.Heroku().get_app_state() == "Running locally":  # TODO: Change hardcoded value
        return

    guild = client.get_guild(payload.guild_id)
    channel = discord.utils.get(guild.channels, id=payload.channel_id)
    message = payload.cached_message

    if channel.name == config['channel']['auditlogs'] or str(message.content).startswith(cmd_prefix):
        return

    embed = discord.Embed(title="", description="*Claim responsibility below*", color=0x2eff93)
    embed.set_author(name=config['embed']['messagedeleted'])
    embed.set_thumbnail(
        url="https://lh3.googleusercontent.com/KhigkfQKR3q9U0pSO5JV4XHKaqYykeRyXkPZe5pdeDbLQe8uDqb0eJAAeVX8SUCM7s1E")
    embed.add_field(name="Author", value=message.author, inline=False)
    embed.add_field(name="Content", value=f"`{message.content}`", inline=False)
    embed.add_field(name="Channel", value=channel.mention, inline=False)
    embed.add_field(name="Time deleted", value=str(datetime.now().strftime("%I:%M:%S")), inline=False)
    embed.set_footer(text=f"Deleted by: {config['emoji']['audit']} You | {config['emoji']['author']} Author")

    audit_channel = utils.get_audit_log_channel(guild)
    await audit_channel.send(embed=embed)


@client.event
async def on_member_update(before, after):

    if before.premium_since is None and after.premium_since is not None:

        try:
            emoji = discord.utils.get(after.guild.emojis, name='boost')
            if emoji is None:
                emoji = "<:boost:755245792343883836>"
        except Exception:
            emoji = "<:boost:755245792343883836>"

        general = discord.utils.get(client.get_all_channels(), name="general")
        await general.send(f"{str(emoji)} {after.mention} just boosted the server!")


@client.event
async def on_member_remove(member):

    """
    :param member: the member that left the server
    :return: a message to the welcome channel indicating their absence.
    """

    welcome_channel = utils.get_welcome_channel(member.guild)
    await welcome_channel.send(f"**{member.name}** has left the server.")


def is_authed_user():

    async def predicate(ctx):

        def _add_authed_users_locally():
            nonlocal user_ids
            if user_ids != [int(x) for x in list(config['id-authed'].values())]:
                for i, user_id in enumerate(user_ids):
                    config['id-authed'][f'id{str(i)}'] = str(user_id)

        user_ids = [int(ids) for ids in config['id-authed'].values()]
        print(f"User IDs: {user_ids}")
        _add_authed_users_locally()
        return (ctx.author.id in user_ids) or (ctx.author.id == int(config['id']['owner']))

    return commands.check(predicate)


@client.event
async def on_command_error(ctx, error):

    message = f"Command error or exception found! See below:\n\nCOMMAND - `{ctx.message.content}`\nERROR - `{error}`\nSENT BY - `{ctx.author}`\nFAILED AT - {ctx.channel.mention}\n\nFULL TRACEBACK:```python\n{error}```"
    print(dir(ctx))
    print(dir(error))

    owner = utils.get_codebase_owner_member(ctx.guild)
    commands_channel = utils.get_bot_commands_channel(ctx.guild)
    if owner:
        message += f"\n\n{owner.mention}"

    if owner and commands_channel is None:
        await owner.send(f"{message}")
    else:
        await commands_channel.send(message)


@client.command(name='auth', pass_context=True, usage="<category>", descrption="description")
@is_authed_user()
async def auth(ctx):

    """
    Send out the visual authentication panel (in #landing)
    :param ctx: context
    :return: None
    """

    await embeddirectory.send_authentication_embed(ctx)


@client.command(name='gamelab', pass_context=True)
@is_authed_user()
async def gamelab(ctx):

    """
    Send out the visual interface for live gaming lab PC updates.
    :param ctx: context
    :return: None
    """
    await embeddirectory.send_machine_availability_embed(ctx)


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
            gamelabscraper.scrape_website(client)
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

    await embeddirectory.send_game_selection_embed(ctx)


@client.command(name='helppanel', pass_context=True)
@is_authed_user()
async def helppanel(ctx):

    """
    Send out the student leadership panel.
    :param ctx: Context
    :return: None
    """

    await helpdirectory.send_help_panel(ctx)


@client.command(name='eventpanel', pass_context=True)
@is_authed_user()
async def eventpanel(ctx):

    """
    Send out the event selection panel.
    :param ctx: Context
    :return: None
    """

    await embeddirectory.send_event_embed(ctx)


@client.command(name="twitterstream", pass_context=True)
@is_authed_user()
async def twitterstream(ctx):

    """
    Force stream auth *IF* 420 error. Wait 15 minutes!
    :param ctx:
    :return:
    """

    twitterfeed.force_thread_start_for_auth()


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
        commands_channel = utils.get_bot_commands_channel(ctx.guild)
        owner = utils.get_codebase_owner_member(ctx.guild)
        await commands_channel.send(f"{owner.mention}, all exceptions were tried against the Twitter streamer. The following was captured:\n{last_resort}\n\nIt is highly recommended to execute `!twitterstream` again.")


@client.command(name='populate', pass_context=True)
@is_authed_user()
async def populate(ctx):

    """
    Populate the social media feed with last 20 tweets
    :param ctx: context
    :return: None
    """

    await twitterfeed.populate_channel_with_tweets(ctx)


@client.command(name="tweet", pass_context=True)
@is_authed_user()
async def tweet(ctx):

    """
    Send out the last tweet (if the auto retriever fails)
    :param ctx: context
    :return: None
    """

    await twitterfeed.get_last_tweet()


@client.command(name="gmpanel", pass_context=True)
@is_authed_user()
async def gmpanel(ctx):

    """
    Send out the game manager's contact info panel.
    :param ctx: context
    :return: None
    """

    await helpdirectory.send_game_manager_panel(ctx)


@client.command(name="forceoff", pass_context=True)
@is_authed_user()
async def forceoff(ctx):

    """
    Force turn off the web scraper (if exception caused API to break)
    :param ctx: context
    :return: None
    """

    await gamelabscraper.force_off(ctx.guild)


@client.command(name="calendarr", pass_context=True)
@is_authed_user()
async def calendarr(ctx):

    """
    Send out the google docs calendar embed
    :param ctx:
    :return:
    """

    await embeddirectory.send_calendar_embed(ctx)


@client.command(name="boosters", pass_context=True)
@is_authed_user()
async def boosters(ctx):

    """
    Get server boosters
    :param ctx:
    :return:
    """

    await embeddirectory.send_boosters_embed(ctx)


@client.command(name="faq", pass_context=True)
@is_authed_user()
async def faq(ctx):

    """
    Send out the FAQ panel
    :param ctx:
    :return:
    """

    await embeddirectory.send_faq_embed(ctx)


@client.command(name="metrics", pass_context=True)
@is_authed_user()
async def metrics(ctx):

    """
    Get server metrics
    :param ctx:
    :return:
    """

    await servermetrics.display_metrics(ctx)


@client.command(name='restart', pass_context=True)
@is_authed_user()
async def restart(ctx):
    """
    Restart the bot.
    :return: None
    """

    await herokuAPI.Heroku().restart_app(ctx)


@client.command(name='rolecheck', pass_context=True)
@is_authed_user()
async def rolecheck(ctx):
    """
    Display users who are missing a role.
    :return: None
    """

    await servermetrics.display_role_check(ctx)
    
    
@client.command(name='pingcheck', pass_context=True)
@is_authed_user()
async def pingcheck(ctx):
    """
    Check user amount of @everyone pings
    :return: None
    """

    await servermetrics.display_ping_check(ctx)


client.run(os.environ['TOKEN'])
