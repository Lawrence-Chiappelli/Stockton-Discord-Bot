from StocktonBotPackage.DevUtilities import configutil, utils
import discord


config = configutil.get_parsed_config()


async def send_help_panel(context):

    await context.message.delete()
    contact_info = utils.get_help_directory_info()

    for user_id, info in contact_info.items():

        """
        0 = role titles
        1 = names
        2 = emails
        3 = colors
        4 = userids
        5 = descriptions
        6 = footers
        """

        embed = discord.Embed(title=info[1],
                              description=info[5],
                              color=int(info[3], 16))

        member = discord.utils.get(context.message.guild.members, id=int(info[4]))
        embed.set_author(name=info[0])
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="`Discord Contact:`",
                        value=member.mention,
                        inline=True)
        embed.add_field(name="`Email Contact:`",
                        value=f"**{info[2]}**",
                        inline=True)
        embed.set_footer(text=f"{info[6]} {member.name}")
        await context.send(embed=embed)

    # These are intentionally hardcoded:
    embed = discord.Embed(
        title="A comprehensive list of leadership roles and their responsibilities, to help you get your answers from the most appropriate individual.",
        description="`🔼 Specific student leaders are listed further up! 🔼`",
        color=int("ffce47", 16)
    )  # Yellow
    embed.set_author(name="📂 Leadership directory")
    embed.set_thumbnail(url="https://icons-for-free.com/iconfiles/png/512/folder-131964753094019398.png")
    embed.add_field(name="👑 President",
                    value="Student President of Stockton eSports. Liaison between Students and Staff.", inline=False)
    embed.add_field(name="👥 Esports Coordinator ",
                    value="Liaison between the Staff Leadership and Student Leaders. Also keeps open lines of communication with the heads of each individual game.",
                    inline=False)
    embed.add_field(name="🤝 Partnerships Manager",
                    value="Contacts and negotiates partnerships and sponsorships with outside organizations.",
                    inline=False)
    embed.add_field(name="🏆 Competitive Coordinator",
                    value="Liaison between competitive teams and outside organizations. Also maintains competitive rosters.",
                    inline=False)
    embed.add_field(name="👔 Marketing Manager", value="Delivers and produces marketing materials for events.",
                    inline=False)
    embed.add_field(name="⚙️ Technical Coordinater", value="Handles behind the scenes production.", inline=False)
    embed.add_field(name="🛠️️ Systems Engineer ", value="Handles on-site production and setup for events.",
                    inline=False)
    embed.add_field(name="🖥️ Software Developer", value="Develops and maintains the Discord bot used in this server.",
                    inline=False)
    embed.set_footer(
        text="🔼 Up above contains roles and responsibility directly specific to our Esports program. 🔼")
    await context.send(embed=embed)


async def send_game_manager_panel(context):

    """
    :param context: Command context
    :return: None

    Send out the game manager panel.
    """

    await context.message.delete()
    contact_info = utils.get_game_manager_info()
    print(f"Have contact info values?:\n{contact_info.values()}")

    def _a_gm_channel():

        nonlocal contact_info

        if context.channel.name in str(contact_info.values()):  # Had to cast to str
            return True
        return False

    for user_id, info in contact_info.items():

        """
        0 = role titles
        1 = names
        2 = emails
        3 = colors
        4 = userids
        5 = descriptions
        6 = channel names (used for role)
        7 = icon links
        """

        if context.channel.name in contact_info[user_id] or not _a_gm_channel():

            """
            The latter condition will only execute if the current iteration
            is the intended channel the user wanted to type in.
            
            Granted, I could update all channels in one fell swoop, but for
            the sake of responsiveness, I'd rather the user be reassured
            nearly immediately based on their intuition. (It could very well
            take a long time for all channels to be updated, depends on how
            Discord wants to behave in general)
            """

            # Determining description:
            if info[5]:
                description = info[5]
            else:
                role_name = info[6].replace("-", " ").title().replace("Of", "of").replace("Fifa", "FIFA").replace("Csgo", "CS:GO")
                role = discord.utils.get(context.guild.roles, name=role_name)
                role_gm = discord.utils.get(context.guild.roles, name=config['role']['gamemanager'])
                description = f"Looking for the **{role.mention}** **{role_gm.mention}**? Please message me!"

            # Adjusting embed data as usual
            embed = discord.Embed(title=info[1],
                                  description=description,
                                  color=int(info[3], 16))

            member = discord.utils.get(context.message.guild.members, id=int(info[4]))
            embed.set_author(name=info[0],
                             icon_url=info[7])
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="`Discord Contact:`",
                            value=member.mention,
                            inline=True)
            embed.add_field(name="`Email Contact:`",
                            value=f"**{info[2]}**",
                            inline=True)

            if _a_gm_channel():
                gm_channel = context.channel
            else:
                gm_channel = discord.utils.get(context.guild.channels, name=info[6])

            bot_channel = utils.get_bot_commands_channel(context.guild)
            last_message = await utils.get_last_message_from_channel(gm_channel)
            if last_message:
                await last_message.edit(embed=embed)
                await bot_channel.send(f"✅ Finished editing contact details in {gm_channel.mention} for Game Manager {member.mention}")
            else:
                await context.send(embed=embed)
                await bot_channel.send(f"✅ Finished creating new contact details in {gm_channel.mention} for Game Manager {member.mention}")