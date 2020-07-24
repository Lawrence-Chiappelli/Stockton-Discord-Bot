

import gspread
from StocktonBotPackage.DevUtilities import dropboxAPI
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
    return sheet


def get_sheet_supported_games():

    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('SUPPORTED GAMES')
    return sheet


def get_sheet_events_subscriptions():
    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('EVENTS / SUBSCRIPTIONS')
    return sheet


def get_sheet_blue_room_reservations():
    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('PC RESERVATIONS - BLUE ROOM')
    return sheet


def get_sheet_authed_users():
    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('AUTHORIZED BOT CMD USERS')
    return sheet


def get_sheet_channel_names():
    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('CHANNELS')
    return sheet


"""
The following are indeed dynamic, but the channel types themselves are common enough
to warrant separate methods that pull individual cell information.
"""


class GsheetsChannelIndice:

    """
    View the Google Sheets Config document for this
    """

    def __init__(self):
        self.landing = 0
        self.social_media_feed = 1
        self.help_directory = 2
        self.bot_command = 3
        self.game_selection = 4
        self.gaming_lab = 5


channel_indice = GsheetsChannelIndice()


def get_landing_channel_name():

    sheet = get_sheet_channel_names()
    channel_names = sheet.col_values(2)
    del channel_names[0:4]
    bot_commands_channel_name = channel_names[channel_indice.landing]
    return bot_commands_channel_name


def get_social_media_feed_channel_name():

    sheet = get_sheet_channel_names()
    channel_names = sheet.col_values(2)
    del channel_names[0:4]
    social_media_feed_channel_name = channel_names[channel_indice.social_media_feed]
    return social_media_feed_channel_name


def get_help_directory_channel_name():

    sheet = get_sheet_channel_names()
    channel_names = sheet.col_values(2)
    del channel_names[0:4]
    help_directory_channel_name = channel_names[channel_indice.help_directory]
    return help_directory_channel_name


def get_bot_commands_channel_name():

    sheet = get_sheet_channel_names()
    channel_names = sheet.col_values(2)
    del channel_names[0:4]
    bot_commands_channel_name = channel_names[channel_indice.bot_command]
    return bot_commands_channel_name


def get_game_selection_channel_name():

    sheet = get_sheet_channel_names()
    channel_names = sheet.col_values(2)
    del channel_names[0:4]
    game_selection_channel_name = channel_names[channel_indice.game_selection]
    return game_selection_channel_name


def get_game_lab_channel_name():

    sheet = get_sheet_channel_names()
    channel_names = sheet.col_values(2)
    del channel_names[0:4]
    gaming_lab_availability_channel = channel_names[channel_indice.gaming_lab]
    return gaming_lab_availability_channel