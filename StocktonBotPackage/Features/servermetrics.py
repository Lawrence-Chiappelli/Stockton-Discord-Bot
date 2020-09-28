import discord
import time
from StocktonBotPackage.DevUtilities import utils, configparser, gsheetsAPI, herokuAPI
from StocktonBotPackage.Features import twitterfeed, gamelabscraper

# -----------------------------------------#
config = configparser.get_parsed_config()  #
# -----------------------------------------#


async def display_metrics(context):

    """
    :param context: Needed for respective guild
    :return: None

    Retrieves the necessary metrics and sends
    it out in a visual interface all in one.
    """

    await context.send("Getting metrics, please wait...")

    # --------------------#
    before = time.time()  #
    # --------------------#

    # Title
    owner = utils.get_codebase_owner_member(context.guild)
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
    twitter_streaming = get_bool_symbols(twitterfeed.listener.is_streaming)
    twitter_poll_status = get_bool_symbols(twitterfeed.twitter_poller.is_polling)
    twitter_error = twitterfeed.listener.error
    if twitterfeed.listener.is_streaming and twitterfeed.twitter_poller.is_polling and twitter_error is None:
        twitter_online_status = get_online_symbols(True)
    else:
        twitter_online_status = get_online_symbols(False)

    gsheets_rates = get_online_symbols(gsheetsAPI.validate_resource_usage())
    gaming_lab_scraping = get_bool_symbols(gamelabscraper.scraper.is_scraping)

    embed = discord.Embed(color=0xff2424, description=f"For more info, please message {owner.mention}, an available {bot_dev_role.mention} or {moderator_role.mention}!")
    embed.set_author(name="📈 Server and API metrics 📉")
    embed.add_field(name="# Authorized server members", value=f"`{num_authed_members}` / `{num_server_members}`", inline=False)
    embed.add_field(name="# Staff", value=get_formatted_role_metrics(roles_staff, num_roles_staff), inline=False)
    embed.add_field(name="# Players", value=get_formatted_role_metrics(roles_games, num_roles_games), inline=False)
    embed.add_field(name="# Other", value=get_formatted_role_metrics(roles_other, num_roles_other), inline=False)
    embed.add_field(name="Twitter API rates", value=f"Rate limits: `{rate_checks}/180`\nTimeline rates: `{timeline_rates}/900`\nStream rates: `{id_rates}/900`", inline=False)
    embed.add_field(name="Twitter stream", value=f"Is streaming: {twitter_streaming}\nIs polling: {twitter_poll_status}\nError: `{twitter_error}`\nStatus: `{twitter_online_status}`", inline=False)
    embed.add_field(name="Twitter stream info", value=f"If not streaming: `!twitterstream`\nIf not polling: `!twitterpoll`\nIf error 420: `!twitterpoll` after __15__ minutes\nIf online & tweet missing: `!tweet`", inline=False)
    embed.add_field(name="Google Sheets API rates", value=f"Read / 100 secs: `100`\nRead / day: `unlimited`", inline=False)
    embed.add_field(name="Gaming lab stream", value=f"Is scraping: {gaming_lab_scraping}\nStatus: `{gsheets_rates}`", inline=False)
    embed.add_field(name="Gaming lab info", value=f"If not scraping: `!scrape`\nIf not updating: `!forceoff`\nLast resort: `Restart the bot`", inline=False)
    embed.add_field(name="Overall bot status", value=f"Heroku rates: `{herokuAPI.Heroku().get_rate_limits()}`\nApp run location: `{herokuAPI.Heroku().get_app_state()}`\nIf running locally: `Wait for Heroku push`", inline=False)

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
                # TODO: Consider better alternative for this

            if i >= len(roles):
                formatted_string += f"{roles[i].mention}:`{roles_amounts[i]}`"
            else:
                formatted_string += f"{roles[i].mention}:`{roles_amounts[i]}`\n"

    except Exception as e:
        formatted_string = f"Error retrieving these metrics: {e}"

    return formatted_string


def get_bool_symbols(bool):

    if bool:
        return "✅"
    return "❌"


def get_online_symbols(bool):

    if bool:
        return "Online"
    return "Offline"