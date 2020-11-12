from oauth2client.service_account import ServiceAccountCredentials
from StocktonBotPackage.DevUtilities import configutil, dropboxAPI
import threading
import gspread
import dropbox
import time
import os




print(f"Opening Dropbox client...")
# ---------------------------------------------------------+
client_dropbox = dropbox.Dropbox(os.environ['DROPBOX-API-TOKEN'])  #
# ---------------------------------------------------------+
print(f"...Dropbox client opened!")


scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]


def _get_and_open_gspread_client():

    print(f"Opening Google Sheets client, please wait...")
    json_keyfile = dropboxAPI.get_ghseets_credentials()
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(credentials)
    print(f"...Google sheets client successfully opened!")
    return client


# Config
# ---------------------------------------#
config = configutil.get_parsed_config()  #
# ---------------------------------------#

# Get GSheets / Gspread client
# -----------------------------------------------#
client_gsheets = _get_and_open_gspread_client()  #
# -----------------------------------------------#

# Open worksheets with this:
# ------------------------------------------------------------------#
file = client_gsheets.open('Stockton Discord Bot - CONFIGURATION')  #
# ------------------------------------------------------------------#


def api_error_handler(func):

    def inner(*args):
        try:
            return func(*args)
        except gspread.exceptions.APIError:
            print(f"Resource quota exhausted exception caught at function {func}")
            return None

    return inner


@api_error_handler
def store_help_directory_config(sheet: gspread.models.Worksheet):

    """
    :param sheet: help directory sheet
    :return: None
    """

    help_dir_info = sheet.get_all_values()[4:]
    for i, leader in enumerate(help_dir_info):
        for j, info in enumerate(leader):
            config[f'contact-info-{j+1}'][str(i+1)] = info


@api_error_handler
def store_config_faq(sheet: gspread.models.Worksheet):

    q_and_a = sheet.get_all_values()[4:]

    questions = [i[0] for i in q_and_a]
    answers = [i[1] for i in q_and_a]

    for i in range(len(q_and_a)):
        config['faq'][str(questions[i])] = str(answers[i])


@api_error_handler
def store_config_supported_games(sheet: gspread.models.Worksheet):

    supported_games = sheet.get_all_values()[4:]

    role_names = [i[0] for i in supported_games]
    emoji_names = [i[1] for i in supported_games]

    for i in range(len(supported_games)):
        config['role-games'][configutil.get_key_name_as_convention(role_names[i])] = str(role_names[i])
        config['emoji-games'][configutil.get_key_name_as_convention(emoji_names[i])] = str(emoji_names[i])


@api_error_handler
def store_config_reserved_pcs_blue(sheet: gspread.models.Worksheet):

    blue_room_values = sheet.get_all_values()[4:]
    reserved_pcs = [i[1] for i in blue_room_values]  # Col 2
    descriptions = [i[2] for i in blue_room_values]  # Col 3
    # Column 1 is reserved for PC numbers- these are nonfunctional labels for users

    config['lab-blue-description']['content'] = descriptions[0]
    for i, pc in enumerate(reserved_pcs):
        config['lab-blue-reservations'][str(i+1)] = pc


@api_error_handler
def store_config_event_subs(sheet: gspread.models.Worksheet):

    event_subs = sheet.get_all_values()[4:]
    role_names = [i[0] for i in event_subs]  # Col 2
    emoji_names = [i[1] for i in event_subs]
    description = [i[2] for i in event_subs]

    for i, item in enumerate(event_subs):
        key = configutil.get_key_name_as_convention(role_names[i])
        config['role-events'][key] = str(role_names[i])
        config['emoji-events'][key] = str(emoji_names[i])
        config['description-events'][key] = str(description[i])


@api_error_handler
def store_config_game_managers(sheet: gspread.models.Worksheet):

    gm_dir_info = sheet.get_all_values()[4:]

    for i, gm in enumerate(gm_dir_info):
        for j, info in enumerate(gm):
            config[f'gm-info-{j + 1}'][str(i + 1)] = str(info).replace("%", "<>")
            # Percents are temporarily replaced due to "invalid interpolation syntax" exception


@api_error_handler
def store_config_channels(sheet: gspread.models.Worksheet):

    channel_names = sheet.get_all_values()[4:]
    for i, channel_name in enumerate(channel_names):
        as_key = str(channel_name[1]).replace("-", "")
        config['channel'][as_key] = str(channel_name[1])


@api_error_handler
def store_config_calendar(sheet: gspread.models.Worksheet):

    info = sheet.get_all_values()[4:]
    for calendar_link, calendar_image, color in info:
        config['calendar']['calendarlink'] = calendar_link
        config['calendar']['calendarimage'] = calendar_image
        config['calendar']['color'] = color
        # WARNING: I have not accounted for multiple calendars


@api_error_handler
def store_config_authed_users(sheet: gspread.models.Worksheet):

    authed_users = sheet.get_all_values()[4:]
    for i, users in enumerate(authed_users):
        config['id-authed'][f'{i+1}'] = str(users[1])


def bg_google_sheets_config_ping():

    print(f"... pinging worksheets!")

    total = 0
    passed_time = 0
    while True:

        print(f"\t<ping>")

        try:
            all_worksheets = file.worksheets()  # 1
            total += 1
        except gspread.exceptions.APIError:
            print(f"\tResource quota exhausted exception caught in ping thread. Retrying in 10 seconds.")
            time.sleep(10)
            continue

        try:
            for worksheet in all_worksheets:

                if worksheet.title == config['api-gspread-tab-names']['contactcards']:
                    total += 1
                    threading.Thread(target=store_help_directory_config, args=[worksheet], daemon=True).start()  # 2
                elif worksheet.title == config['api-gspread-tab-names']['faq']:
                    total += 1
                    threading.Thread(target=store_config_faq, args=[worksheet], daemon=True).start()  # 3
                elif worksheet.title == config['api-gspread-tab-names']['supportedgames']:
                    total += 1
                    threading.Thread(target=store_config_supported_games, args=[worksheet], daemon=True).start()  # 4
                elif worksheet.title == config['api-gspread-tab-names']['eventsubscriptions']:
                    total += 1
                    threading.Thread(target=store_config_event_subs, args=[worksheet], daemon=True).start()  # 5
                elif worksheet.title == config['api-gspread-tab-names']['blueroom']:
                    total += 1
                    threading.Thread(target=store_config_reserved_pcs_blue, args=[worksheet], daemon=True).start()  # 6
                elif worksheet.title == config['api-gspread-tab-names']['gamemanager']:
                    total += 1
                    threading.Thread(target=store_config_game_managers, args=[worksheet], daemon=True).start()  # 7
                elif worksheet.title == config['api-gspread-tab-names']['goldroom']:
                    # TODO
                    pass
                elif worksheet.title == config['api-gspread-tab-names']['channels']:
                    total += 1
                    threading.Thread(target=store_config_channels, args=[worksheet], daemon=True).start()  # 8
                elif worksheet.title == config['api-gspread-tab-names']['calendar']:
                    total += 1
                    threading.Thread(target=store_config_calendar, args=[worksheet], daemon=True).start()  # 9
                elif worksheet.title == config['api-gspread-tab-names']['authorizedusers']:
                    total += 1
                    threading.Thread(target=store_config_authed_users, args=[worksheet], daemon=True).start()  # 10
        except AttributeError:
            print(F"AttributeError exception occurred (not fatal, probably due to timing inconsistencies).\nRetrying in 5 seconds:")
            time.sleep(5)
            continue
        except TimeoutError as timeout_error:
            print(f"Timeout error occurred, please investigate:\n{timeout_error}")
            passed_time = 0
        except Exception as unknown_exception:
            print(f"Unknown exception caught:\n{unknown_exception}")
            passed_time = 0

        print(F"Finished iteration, current total: {total}")
        passed_time += 10
        print(f"Passed time: {passed_time}")
        if passed_time > 1000:
            passed_time = 0

        time.sleep(10)  # Optimalish time - this should be adjusted based on the number of worksheets


print(f"Starting Google Sheet background thread...")
thread = threading.Thread(target=bg_google_sheets_config_ping, args=[])

# --------------#
thread.start()  #
# --------------#
