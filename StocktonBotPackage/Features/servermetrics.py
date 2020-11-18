from StocktonBotPackage.DevUtilities import utils, configutil, herokuAPI
from StocktonBotPackage.Features import twitterfeed, gamelabscraper
from datetime import datetime
import calendar
import discord
import time


# ---------------------------------------#
config = configutil.get_parsed_config()  #
# ---------------------------------------#


"""
Overall metrics:
"""


async def display_metrics(context):
    """
    :param context: Needed for guild and its related attributes
    :return: None

    Retrieves the necessary metrics and sends
    it out in a visual interface all in one.
    """

    await context.send("Getting metrics, please wait...")

    # --------------------#
    before = time.time()  #
    # --------------------#

    # Title
    owner = discord.utils.get(context.guild.members, id=int(config['id']['owner']))
    bot_dev_role = discord.utils.get(context.guild.roles, name=config['role-other']['botdeveloper'])
    moderator_role = discord.utils.get(context.guild.roles, name=config['role']['moderator'])
    authed_role = discord.utils.get(context.guild.roles, name=config['role']['authed'])

    # Server Overview
    num_authed_members = utils.get_num_members_with_role(authed_role)
    num_server_members = len(context.guild.members)

    # Role metrics
    roles_staff = [discord.utils.get(context.guild.roles, name=role) for role in config['role'].values()]
    roles_games = [discord.utils.get(context.guild.roles, name=role) for role in config['role-games'].values()]
    roles_other = [discord.utils.get(context.guild.roles, name=role) for role in config['role-other'].values()]
    num_roles_staff = [utils.get_num_members_with_role(role) for role in roles_staff]
    num_roles_games = [utils.get_num_members_with_role(role) for role in roles_games]
    num_roles_other = [utils.get_num_members_with_role(role) for role in roles_other]

    # Note: I'm using separate lists because dict comprehension is
    # too long for a single line of code- I would have to use
    # discord utils twice.

    # Twitter related
    rate_checks = twitterfeed.TweepyClient().get_rate_limit()
    timeline_rates = twitterfeed.TweepyClient().get_rates_timeline()
    id_rates = twitterfeed.TweepyClient().get_rates_id()
    twitter_streaming = utils.get_bool_symbols(twitterfeed.listener.is_streaming)
    twitter_poll_status = utils.get_bool_symbols(twitterfeed.twitter_poller.is_polling)
    twitter_error = twitterfeed.listener.error
    if twitterfeed.listener.is_streaming and twitterfeed.twitter_poller.is_polling and twitter_error is None:
        twitter_online_status = utils.get_online_symbols(True)
    else:
        twitter_online_status = utils.get_online_symbols(False)

    # Gamelab related
    gaming_lab_scraping = utils.get_bool_symbols(gamelabscraper.scraper.is_scraping)

    embed = discord.Embed(color=0xff2424,
                          description=f"For more info, please message {owner.mention}, an available {bot_dev_role.mention} or {moderator_role.mention}!")
    embed.set_author(name="📈 Server and API metrics 📉")
    embed.add_field(name="# Authorized server members", value=f"`{num_authed_members}` / `{num_server_members}`",
                    inline=False)
    embed.add_field(name="# Staff", value=get_formatted_role_metrics(roles_staff, num_roles_staff), inline=False)
    embed.add_field(name="# Players", value=get_formatted_role_metrics(roles_games, num_roles_games), inline=False)
    embed.add_field(name="# Other", value=get_formatted_role_metrics(roles_other, num_roles_other), inline=False)
    embed.add_field(name="Twitter API rates",
                    value=f"Rate limits: `{rate_checks}/180`\nTimeline rates: `{timeline_rates}/900`\nStream rates: `{id_rates}/900`",
                    inline=False)
    embed.add_field(name="Twitter stream",
                    value=f"Is streaming: {twitter_streaming}\nIs polling: {twitter_poll_status}\nError: `{twitter_error}`\nStatus: `{twitter_online_status}`",
                    inline=False)
    embed.add_field(name="Twitter stream info",
                    value=f"If not streaming: `!twitterstream`\nIf not polling: `!twitterpoll`\nIf error 420: `!twitterpoll` after __15__ minutes\nIf online & tweet missing: `!tweet`",
                    inline=False)
    embed.add_field(name="Google Sheets API rates", value=f"Read / 100 secs: `100`\nRead / day: `unlimited`",
                    inline=False)
    embed.add_field(name="Gaming lab stream", value=f"Is online: {gaming_lab_scraping}\n", inline=False)
    embed.add_field(name="Gaming lab info",
                    value=f"If not scraping: `!scrape`\nIf not updating: `!forceoff`\nLast resort: `Restart the bot`",
                    inline=False)
    embed.add_field(name="Overall bot status",
                    value=f"Heroku rates: `{herokuAPI.Heroku().get_rate_limits()}`\nApp run location: `{herokuAPI.Heroku().get_app_state()}`\nIf running locally: `Wait for Heroku push`",
                    inline=False)

    # -------------------#
    after = time.time()  #
    # -------------------#

    embed.set_footer(text=f"📊 Metrics retrieved in {1000 * (after - before)} milliseconds.")
    await context.send(embed=embed)


def get_formatted_role_metrics(roles: list, roles_amounts: list):
    """
    :param roles: The category of roles to iterate through and format
    :param roles_amounts: Gets placed next to the role category
    :return: The formatted string of: {roles}:`{role_amounts}`
    """

    if len(roles) == 0:
        return "No roles found for this category"
    elif len(roles) != len(roles_amounts):
        return "Passed incorrect role arguments"

    try:
        formatted_string = ""
        for i in range(len(roles)):

            if roles[i].name == config['role']['authed']:
                continue  # No need to add authed role here

            if i >= len(roles):
                formatted_string += f"{roles[i].mention}:`{roles_amounts[i]}`"
            else:
                formatted_string += f"{roles[i].mention}:`{roles_amounts[i]}`\n"

    except Exception as e:
        formatted_string = f"Error retrieving these metrics: {e}"

    return formatted_string


"""
Role-specific metrics:
"""


async def display_role_check(context):

    roles = _get_list_of_roles_to_compare(context)
    all_members_with_roles = _get_full_role_member_dict(roles)
    all_members_with_reactions = await _get_full_member_reaction_dict(context)
    members_missing_role = _get_members_missing_role(context, all_members_with_roles, all_members_with_reactions)

    embed = discord.Embed(title=" ",
                          description="`Description`: The following users are missing the following roles. This means the bot failed to give out these roles, and should be manually re-added to each member.\n",
                          color=0xff961f)
    embed.set_author(name="Bot Failure Report - Role Check")
    running_failure_total = 0

    for role, member_list in members_missing_role.items():

        mentioned_members = [member.mention for member in member_list]
        str_member_list = utils.remove_list_characters(mentioned_members)
        running_failure_total += len(member_list)

        embed.add_field(name=f"Total: {len(member_list)}",
                        value=f"{role.mention}\n\n{str_member_list}",
                        inline=True)

    embed.set_footer(text=f"Total failures: {running_failure_total} {utils.get_bool_symbols(not running_failure_total)}")
    await context.send(embed=embed)


"""
Role-specific metric utilities:
"""


def _get_list_of_roles_to_compare(context):

    """
    :return: List of Discord role objects that we want to check
    This could change in complexity/size down the line, so it's
    best to abstract this in another function
    """

    # TODO: Maybe pass a list of role arguments in here instead?

    roles_to_check = [discord.utils.get(context.guild.roles, name=_role) for _role in config['role-games'].values()]
    roles_to_check += [discord.utils.get(context.guild.roles, name=_role) for _role in config['role-events'].values()]
    roles_to_check.append(discord.utils.get(context.guild.roles, name=config['role']['authed']))  # Only need this 1
    return roles_to_check


def _get_full_role_member_dict(roles: list):

    """
    :param roles: A list of all of the roles we want to look at
    :return: a dict of all guild members currently containing
    the role in the format: {discord_role_object, [members]}
    """

    all_members_w_role = {}

    for role in roles:
        members_with_role = utils.get_members_with_role(role)
        all_members_w_role[role.name] = members_with_role

    return all_members_w_role


async def _get_full_member_reaction_dict(context):

    """
    :return: a dict of all guild members having reacted
    to a subset of reactions we want to look at
    {a string role name (not a Discord object), [members reacted]}
    """

    all_members_w_reaction = {}

    game_selection_channel = utils.get_game_selection_channel(context.guild)
    game_selection_message = await utils.get_last_message_from_channel(game_selection_channel)
    event_subs_channel = utils.get_event_subscriptions_channel(context.guild)
    event_subs_message = await utils.get_last_message_from_channel(event_subs_channel)
    landing_channel = utils.get_landing_channel(context.guild)
    landing_message = await utils.get_last_message_from_channel(landing_channel)
    desired_reactions = game_selection_message.reactions + event_subs_message.reactions + landing_message.reactions

    for reaction in desired_reactions:

        try:
            role_name = reaction.emoji.name
        except AttributeError:
            # TODO: Fixed the following hardcoded code if
            #  emojis are using built in discord emojis
            if reaction.emoji == config['emoji']['authed']:
                role_name = config['role']['authed']
            elif reaction.emoji == config['emoji-events']['tuesdaygamenight']:
                role_name = config['role-events']['tuesdaygamenight'].replace(" ", "")
            else:
                continue

        users_with_reaction = await reaction.users().flatten()
        all_members_w_reaction[role_name] = users_with_reaction

    return all_members_w_reaction


def _get_members_missing_role(context, all_members_with_roles: dict, all_members_with_reactions: dict):

    """
    :param all_members_with_roles: These role keys contain spaces
    :param all_members_with_reactions: These reaction keys do not contain spaces

    Or at least, if processed correctly, the above description should
    match that kind of output I describe, unless there's a more
    streamlined system I haven't thought of.

    See below notes for importance on role name matches for future comparisons
    :return: A dictionary of all members containing the following roles
    in the following format: {discord_role_object: [a list of missing members]}
    """

    """
    NOTE: Rename the reaction keys in reaction dict so we can
    easily perform role vs member comparisons, where the
    role names should be matching exactly.
    """

    for role in all_members_with_roles.keys():
        old_key = str(role).replace(" ", "").replace(":", "")
        all_members_with_reactions[role] = all_members_with_reactions.pop(old_key)

    """
    Now actually look for members who have reacted but
    are missing from a current specific role list
    """
    missing_member_roles = {}
    for role_reaction, reacted_members in all_members_with_reactions.items():
        temp_missing_members = []
        for reacted_member in reacted_members:

            if reacted_member.bot or reacted_member not in context.guild.members:
                continue

            # ---------------------------------------------------------------#
            elif reacted_member not in all_members_with_roles[role_reaction]:  #
                temp_missing_members.append(reacted_member)  #
            # ---------------------------------------------------------------#

        disc_role_obj = discord.utils.get(context.guild.roles, name=role_reaction)
        missing_member_roles[disc_role_obj] = temp_missing_members

    return missing_member_roles


async def display_ping_check(ctx_or_client):

    last_day_of_month = calendar.monthrange(datetime.today().year, datetime.today().month)[1]

    # TODO: Get announcements and leadership chat into config
    try:
        ping_channel = discord.utils.get(ctx_or_client.guild.channels, name="announcements")

        if datetime.today().day == last_day_of_month:
            report_channel = discord.utils.get(ctx_or_client.guild.channels, name="leadership-chat")
        else:
            report_channel = utils.get_bot_commands_channel(ctx_or_client.guild)

    # TODO: Fix up guild differentiation
    except AttributeError:
        guild = ctx_or_client.get_guild(int(config['id-guild']['id']))
        ping_channel = discord.utils.get(guild.channels, name="announcements")

        if datetime.today().day == last_day_of_month:
            report_channel = discord.utils.get(guild.channels, name="leadership-chat")
        else:
            report_channel = utils.get_bot_commands_channel(guild)

    first_day_of_month = datetime.today().replace(day=1)
    msgs = [msg async for msg in ping_channel.history(limit=100, before=None, after=first_day_of_month, around=None, oldest_first=None)]
    user_pings = {}
    total_pings = 0
    for msg in msgs:
        if "@everyone" in msg.content:
            total_pings += 1
            try:
                user_pings[msg.author] += 1
            except KeyError:
                user_pings[msg.author] = 1

    embed = discord.Embed(title=" ",
                          description=f"`Description`: The total of users who have pinged @everyone in {ping_channel.mention} since {calendar.month_name[datetime.today().month]} 1, {datetime.today().year}.",
                          color=0xff961f)
    embed.set_author(name="Ping Check - Report")
    embed.set_thumbnail(url="https://i.redd.it/4t5g9j86khp21.png")
    embed.set_footer(text=f"Total pings: {total_pings}")

    for user, pings in user_pings.items():
        embed.add_field(name=f"User total: {pings}", value=f"{user.mention}", inline=True)
    await report_channel.send(embed=embed)
