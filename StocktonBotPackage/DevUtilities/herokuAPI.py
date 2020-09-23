from StocktonBotPackage.DevUtilities import gsheetsAPI
import discord
import heroku3
import os

print(f"Getting Heroku auth...")
try:
    auth = heroku3.from_key((os.environ['HEROKU-API-KEY']))
    print(f"...Heroku auth successfully connected!")
except NameError:
    auth = None
    raise NameError("No key has been provided for Heroku API. This is okay. Continuing program execution.")


class Heroku:

    def __init__(self):
        self.app = auth.app('stockton-discord-bot')
        self.max_rate_limits = 4500  # Refer to docs if this changes

    async def restart_app(self, context):

        print(F"Restarting bot!")

        bot_channel_name = gsheetsAPI.get_bot_commands_channel_name()
        bot_channel = discord.utils.get(context.guild.channels, name=bot_channel_name)

        if self.is_authenticated() and [dyno.state for dyno in self.app.dynos()]:
            await bot_channel.send("Restarting bot from Heroku- please wait approximately 15 seconds...")
            self.app.restart()
        else:
            await bot_channel.send("Will not restart- this bot must be running on Heroku")
            # Do nothing if running locally

    def get_app_state(self):

        if self.is_authenticated() and [dyno.state for dyno in self.app.dynos()]:
            return "Running on Heroku"
        return "Running locally"

    def get_rate_limits(self):

        if self.is_authenticated:
            return f"{auth.ratelimit_remaining()} / {self.max_rate_limits}"

        return "Heroku is not authenticated!"

    def is_authenticated(self):

        if auth.is_authenticated:
            return True
        return False