from StocktonBotPackage.DevUtilities import configutil
import discord
import re

config = configutil.get_parsed_config()

# Generic Discord-related utilities:


def get_num_members_with_role(role: discord.Role):

    num_members_with_role = 0
    for member in role.guild.members:
        if role in member.roles and not member.bot:
            num_members_with_role += 1

    return num_members_with_role


def get_members_with_role(role: discord.Role):

    members_with_roles = []
    for member in role.guild.members:
        if role in member.roles:
            members_with_roles.append(member)

    return members_with_roles


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


async def get_last_message_from_channel(channel: type(discord.TextChannel)):

    """
    :param channel: The channel to search in

    :return: last message
    """

    try:
        last_message = [msg async for msg in channel.history(limit=1)].pop()
    except Exception:
        return None

    return last_message


async def get_messages_from_channel(channel: type(discord.TextChannel), limit: int):

    """
    :param channel: The channel to search in
    :param limit: The channel history limit
    :return: list of messages
    """

    try:
        messages = [msg async for msg in channel.history(limit=limit)]
    except Exception as e:
        return e

    return messages


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
        if "of" in converted_name:  # space before the 'of' in League of Legends or Call of Duty
            converted_name = str(converted_name).replace("of", " of")
        elif "Of" in converted_name:  # Capital Of's don't need spacing for some reason
            converted_name = str(converted_name).replace("Of", "of")

    return converted_name

# Generic miscellaneous utilities:


def remove_list_characters(some_list: list):

    """

    :param some_list:
    :return: The list as a string without the
    default list characters [, [, `, and ,.
    """

    return str(some_list).replace('[', '').replace(']', '').replace(',', '').replace("'", "")


def get_bool_symbols(a_boolean):
    """
    :param a_boolean: Any boolean representation
    :return: Symbols corresponding the to the
    True or False value of some boolean representation

    Motivation: this is reused on multiple occasions
    """

    if a_boolean:
        return "✅"
    return "❌"


def get_online_symbols(a_boolean):
    if a_boolean:
        return "Online"
    return "Offline"


"""
Channels:
"""


def get_landing_channel(guild: type(discord.Guild)):

    """
    :param guild: The guild to search in. Also supports
    passing in a client object! (But not explicitly
    specified for the sake of simplicity)

    Motivation: In some rare cases, it's impossible to have
    a guild object ready to search in. It's completely
    acceptable to pass in a client object if we
    have to search that way.

    :return: The channel after finding the given name
    and using the provided method by the user.

    I cannot guarantee anything if the user renames or
    deletes the channel. I've exercised all possible
    options to account for human adjustments or errors,
    so if a channel is None, it returns None. Exceptions
    are not raised by default with this. It simply is
    what it is.
    """

    try:
        name = config['channel']['landing']
    except KeyError:
        return None

    return get_channel_by_method(guild, name)


def get_bot_commands_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    try:
        name = config['channel']['botcommands']
    except KeyError:
        return None

    return get_channel_by_method(guild, name)


def get_audit_log_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    try:
        name = config['channel']['auditlogs']
    except KeyError:
        return None
    return get_channel_by_method(guild, name)


def get_game_selection_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    try:
        name = config['channel']['gameselection']
    except KeyError:
        return None
    return get_channel_by_method(guild, name)


def get_event_subscriptions_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    try:
        name = config['channel']['eventsubscriptions']
    except KeyError:
        return None
    return get_channel_by_method(guild, name)


def get_welcome_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    try:
        name = config['channel']['welcome']
    except KeyError:
        return None
    return get_channel_by_method(guild, name)


def get_social_media_feed_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    try:
        name = config['channel']['socialmediafeed']
    except KeyError:
        return None
    return get_channel_by_method(guild, name)


def get_game_lab_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    try:
        name = config['channel']['gamelabavailability']
    except KeyError:
        return None
    return get_channel_by_method(guild, name)


def get_faq_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    try:
        name = config['channel']['faq']
    except KeyError:
        return None
    return get_channel_by_method(guild, name)


def get_help_directory_channel(guild: (type(discord.Guild), (type(discord.Client())))):

    try:
        name = config['channel']['helpdirectory']
    except KeyError:
        return None
    return get_channel_by_method(guild, name)


"""
Info related, not channels:
"""


def get_help_directory_info():

    sections = [config[sec] for sec in config.sections() if str(sec).startswith('contact-info-')]
    as_dict = _get_user_formatted_dict_from_sections(sections)

    """        
    Info index positions within 
    the dict are as follows,
    specific to this setup.

    0 = role titles 
    1 = names
    2 = emails
    3 = colors
    4 = user id
    5 = description
    6 = footers
    """

    return as_dict


def get_game_manager_info():

    sections = [config[sec] for sec in config.sections() if str(sec).startswith('gm-info-')]
    as_dict = _get_user_formatted_dict_from_sections(sections)
    return as_dict


def get_calendar_info():

    """
    0 = calendar link
    1 = calendar image link
    2 = embed color
    :return: list of calendar data
    """

    return [info for info in config['calendar'].items()]


def get_faq_and_a():

    """
    0 = question
    1 = answer

    :return: list of questions and answers
    """

    return [q_and_a for q_and_a in config['faq'].items()]


def get_event_subscription_info():

    """
    0 = roles
    1 = emojis
    2 = descriptions


    :return: a tuple of tuples of role names, emojis,
    and descriptions

    Align indexes if you need matching event info
    """

    roles = [role_name for role_name in config['role-events'].values()]
    emojis = [emoji for emoji in config['emoji-events'].values()]
    descs = [desc for desc in config['description-events'].values()]
    as_tuple = (roles, emojis, descs)

    return as_tuple


def get_channel_by_method(method, name):

    """
    :param method: The method used to find the channel
    For now, only supports discord client and guild
    :param name: The name as determined by the preceding function
    :return: The channel with the given method
    """

    if isinstance(method, type(discord.Client())):  # Client
        return discord.utils.get(method.get_all_channels(), name=name)
    elif isinstance(method, discord.guild.Guild):  # Guild
        return discord.utils.get(method.channels, name=name)  # Warning can be ignored
    else:
        raise AssertionError(f"Could not find channel {name} with the following provided method '{method}' of type {type(method)}:")


def _get_user_formatted_dict_from_sections(sections: list):

    """
    :param sections: A list of config sections
    :return: A dictionary in a nicely formatted
    structure that accommodates sending embedded
    Discord data in quick succession.

    Note: when using list comprehension on the
    config sections, I could not access individual
    list section items with config[sec].items(),
    despite checking with manual / forced iterations.

    That's why there's a somewhat weird looking
    set of iterations below, which could have been
    somewhat avoided if I had access to the section
    item data directly.
    """

    as_dict = {}  # in format of: {int(ID): list(data)}
    for section in sections:
        for id_, item in section.items():
            as_dict.setdefault(int(id_), []).append(item)

    """
    This structures the dict such that we get an ID,
    and that ID is associated with a list of that
    specific user's information. I would have added
    data to the dict differently if the config
    was stored slightly differently. 
    
    There's trade offs between storing the config
    data as row-based vs column-based.
    """

    return as_dict

