from StocktonBotPackage.DevUtilities import configparser, gsheetsAPI
import discord


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

    bot_emojis = dict(config.items('emoji'))
    game_emojis = dict(config.items('emoji-games'))
    _, event_emojis, _ = gsheetsAPI.get_event_subscriptions()
    all_environment_channels = gsheetsAPI.SheetChannels()._get_all_channel_names()

    if isinstance(emoji, discord.partial_emoji.PartialEmoji):  # If custom emoji, the name needs to be grabbed
        emoji = str(emoji.name)
    elif not isinstance(emoji, str):
        emoji = str(emoji)

    if not isinstance(channel, str):
        channel = str(channel)

    if channel in all_environment_channels and (emoji in bot_emojis.values() or emoji in game_emojis.values() or emoji in str(event_emojis)):
        return True

    return False


async def machine_availabilty_embed_exists(client):

    try:
        game_lab_channel_name = gsheetsAPI.SheetChannels().get_game_lab_channel_name()
    except (NameError, Exception) as e:

        """
        Generally speaking, I'd like to use the channel name from
        Google sheets, but in the case it's down, it's critical
        that we look for a default name.
        """

        print(f"USING DEFAULT GAME LAB CHANNEL! Error:\n{e}")
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
