import discord
from StocktonBotPackage.DevUtilities import configparser

config = configparser.get_parsed_config()


def is_bot_reaction_function(emoji, channel):

    """
    :param emoji: emoji reacted to
    :param channel: channel containing reaction
    :return: True (if this is a valid custom bot function)
    False (if just a generic reaction)

    This is to help make the distinction between general
    user reactions and ones that are intended to perform
    additional functionality.
    """

    bot_channels = dict(config.items('channel'))
    bot_emojis = dict(config.items('emoji'))

    if isinstance(emoji, discord.partial_emoji.PartialEmoji):  # If custom emoji, the name needs to be grabbed
        emoji = str(emoji.name)
    elif not isinstance(emoji, str):
        emoji = str(emoji)

    if not isinstance(channel, str):
        channel = str(channel)

    if channel in bot_channels.values() and emoji in bot_emojis.values():
        return True

    return False


async def machine_availabilty_embed_exists(client):

    game_lab_channel_name = config['channel']['gamelabavailability']
    channel = discord.utils.get(client.get_all_channels(), name=game_lab_channel_name)

    try:
        messages = [msg async for msg in channel.history(limit=int(config['lab']['num_rooms']))].pop()
    except IndexError:  # Meaning the channel is empty
        return False

    embed = messages.embeds[0]
    if channel and embed:
        return True

    return False