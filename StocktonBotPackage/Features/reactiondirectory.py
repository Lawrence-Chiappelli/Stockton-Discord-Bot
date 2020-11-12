from StocktonBotPackage.DevUtilities import configutil, utils
import discord
import asyncio

# ---------------------------------------#
config = configutil.get_parsed_config()  #
# ---------------------------------------#


async def find_reaction_function(emoji, channel, member, message, is_add=True):

    """
    :param emoji: The emoji reacted to
    :param channel: The channel reacted in
    :param member: The member that reacted
    :param message: the message object belonging to the reaction
    :param is_add: Determines whether to
    add / remove reaction / role

    Default: True (reason: users always
    initially add reactions)

    Do NOT search through spreadsheet for data- store them
    before doing so as to not burn through rate limits.

    :return: None
    """

    if isinstance(emoji, discord.partial_emoji.PartialEmoji):  # Grab the name of the custom emoji
        emoji = emoji.name

    if _is_member_authenticating(channel, emoji):
        await _authenticate_member(member, message, is_add)

    elif _is_moderator_auditing(channel, emoji):
        await _audit_member(member, emoji, message, is_add)

    elif _is_assigning_game_role(emoji, channel):
        await _assign_game_role(member, emoji, is_add)

    elif _is_assigning_event_role(emoji, channel):
        await _assign_event_role(member, emoji, is_add)

    else:

        if is_add:
            print(F"No function found! ({member.name} reacted to {emoji} in channel {channel.name})")
        else:
            print(F"No function found! ({member.name} unreacted from {emoji} in channel {channel.name})")

    return None


async def debug_reaction(emoji, channel, member, is_add=True):

    """
    :param emoji: The emoji the user reacted with
    :param channel: The channel the user reacted inside of
    :param member: The member that did the reactiobn
    :return: None

    Ideally, this should only execute if the user
    is reacting under personally designated environment
    (channel compared to emoji) matches.
    """

    bot_channel = utils.get_bot_commands_channel(member.guild)
    owner = utils.get_codebase_owner_member(member.guild)

    if is_add:
        await bot_channel.send(f"{owner.mention}, member `{member}` reacted to {emoji} in {channel.mention}")
    else:
        await bot_channel.send(f"{owner.mention}, member `{member}` unreacted from {emoji} in {channel.mention}")


async def _authenticate_member(member, message, is_add):

    if not is_add:
        return

    embed = message.embeds[0]
    auth_role = discord.utils.get(member.guild.roles, name=config['role']['authed'])
    await member.add_roles(auth_role)

    await asyncio.sleep(1)
    embed.set_field_at(index=1, name=f"Users Authorized:", value=utils.get_num_members_with_role(auth_role), inline=True)
    await message.edit(embed=embed)


async def _audit_member(member, emoji, message, is_add):

    """
    :param emoji: The emoji the user reacted with
    :param member: The member doing the reacting
    :param message: The message belong to the reaction
    :param is_add: Action to take if reaction is raw add
    :return: None

    Simply edits in the name of the user
    who deleted the message- that being
    the person who reacted, or the
    author being specified in the embed
    """

    if not is_add:  # For now, nothing special needs to occur if reaction is remove
        return

    embed = message.embeds[0]

    if emoji == config['emoji']['audit']:
        embed.description = f'`{member}`'
    else:
        embed.description = "`Self deleted by author`"

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

    event_emojis = [emoji_ for emoji_ in config['emoji-events'].values()]
    event_role_names = [emoji_ for emoji_ in config['role-events'].values()]

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


def _is_member_authenticating(channel, emoji):

    auth_emoji = config['emoji']['authed']
    auth_channel = config['channel']['landing']

    if channel.name == auth_channel:
        print(F"Channel.name {channel.name} is auth channel {auth_channel}")

    if str(emoji) == auth_emoji and channel.name == auth_channel:
        return True
    return False


def _is_moderator_auditing(channel, emoji):

    audit_emoji = config['emoji']['audit']  # Not externally configurable
    author_emoji = config['emoji']['author']  # Also not externally congiruable
    audit_channel = config['channel']['auditlogs']

    if (str(emoji) == audit_emoji or str(emoji) == author_emoji) and channel.name == audit_channel:
        return True
    return False


def _is_assigning_game_role(emoji, channel):

    game_emojis = [emoji_ for emoji_ in config['emoji-games'].values()]
    gameselection_channel = config['channel']['gameselection']

    if str(emoji).replace("Of", "of") in game_emojis and channel.name == gameselection_channel:
        return True
    return False


def _is_assigning_event_role(emoji, channel):

    event_emojis = [emoji_ for emoji_ in config['emoji-events'].values()]
    events_channel = config['channel']['eventsubscriptions']

    if str(emoji) in event_emojis and channel.name == events_channel:  # Event emojis here is list and not dict
        return True
    return False
