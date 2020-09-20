from StocktonBotPackage.DevUtilities import configparser, utils, gsheetsAPI
import discord
import asyncio

# ------------------------------------------
config = configparser.get_parsed_config()  #
# ------------------------------------------


async def find_reaction_function(emoji, channel, member, is_add=True):

    """
    :param emoji: The emoji reacted to
    :param channel: The channel reacted in
    :param member: The member that reacted
    :param is_add: Determines whether to
    add / remove reaction / role
    Default: True (reason: users always
    initially add reactions)
    :return: None
    """

    if isinstance(emoji, discord.partial_emoji.PartialEmoji):  # Convert the emoji, if custom
        emoji = emoji.name

    if _is_member_authenticating(emoji, channel):
        await _authenticate_member(member, channel)

    elif _is_moderator_auditing(emoji, channel):  # TODO: Will not work for messages deleted in quick succession
        await _audit_member(member, channel)

    elif _is_assigning_game_role(emoji, channel):
        await _assign_game_role(member, emoji, is_add)

    elif _is_assigning_event_role(emoji, channel):
        await _assign_event_role(member, emoji, is_add)

    else:
        print(F"No function found! ({member.name} reacted in channel {channel.name})")

    return None


async def _authenticate_member(member, channel):

    message, embed = await _get_msg_and_embed(channel)
    auth_role = discord.utils.get(member.guild.roles, name=config['role']['authed'])
    await member.add_roles(auth_role)

    await asyncio.sleep(1)
    embed.set_field_at(index=1, name=f"Users Authorized:", value=utils.get_num_members_with_role(auth_role), inline=True)
    await message.edit(embed=embed)


async def _audit_member(member, channel):

    message, embed = await _get_msg_and_embed(channel)
    embed.description = member.mention   # TODO: Get field value index 0
    await message.edit(embed=embed)


async def _assign_game_role(member, emoji, is_add):

    converted_name = utils.convert_custom_emoji_name_to_role_name(str(emoji))
    game_role = discord.utils.get(member.guild.roles, name=converted_name)

    if is_add and game_role not in member.roles:
        await member.add_roles(game_role)
    else:
        if game_role in member.roles:
            await member.remove_roles(game_role)


async def _assign_event_role(member, emoji, is_add):

    event_role_names, event_emojis, _ = gsheetsAPI.get_event_subscriptions()
    """
    For built-in emojis, we have to iterate through
    our list of wanted emojis and extract
    the corresponding role name
    """

    matching_role_name = None
    for i, event_role_name in enumerate(event_role_names):
        if str(emoji) == event_emojis[i]:
            matching_role_name = event_role_name
            break

    if matching_role_name is None:
        return None

    event_role = discord.utils.get(member.guild.roles, name=matching_role_name)
    if is_add and event_role not in member.roles:
        await member.add_roles(event_role)
    else:
        if event_role in member.roles:
            await member.remove_roles(event_role)


async def _get_msg_and_embed(channel):

        message = [msg async for msg in channel.history(limit=1)].pop()
        embed = message.embeds[0]
        return message, embed


def _is_member_authenticating(emoji, channel):

    auth_emoji = config['emoji']['authed']
    auth_channel = gsheetsAPI.get_landing_channel_name()

    if str(emoji) == auth_emoji and str(channel) == auth_channel:
        return True
    return False


def _is_moderator_auditing(emoji, channel):

    audit_emoji = config['emoji']['audit']
    author_emoji = config['emoji']['author']
    audit_channel = gsheetsAPI.get_audit_logs_channel_name()

    if (str(emoji) == audit_emoji or str(emoji) == author_emoji) and str(channel) == audit_channel:
        return True
    return False


def _is_assigning_game_role(emoji, channel):

    game_emojis = dict(config.items('emoji-games'))  # TODO: Why dict?
    gameselection_channel = gsheetsAPI.get_game_selection_channel_name()

    if str(emoji) in game_emojis.values() and str(channel) == gameselection_channel:
        return True
    return False


def _is_assigning_event_role(emoji, channel):

    events_channel = gsheetsAPI.get_event_subscriptions_channel_name()
    _, event_emojis, _ = gsheetsAPI.get_event_subscriptions()  # TODO: Weigh options (rate limit usage vs readability)

    if str(emoji) in event_emojis and str(channel) == events_channel:  # Event emojis here is list and not dict
        return True
    return False
