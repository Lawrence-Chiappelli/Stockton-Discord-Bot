import configparser

file = 'config.ini'
config = configparser.ConfigParser()


def get_parsed_config():

    """
    :return: the parsed version of the config file.
    Note: it is encoded as utf-8 so that emojis
    can be retrieved (it wouldn't work otherwise)
    """

    config.read(file, encoding='utf-8')
    return config


def overwrite_config_section(section: str, disc_obj_list: list):

    """
    :param section: The name of the section category
    :param disc_obj_list: Probably a list of string emotes or roles
    :return: None

    The intent of this utility is to create / overwrite
    a local configuration in the possible but likely
    event that the Google Sheets API runs into an
    exhaustion error. This way they can be retrieved offline
    until the 1 minute cool down has passed.
    """

    if list(config[section]) == disc_obj_list:
        return  # No need to overwrite for equivalent lists

    def _converted_to_key(obj):
        return str(obj).replace(" ", "").lower()

    for disc_obj in disc_obj_list:
        key = _converted_to_key(disc_obj)
        config[section][key] = disc_obj


def write_to_file():

    with open(file, 'w') as config:
        config.write(file)


def print_entire_config_for_verification():

    """
    :return: None

    Should just print out the config
    in a "1-to-1" style (i.e., should
    look exactly the same as the
    config.ini file)
    """

    for section in config.sections():
        print(f"[{section}]")
        for item in config.items(section):
            print(f"{item[0]} = {item[1]}")
        print(f"")


def print_specific_section_items_for_verification(section_name: str):

    """
    :param section_name: Section name as a string
    :return: None
    """

    print(f"[{section_name}]")
    for item in config[section_name].items():
        print(f"{item[0]} = {item[1]}")
    print(f"")


def get_key_name_as_convention(desired_name: str):

    """
    :param desired_name: The name you would
    like to convert
    :return: The key name as a personal
    convention I'm using for config.ini
    """

    return desired_name.lower().replace(" ", "").replace(":", "")
