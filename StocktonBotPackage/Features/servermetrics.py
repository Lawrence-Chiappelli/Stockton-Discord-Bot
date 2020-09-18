import discord
import time
from StocktonBotPackage.DevUtilities import utils, configparser, gsheetsAPI
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

    # TODO: Iterate through roles instead and unpack accordingly

    authed_role = discord.utils.get(context.guild.roles, name=config['role']['authed'])
    admin_role = discord.utils.get(context.guild.roles, name=config['role']['admin'])
    admini_role = discord.utils.get(context.guild.roles, name=config['role']['admini'])
    moderator_role = discord.utils.get(context.guild.roles, name=config['role']['moderator'])
    leadership_role = discord.utils.get(context.guild.roles, name=config['role']['leadershipstaff'])
    gamemanager_role = discord.utils.get(context.guild.roles, name=config['role']['gamemanager'])
    
    apex_role = discord.utils.get(context.guild.roles, name=config['role-games']['apex'])
    csgo_role = discord.utils.get(context.guild.roles, name=config['role-games']['csgo'])
    fifa_role = discord.utils.get(context.guild.roles, name=config['role-games']['fifa'])
    fortnite_role = discord.utils.get(context.guild.roles, name=config['role-games']['fortnite'])
    hearthstone_role = discord.utils.get(context.guild.roles, name=config['role-games']['hearthstone'])
    league_role = discord.utils.get(context.guild.roles, name=config['role-games']['league'])
    overwatch_role = discord.utils.get(context.guild.roles, name=config['role-games']['overwatch'])
    rocketleague_role = discord.utils.get(context.guild.roles, name=config['role-games']['rocketleague'])
    smash_role = discord.utils.get(context.guild.roles, name=config['role-games']['smash'])
    valorant_role = discord.utils.get(context.guild.roles, name=config['role-games']['valorant'])
    minecraft_role = discord.utils.get(context.guild.roles, name=config['role-games']['minecraft'])

    botdeveloper_role = discord.utils.get(context.guild.roles, name=config['role-other']['botdeveloper'])
    nitrobooster_role = discord.utils.get(context.guild.roles, name=config['role-other']['nitrobooster'])
    alumni_role = discord.utils.get(context.guild.roles, name=config['role-other']['alumni'])
    owner = discord.utils.get(context.guild.members, id=int(config['id']['owner']))

    await context.send("Getting metrics, please wait...")
    before = time.time()

    num_server_members = str(len(context.guild.members))
    num_authed = utils.get_num_members_with_role(authed_role)

    num_admin = utils.get_num_members_with_role(admin_role)
    num_admini = utils.get_num_members_with_role(admini_role)
    num_moderators = utils.get_num_members_with_role(moderator_role)
    num_leadership = utils.get_num_members_with_role(leadership_role)
    num_gamemanager = utils.get_num_members_with_role(gamemanager_role)

    num_apex = utils.get_num_members_with_role(apex_role)
    num_csgo = utils.get_num_members_with_role(csgo_role)
    num_fifa = utils.get_num_members_with_role(fifa_role)
    num_fortnite = utils.get_num_members_with_role(fortnite_role)
    num_hearthstone = utils.get_num_members_with_role(hearthstone_role)
    num_league = utils.get_num_members_with_role(league_role)
    num_overwatch = utils.get_num_members_with_role(overwatch_role)
    num_rocketleague = utils.get_num_members_with_role(rocketleague_role)
    num_smash = utils.get_num_members_with_role(smash_role)
    num_valorant = utils.get_num_members_with_role(valorant_role)
    num_minecraft = utils.get_num_members_with_role(minecraft_role)

    num_botdeveloper = utils.get_num_members_with_role(botdeveloper_role)
    num_nitrobooster = utils.get_num_members_with_role(nitrobooster_role)
    num_alumni = utils.get_num_members_with_role(alumni_role)

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

    after = time.time()
    embed = discord.Embed(color=0xff2424, description=f"For more info, please message {owner.mention}, an available {botdeveloper_role.mention} or {moderator_role.mention}!")
    embed.set_author(name="Server and API metrics")
    embed.add_field(name="# Authorized server members", value=f"`{num_authed}` / `{num_server_members}`", inline=False)
    embed.add_field(name="# Staff", value=f"{admin_role.mention}: `{num_admin}`\n{admini_role.mention}: `{num_admini}`\n{moderator_role.mention}: `{num_moderators}`\n{leadership_role.mention}: `{num_leadership}`\n{gamemanager_role.mention}: `{num_gamemanager}`", inline=False)
    embed.add_field(name="# Players", value=f"{apex_role.mention}: `{num_apex}`\n{csgo_role.mention}: `{num_csgo}`\n{fifa_role.mention}: `{num_fifa}`\n{fortnite_role.mention}: `{num_fortnite}`\n{hearthstone_role.mention}: `{num_hearthstone}`\n{league_role.mention}: `{num_league}`\n{overwatch_role.mention}: `{num_overwatch}`\n{rocketleague_role.mention}: `{num_rocketleague}`\n{smash_role.mention}: `{num_smash}`\n{valorant_role.mention}: `{num_valorant}`\n{minecraft_role.mention}: `{num_minecraft}`", inline=False)
    embed.add_field(name="# Other", value=f"{botdeveloper_role.mention}: `{num_botdeveloper}`\n{nitrobooster_role.mention}: `{num_nitrobooster}`\n{alumni_role.mention}: `{num_alumni}`", inline=False)
    embed.add_field(name="Twitter API rates", value=f"Rate checks: `{rate_checks}/180`\nTimeline: `{timeline_rates}/900`\nStream rates: `{id_rates}/900`", inline=False)
    embed.add_field(name="Twitter stream", value=f"Is streaming: {twitter_streaming}\nIs polling: {twitter_poll_status}\nError: `{twitter_error}`\nStatus: `{twitter_online_status}`", inline=False)
    embed.add_field(name="Twitter stream info", value=f"If not streaming: `!twitterstream`\nIf not polling: `!twitterpoll`\nIf error 420: `!twitterpoll` after __15__ minutes\nIf online & tweet missing: `!tweet`", inline=False)
    embed.add_field(name="Google Sheets API rates", value=f"Read / 100 secs: `100`\nRead / day: `unlimited`", inline=False)
    embed.add_field(name="Gaming lab stream", value=f"Is scraping: {gaming_lab_scraping}\nStatus: `{gsheets_rates}`", inline=False)
    embed.add_field(name="Gaming lab info", value=f"If not scraping: `!scrape`\nIf not updating: `!forceoff`\nLast resort: `Restart the bot`", inline=False)
    embed.set_footer(text=f"Metrics retrieved in {1000 * (after - before)} milliseconds.")

    await context.send(embed=embed)


def get_bool_symbols(bool):

    if bool:
        return "✅"
    return "❌"


def get_online_symbols(bool):

    if bool:
        return "Online"
    return "Offline"