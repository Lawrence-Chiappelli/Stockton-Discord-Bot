import gspread
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
    credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(credentials)
    print(f"...Google sheets client successfully opened!")
    return client


# ------------------------------------+
client = open_google_sheets_client()  #
# ------------------------------------+


def get_sheet_help_directory_contact_cards():

    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('HELP DIRECTORY CONTACT CARDS')
    return sheet


def get_sheet_supported_games():

    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('SUPPORTED GAMES')
    return sheet


def get_sheet_events_subscriptions():
    sheet = client.open("Stockton Discord Bot - CONFIGURATION").worksheet('EVENTS / SUBSCRIPTIONS')
    return sheet

