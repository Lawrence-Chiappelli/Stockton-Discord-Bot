import configparser


def get_parsed_config():

    """
    :return: the parsed version of the config file.
    Note: it is encoded as utf-8 so that emojis
    can be retrieved (it wouldn't work otherwise)
    """

    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    return config
