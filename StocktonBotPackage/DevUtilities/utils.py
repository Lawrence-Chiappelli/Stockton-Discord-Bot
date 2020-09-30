from StocktonBotPackage.DevUtilities import configparser, gsheetsAPI
import discord
import re

config = configparser.get_parsed_config()


def get_num_members_with_role(role):

    num_members_with_role = 0
    for member in role.guild.members:
        if role in member.roles and not member.bot:
            num_members_with_role += 1

    return num_members_with_role


def get_codebase_owner_member(guild):

    """
    :param guild: The guild to search in
    :return: The codebase owner (will return
    helpful information if something goes wrong)
    """

    try:
        owner = discord.utils.get(guild.members, id=int(config['id']['owner']))
    except Exception as e:
        owner = f"`No codebase owner found: {e}`\n"

    return owner


def convert_custom_emoji_name_to_role_name(emoji):

    """
    :param emoji: name of emoji to convert
    :return: converted name

    This method is based on an internal
    naming conventional, may or may not
    be applicable to all situations
    """

    if str(emoji).isupper():
        if "SG" in str(emoji):
            converted_name = str(emoji).replace("SG", "S:G")  # Insert colon for CS:GO
        else:
            converted_name = str(emoji)  # And ignore if FIFA or otherwise all caps

    else:
        converted_name = re.sub(r"(\w)([A-Z])", r"\1 \2", str(emoji))
        if "of" in converted_name:  # space before the 'of' in League of Legends
            converted_name = str(converted_name).replace("of", " of")

    return converted_name


def get_landing_channel(guild: type(discord.Guild)):

    """
    :param guild: The guild to search in. Also technically
    works if passing in a client object!
    :return: The channel after finding the given name
    and using the provided method by the user.

    Motivation: In some rare cases, it's impossible to have
    a guild object ready to search in. It's completely
    acceptable to pass in a client object if we
    have to search that way.

    Furthermore, if there's an issue trying to find the
    channel name with the Google Sheets API, we can
    just revert to the default hardcoded names.

    I cannot guarantee anything if the user renames or
    deletes the channel. I've exercised all possible
    options to account for human adjustments or errors,
    so if a channel is None, it returns None. Exceptions
    are not raised by default with this.
    """

    name = gsheetsAPI.SheetChannels().get_landing_channel_name()
    if name is None:
        name = config['channel']['landing']

    return get_channel_by_method(guild, name)


def get_bot_commands_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    name = gsheetsAPI.SheetChannels().get_bot_commands_channel_name()
    if name is None:
        name = config['channel']['botcommands']

    return get_channel_by_method(guild, name)


def get_audit_log_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    name = gsheetsAPI.SheetChannels().get_audit_logs_channel_name()
    if name is None:
        name = config['channel']['auditlogs']

    return get_channel_by_method(guild, name)


def get_game_selection_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    name = gsheetsAPI.SheetChannels().get_game_selection_channel_name()
    if name is None:
        name = config['channel']['gameselection']

    return get_channel_by_method(guild, name)


def get_event_subscriptions_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    name = gsheetsAPI.SheetChannels().get_event_subscriptions_channel_name()
    if name is None:
        name = config['channel']['eventsubscriptions']

    return get_channel_by_method(guild, name)


def get_welcome_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    name = gsheetsAPI.SheetChannels().get_welcome_channel_name()
    if name is None:
        name = config['channel']['welcome']

    return get_channel_by_method(guild, name)


def get_social_media_feed_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    name = gsheetsAPI.SheetChannels().get_social_media_feed_channel_name()
    if name is None:
        name = config['channel']['socialmediafeed']

    return get_channel_by_method(guild, name)


def get_game_lab_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    name = gsheetsAPI.SheetChannels().get_game_lab_channel_name()
    if name is None:
        name = config['channel']['game-lab-availability']

    return get_channel_by_method(guild, name)


def get_faq_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    name = gsheetsAPI.SheetChannels().get_faq_channel_name()
    if name is None:
        name = config['channel']['faq']

    return get_channel_by_method(guild, name)


def get_help_directory_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    name = gsheetsAPI.SheetChannels().get_help_directory_channel_name()
    if name is None:
        name = config['channel']['helpdirectory']

    return get_channel_by_method(guild, name)


def get_channel_by_method(method, name):

    """
    :param args: The method used to find the channel
    :param name: The name as determined by the preceding function
    :return: The channel with the given method
    """

    if isinstance(method, type(discord.Client())):  # Client
        return discord.utils.get(method.get_all_channels(), name=name)
    elif isinstance(method, discord.guild.Guild):  # Guild
        return discord.utils.get(method.channels, name=name)  # Warning can be ignored
    else:
        raise AssertionError(f"Could not find channel with the following provided method '{method}' of type {type(method)}:")
