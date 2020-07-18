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
