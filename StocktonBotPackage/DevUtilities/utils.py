from StocktonBotPackage.DevUtilities import configparser
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
