from StocktonBotPackage.DevUtilities import configutil, utils
import discord


config = configutil.get_parsed_config()


def is_bot_reaction_function(emoji, channel):

    """
    :param emoji: emoji reacted to
    :param channel: channel containing reaction
    :return: True (if this is a valid custom bot function)
    False (if just a generic reaction)

    This is to help make the distinction between generic
    user reactions and ones that are intended to perform
    additional functionality.
    """

    # Making comparisons easier to read:
    if isinstance(emoji, discord.partial_emoji.PartialEmoji):  # If custom emoji, its name takes a little more work to extract
        emoji = str(emoji.name).replace("Of", "of")  # For emojis that have capital of's, and would rather keep the emoji count
    elif not isinstance(emoji, str):
        emoji = str(emoji)

    if not isinstance(channel, str):
        channel = str(channel)

    all_channel_names = [name for name in config['channel'].values()]
    if channel not in all_channel_names:
        return False

    """
    Meeting a channel condition is one requirements- we need to actually
    verify if the user's reaction is a valid one, so we don't burn
    through our sparse rate limits:
    """

    emojis_discord_default = [emoji_ for emoji_ in config['emoji'].values()]  # emoji_ prevents shadowing
    if emoji in emojis_discord_default:
        return True

    emoji_games = [emoji_ for emoji_ in config['emoji-games'].values()]
    if emoji in emoji_games:
        return True

    emoji_events = [emoji_ for emoji_ in config['emoji-events'].values()]
    if emoji in emoji_events:
        return True

    return False


async def validate_pc_availability_embeds(client):

    """
    :param client: Discord client object
    :return: True if the PC availability embeds exist
    """

    channel = utils.get_game_lab_channel(client)

    try:
        messages = [msg async for msg in channel.history(limit=int(config['lab']['num_rooms']))].pop()
    except IndexError:  # Meaning the channel is empty
        return False

    embed = messages.embeds[0]
    if channel and embed:
        return True

    return False
