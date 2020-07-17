from StocktonBotPackage.DevUtilities import configparser
import discord
import os

"""
This module is an attempt to abtract 
each panel away from the main content.
"""

config = configparser.get_parsed_config()


async def send_help_panel(context, client):

    await context.message.delete()

    president = discord.utils.get(client.get_all_members(), id=int(os.environ['PRESIDENT']))
    embed = discord.Embed(title=config['help-name']['president'], description="If you have a question that does not fall into another category, feel free to ask!", color=0x49a6fd)  # Blue
    embed.set_author(
        name="Student President for Stockton Esports",
        icon_url="https://i.pinimg.com/originals/a7/44/8a/a7448aea8e9d49290ba6924fe8495850.png")
    embed.set_thumbnail(url=president.avatar_url)
    embed.add_field(name="`Discord Contact:`", value=president.mention, inline=True)
    embed.add_field(name="`Email Contact:`", value=f"**{config['help-email']['president']}**", inline=True)
    embed.set_footer(text=f"Please view other leadership staff roles before messaging {president.name}")
    await context.send(embed=embed)

    marketer = discord.utils.get(client.get_all_members(), id=int(os.environ['MARKETER']))
    embed = discord.Embed(title=config['help-name']['marketer'], description="Ask any questions related to graphic design or marketing here!", color=0xff24f8)  # Pink
    embed.set_author(
        name="👔 Marketing Manager",
        )
    embed.set_thumbnail(url=marketer.avatar_url)
    embed.add_field(name="`Discord Contact:`", value=marketer.mention, inline=True)
    embed.add_field(name="`Email Contact:`", value=f"**{config['help-email']['marketer']}**", inline=True)
    embed.set_footer(text=f"Direct all marketing-related questions to {marketer.name}")  # Purple
    await context.send(embed=embed)

    partnerships = discord.utils.get(client.get_all_members(), id=int(os.environ['PARTNERSHIPS']))
    embed = discord.Embed(title=config['help-name']['partnerships'], description="If you are an outside org looking to partner with us, ask here!", color=0xa51fff)  # Purple
    embed.set_author(
        name="🤝 Partnerships Manager",
        )
    embed.set_thumbnail(url=partnerships.avatar_url)
    embed.add_field(name="`Discord Contact:`", value=partnerships.mention, inline=True)
    embed.add_field(name="`Email Contact:`", value=f"**{config['help-email']['partnerships']}**", inline=True)
    embed.set_footer(text=f"Direct all partnership-related questions to {partnerships.name}")
    await context.send(embed=embed)

    community = discord.utils.get(client.get_all_members(), id=int(os.environ['COMMUNITY']))
    embed = discord.Embed(title=config['help-name']['community'], description=f"Having an issue within the Stockton University Esports community? {community.name} is your go-to!", color=0xff7b00)  # Orange
    embed.set_author(
        name="👥 Community Manager",
        )
    embed.set_thumbnail(url=community.avatar_url)
    embed.add_field(name="`Discord Contact:`", value=community.mention, inline=True)
    embed.add_field(name="`Email Contact:`", value=f"**{config['help-email']['community']}**", inline=True)
    embed.set_footer(text=f"Direct all community-related questions to {community.name}")
    await context.send(embed=embed)

    competitive = discord.utils.get(client.get_all_members(), id=int(os.environ['COMPETITIVE']))
    embed = discord.Embed(title=config['help-name']['competitive'], description="If you are interested in competitive play, ask me!", color=0x04ff00)  # Green
    embed.set_author(
        name="🏆 Competitive Coordinator",
        )
    embed.set_thumbnail(url=competitive.avatar_url)
    embed.add_field(name="`Discord Contact:`", value=competitive.mention, inline=True)
    embed.add_field(name="`Email Contact:`", value=f"**{config['help-email']['competitive']}**", inline=True)
    embed.set_footer(text=f"Direct all competitive-related questions to {competitive.name}")
    await context.send(embed=embed)    

    technical = discord.utils.get(client.get_all_members(), id=int(os.environ['TECHNICAL']))
    embed = discord.Embed(title=config['help-name']['technical'], description="For all of your IT needs, message me!", color=0xff1a1a)  # Red
    embed.set_author(
        name="⚙️Technical Coordinator",
        )
    embed.set_thumbnail(url=technical.avatar_url)
    embed.add_field(name="`Discord Contact:`", value=technical.mention, inline=True)
    embed.add_field(name="`Email Contact:`", value=f"**{config['help-email']['technical']}**", inline=True)
    embed.set_footer(text=f"Direct all Technical-related questions to {technical.name}")
    await context.send(embed=embed)

    bot = discord.utils.get(client.get_all_members(), id=int(os.environ['DEVELOPER']))
    embed = discord.Embed(title=f"**{config['help-name']['developer']}**", description="If you're interested in our bot's functionality, want to report a bug or have other questions about the Discord server, ask any time!", color=0x2eff89)  # Teal
    embed.set_author(
        name="Bot Developer",
        icon_url="https://www.solid-optics.com/wp-content/uploads/dev_icon.png")
    embed.set_thumbnail(url=bot.avatar_url)
    embed.add_field(name="`Discord Contact:`", value=bot.mention, inline=True)
    embed.add_field(name="`Email Contact:`", value=f"**{config['help-email']['developer']}**", inline=True)
    embed.set_footer(text=f"Direct all Discord bot-related questions to {bot.name}")
    await context.send(embed=embed)

    embed = discord.Embed(
        title="A comprehensive list of leadership roles and their responsibilities, to help you get your answers from the most appropriate individual.",
        description="`🔼 Specific student leaders are listed further up! 🔼`", color=0xffce47)  # Yellow
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
