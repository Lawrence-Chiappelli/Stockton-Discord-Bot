from StocktonBotPackage.DevUtilities import configparser, gsheetsAPI
import discord
import os

"""
This module is an attempt to abtract 
each panel away from the main content.
"""

config = configparser.get_parsed_config()


async def send_help_panel(context, client):

    await context.message.delete()

    role_titles, \
        names, \
        emails, \
        colors, \
        user_ids, \
        descriptions, \
        footers \
        = gsheetsAPI.get_sheet_help_directory_contact_cards()

    for i, role_title in enumerate(role_titles):
        member = discord.utils.get(context.message.guild.members, id=int(user_ids[i]))
        embed = discord.Embed(title=names[i],
                              description=descriptions[i],
                              color=int(colors[i], 16))
        embed.set_author(name=role_titles[i])
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="`Discord Contact:`",
                        value=member.mention,
                        inline=True)
        embed.add_field(name="`Email Contact:`",
                        value=f"**{emails[i]}**",
                        inline=True)
        embed.set_footer(text=f"{footers[i]} {member.name}")
        await context.send(embed=embed)

    embed = discord.Embed(
        title="A comprehensive list of leadership roles and their responsibilities, to help you get your answers from the most appropriate individual.",
        description="`🔼 Specific student leaders are listed further up! 🔼`",
        color=int("ffce47", 16)
    )  # Yellow
    embed.set_author(name="❓ Help directory")
    embed.set_thumbnail(url="https://icons-for-free.com/iconfiles/png/512/folder-131964753094019398.png")
    embed.add_field(name="👑 President",
                    value="Student President of Stockton eSports. Liaison between Students and Staff.", inline=False)
    embed.add_field(name="👥 Community Manager",
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
    embed.add_field(name="🖥️ Bot Developer", value="Develops and maintains the Discord bot used in this server.",
                    inline=False)
    embed.set_footer(
        text="🔼 Up above contains roles and responsibility directly specific to our Esports program. 🔼")
    await context.send(embed=embed)


async def send_gm_panel(client, context):

    await context.message.delete()

    current_message_channel_name = context.channel.name
    role_titles, \
        names, \
        emails, \
        colors, \
        user_ids, \
        descriptions, \
        channel_names, \
        icon_links \
        = gsheetsAPI.get_gm_info()

    for i, channel_name in enumerate(channel_names):

        if channel_name == current_message_channel_name:

                emoji = discord.utils.get(context.guild.emojis, name=str(channel_name).capitalize())

                role_gm = discord.utils.get(context.guild.roles, name="Game Manager")  # TODO: Allow for config
                role_game_name = str(channel_name).replace("-", " ").title().replace("Of", "of").replace("Fifa", "FIFA").replace("Csgo", "CS:GO")  #TODO: Better setup
                role_game = discord.utils.get(context.guild.roles, name=role_game_name)

                if names[i] == "n/a" or names[i] == "" or names[i] is None:

                    print(f"Help wanted. Found Names[i] to be: {names[i]}")

                    help_directory_name = gsheetsAPI.get_help_directory_channel_name()
                    help_directory_channel = discord.utils.get(context.guild.channels, name=help_directory_name)

                    names[i] = "Help wanted!"
                    emails[i] = "N/A"
                    member_name = f"See {help_directory_channel.mention}"
                    description = f"We are currently looking for **{role_gm.mention}s** for the game title **{role_game.mention}**!"
                    url = ""
                else:
                    member = discord.utils.get(context.guild.members, id=int(user_ids[i]))
                    member_name = member.mention
                    description = f"Looking for the **{role_game.mention}** **{role_gm.mention}**? Please message me!"
                    url = member.avatar_url

                embed = discord.Embed(title=f"{names[i]}",
                                      description=f"{description}",
                                      color=int(colors[i], 16))
                embed.set_author(name=f"{role_titles[i]}",
                                 icon_url=icon_links[i])
                embed.set_thumbnail(url=url)
                embed.add_field(name=f"`Discord Contact:`",
                                value=f"{member_name}",
                                inline=True)
                embed.add_field(name=f"`Email Contact:`",
                                value=f"**{emails[i]}**",
                                inline=True)
                await context.send(embed=embed)
                break
