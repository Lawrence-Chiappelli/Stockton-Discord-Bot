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

    help_dir_sheet = gsheetsAPI.get_sheet_help_directory_contact_cards()

    role_titles = help_dir_sheet.col_values(1)
    names = help_dir_sheet.col_values(2)
    emails = help_dir_sheet.col_values(3)
    colors = help_dir_sheet.col_values(4)
    user_ids = help_dir_sheet.col_values(5)
    descriptions = help_dir_sheet.col_values(6)
    footers = help_dir_sheet.col_values(7)

    del role_titles[0:4]  # Remove the headers I've added
    del names[0:4]
    del emails[0:4]
    del colors[0:4]
    del user_ids[0:4]
    del descriptions[0:4]
    del footers[0:4]

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
    gm_sheet = gsheetsAPI.get_sheet_gms()

    role_titles = gm_sheet.col_values(1)
    names = gm_sheet.col_values(2)
    emails = gm_sheet.col_values(3)
    colors = gm_sheet.col_values(4)
    user_ids = gm_sheet.col_values(5)
    descriptions = gm_sheet.col_values(6)
    channel_names = gm_sheet.col_values(7)
    icon_links = gm_sheet.col_values(8)

    del role_titles[0:4]
    del names[0:4]
    del emails[0:4]
    del colors[0:4]
    del user_ids[0:4]
    del descriptions[0:4]
    del channel_names[0:4]
    del icon_links[0:4]

    for i, channel_name in enumerate(channel_names):

        if channel_name == current_message_channel_name:

                emoji = discord.utils.get(context.guild.emojis, name=str(channel_name).capitalize())

                role_gm = discord.utils.get(context.guild.roles, name="Game Manager")  # TODO: Allow for config
                print(f"Channel name: {channel_name}")
                role_game_name = str(channel_name).replace("-", " ").title().replace("Of", "of").replace("Fifa", "FIFA").replace("Csgo", "CS:GO")  #TODO: Better setup
                print(f'Role game name: {role_game_name}')
                role_game = discord.utils.get(context.guild.roles, name=role_game_name)
                print(f'Role game: {role_game}')

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
