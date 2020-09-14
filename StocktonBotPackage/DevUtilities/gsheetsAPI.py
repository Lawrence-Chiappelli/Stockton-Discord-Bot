import gspread
from StocktonBotPackage.DevUtilities import dropboxAPI, configparser
from oauth2client.service_account import ServiceAccountCredentials

"""
This module is a visual database for a very small set of Discord admins
to use and customize the output of the bot.
"""

scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]


class Formatting:

    """
    We only need to retrieve this once during runtime.
    Never gets updated dynamically. The Google Sheet
    ranges following are locked, providing an extra layer
    of consistency.
    """

    def __init__(self):
        self.start = int(config['api-gsheets']['start'])
        self.end = int(config['api-gsheets']['end'])
        
        
config = configparser.get_parsed_config()
format = Formatting()


def open_google_sheets_client():

    print(f"Opening Google Sheets client, please wait...")
    json_keyfile = dropboxAPI.get_ghseets_credentials()
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(credentials)
    print(f"...Google sheets client successfully opened!")
    return client


# ------------------------------------+
client = open_google_sheets_client()  #
# ------------------------------------+


def get_sheet_help_directory_contact_cards():

    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('CONTACT CARDS')
    
    role_titles = sheet.col_values(1)
    names = sheet.col_values(2)
    emails = sheet.col_values(3)
    colors = sheet.col_values(4)
    user_ids = sheet.col_values(5)
    descriptions = sheet.col_values(6)
    footers = sheet.col_values(7)

    del role_titles[format.start:format.end]  # Remove the headers I've added
    del names[format.start:format.end]
    del emails[format.start:format.end]
    del colors[format.start:format.end]
    del user_ids[format.start:format.end]
    del descriptions[format.start:format.end]
    del footers[format.start:format.end]
    
    return role_titles, \
        names, \
        emails, \
        colors, \
        user_ids, \
        descriptions,\
        footers


def get_sheet_supported_games():

    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('SUPPORTED GAMES')
    game_roles = sheet.col_values(1)
    game_emojis = sheet.col_values(2)
    del game_roles[format.start:format.end]
    del game_emojis[format.start:format.end]
    return game_roles, game_emojis


def get_event_subscriptions():
    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('EVENTS / SUBSCRIPTIONS')
    role_names = sheet.col_values(1)
    emojis = sheet.col_values(2)  # These are already default, raw emojis
    description_values = sheet.col_values(3)

    del role_names[format.start:format.end]
    del emojis[format.start:format.end]
    del description_values[format.start:format.end]
    return role_names, emojis, description_values


def get_blue_room_reserves_and_desc():

    """
    :return: the reservations and description
    Format: reservations, description
    """

    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('PC RESERVATIONS - BLUE ROOM')
    reservations = sheet.col_values(2)
    description = sheet.col_values(3)
    del reservations[format.start:format.end]
    del description[format.start:format.end]

    return reservations, description


def get_authed_user_ids():
    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('AUTHORIZED BOT CMD USERS')
    ids = sheet.col_values(2)
    del ids[format.start:format.end]  # Remove headers
    ids = [int(i) for i in ids]  # Converts strings to ints
    return ids


def get_sheet_channel_names():
    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('CHANNELS')
    return sheet


def get_gm_info():
    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('GAME MANAGERS')
    role_titles = sheet.col_values(1)
    names = sheet.col_values(2)
    emails = sheet.col_values(3)
    colors = sheet.col_values(4)
    user_ids = sheet.col_values(5)
    descriptions = sheet.col_values(6)
    channel_names = sheet.col_values(7)
    icon_links = sheet.col_values(8)

    del role_titles[format.start:format.end]
    del names[format.start:format.end]
    del emails[format.start:format.end]
    del colors[format.start:format.end]
    del user_ids[format.start:format.end]
    del descriptions[format.start:format.end]
    del channel_names[format.start:format.end]
    del icon_links[format.start:format.end]

    return role_titles, \
        names, \
        emails, \
        colors, \
        user_ids, \
        descriptions, \
        channel_names, \
        icon_links


def get_calendar():

    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('CALENDAR')
    link = sheet.col_values(1)
    thumbnail = sheet.col_values(2)
    color = sheet.col_values(3)
    del link[format.start:format.end]
    del thumbnail[format.start:format.end]
    del color[format.start:format.end]
    return link, thumbnail, color


def get_faq():

    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('FAQ')
    questions = sheet.col_values(1)
    answers = sheet.col_values(2)
    del questions[format.start:format.end]
    del answers[format.start:format.end]
    return questions, answers


"""
The following are indeed dynamic, but the channel types themselves are common enough
to warrant separate methods that pull individual cell information.
"""


class GsheetsChannelIndice:

    """
    View the Google Sheets Config document for this
    """

    # TODO: Replace hardcoded indice with matching dictionary key

    def __init__(self):
        self.landing = 0
        self.social_media_feed = 1
        self.help_directory = 2
        self.bot_command = 3
        self.game_selection = 4
        self.gaming_lab = 5
        self.event_subscriptions = 6
        self.faq = 7
        self.audit_logs = 8
        self.welcome = 9


channel_indice = GsheetsChannelIndice()


def get_all_channel_names():

    """
    :return: the raw channel names, not the sheet object
    """

    sheet = get_sheet_channel_names()
    channel_names = sheet.col_values(2)
    del channel_names[format.start:format.end]
    return channel_names


def get_landing_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.landing]


def get_social_media_feed_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.social_media_feed]


def get_help_directory_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.help_directory]


def get_bot_commands_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.bot_command]


def get_game_selection_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.game_selection]


def get_game_lab_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.gaming_lab]


def get_event_subscriptions_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.event_subscriptions]


def get_faq_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.faq]


def get_audit_logs_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.audit_logs]


def get_welcome_channel_name():

    channel_names = get_all_channel_names()
    return channel_names[channel_indice.welcome]


def validate_resource_usage():

    """
    :return: True or False if able
    to open a sheet

    There seems to be no direct way of
    accessing current rate limits
    directly through the API.

    In this case, if the client is
    able to open any given sheet,
    that means resource are still available,
    and it returns True. Otherwise, it
    return False.
    """

    try:
        sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('FAQ')
        if sheet:
            return True
        return False
    except Exception:  # 429 error API resource exhausted
        return False
    
# if __name__ == os.path.relpath(__file__).replace("\\", ".").replace(".py", "")
