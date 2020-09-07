from StocktonBotPackage.DevUtilities import configparser, gsheetsAPI
from collections import OrderedDict
import discord
import tweepy
import os
import datetime
import threading
import asyncio
import json
import warnings
import copy


class TweepyClient:

    def __init__(self, profile=None):
        self.auth = tweepy.OAuthHandler(os.environ['TWITTER-API-KEY'], os.environ['TWITTER-API-KEY-SECRET'])
        self.auth.set_access_token(os.environ['TWITTER-ACCESS-TOKEN'], os.environ['TWITTER-ACCESS-TOKEN-SECRET'])
        self.api = tweepy.API(self.auth)
        self.user_id = os.environ['TWITTER-ID-STOCKTON-ESPORTS']
        self.profile = profile

    def get_rate_limit(self):
        remaining = self.api.rate_limit_status()['resources']['application']['/application/rate_limit_status']['remaining']
        return remaining

    def get_rates_timeline(self):

        """
        :return: Timeline remaining rates
        """

        return self.api.rate_limit_status()['resources']['statuses']['/statuses/user_timeline']['remaining']

    def get_rates_id(self):

        """
        :return: ID remaining rates
        """

        return self.api.rate_limit_status()['resources']['statuses']['/statuses/show/:id']['remaining']

    def get_all_rate_limits(self):
        return self.api.rate_limit_status()


class StdOutListener(tweepy.StreamListener):

    def __init__(self):
        super().__init__()
        self.is_streaming = False
        self.social_media_channel = None
        self.commands_channel = None
        self.static_data = None
        self.dynamic_data = None
        self.error = None

    def on_data(self, raw_data):
        """
        This method is overridden.
        :param raw_data: data that is streamed in from the stream listener
        :return True if data was successfully streamed
        """

        self.static_data = tweet_data_wrapper.get_static_data(raw_data)
        self.dynamic_data = tweet_data_wrapper.get_dynamic_data()

    def on_error(self, status):
        """
        This method if: error that's passed in through status to stream
        """
        print(f"Twitter Stream Error: {status}")
        self.error = status

    def thread_stream(self):

        """
        Data retrieved automatically pipes to StdOutListener

        Note: separate thread allows for stream listening
        with disregard to process blocking
        """

        print(f"Starting Twitter stream thread...")
        self.is_streaming = True
        stream = tweepy.Stream(client.auth, listener)  # Listener is responsible for data handling
        stream.filter(follow=[client.user_id])  # Function cuts off early here


class TweetDataRetrieverWrapper:

    def __init__(self):
        self._twitter_icon_url = "https://cdn.clipart.email/fcf0df581fb3270b21dc370803b034ad_logo-twitter-circle-png-transparent-image-47449-free-icons-and-_2267-2267.png"
        self._tweet = None

    def get_static_data(self, data, tweet_index=None):

        """
        :param data: the data retrieved from either the stream or otherwise
        manual API calls
        :param tweet_index: default None- increment this index if you wish
        to retrieve multiple tweets and are *manually* pulling the tweets
        (i.e., direct status calls)
        :return: tuple data in the following order:
        :returns: text, date, handle, followers, following, username, icon_url,
        thumbnail_url, img_url
        return None if the tweet was not found (the poll method won't execute)
        """

        self._tweet = self._get_tweet_from_data(data, tweet_index)
        if self._tweet is None:
            console_color_red = '\033[93m'
            console_color_normal = '\033[0m'
            print(f"{console_color_red}Tweet is none{console_color_normal}")
            return None

        text = self._get_full_text()
        followers = self._tweet.user.followers_count
        following = self._tweet.user.friends_count
        username = self._tweet.user.name
        icon_url = self._twitter_icon_url
        # thumbnail_url = str(self._tweet.profile_image_url).replace("normal.jpg", "400x400.jpg")
        thumbnail_url = "https://pbs.twimg.com/profile_images/1219805354059599872/sVdcP-_G_400x400.jpg"
        handle = "@" + self._tweet.author.screen_name
        twitter_url = f"https://www.twitter.com/{self._tweet.author.screen_name}"

        if self._is_retweet(self._tweet):
            text, handle, twitter_url = self._adjust_fields_for_retweet(text)
        else:
            if handle in text:
                text = str(text).replace(f"{handle}", f"**{handle}**", 1)
                handle = "Mention in " + handle

        try:
            website_url = self._tweet.entities['url']['urls'][0]['expanded_url']  # The user's linked personal website URL
        except Exception:
            website_url = twitter_url  # Revert to user's twitter link if no personal website

        try:
            img_url = self._tweet.entities['media'][0]['media_url_https']
        except Exception:
            img_url = None

        try:
            month_day_year = datetime.datetime.date(self._tweet.created_at).strftime('%h %d, %Y')
            normal_time = self._convert_from_military_to_normal(self._tweet.created_at)
            date = month_day_year + " | " + normal_time
        except Exception as e:
            text = "Exception caught retrieving data:"
            date = e

        queue_wrapper.push_tweet_id_to_queue(self._tweet.id)
        print(f"Pushed tweet ID to queue...")
        return text, date, handle, followers, following, username, icon_url, thumbnail_url, website_url, twitter_url, img_url

    def get_dynamic_data(self, tweet=None):

        """
        :param tweet: For tweets retrieved manually
        :return: dynamic data (will poll this method semi frequently)
        :returns: favorites, retweets
        Return None if tweet was not stored earlier
        """

        if tweet is not None:  # If tweet was already discovered
            self._tweet = tweet

        if self._tweet is None:
            return None

        retweets = self._tweet.retweet_count
        if hasattr(self._tweet, "retweeted_status"):
            favorites = self._tweet.retweeted_status.favorite_count
        else:
            favorites = self._tweet.favorite_count

        return favorites, retweets

    def _get_tweet_from_data(self, data, tweet_index=None):

        """
        :return: tweet if data was pulled manually (from client.profile)
        or automatically (from stream listener)
        """

        if hasattr(data, 'timeline()') or tweet_index is not None:  # !tweet tweets
            tweet = data.timeline()[tweet_index]
            return tweet

        raw_tweet_data = json.loads(data)  # !populate tweets
        if hasattr(raw_tweet_data, 'id') or 'id' in raw_tweet_data:  # Or streamed tweets
            raw_tweet_id = int(raw_tweet_data['id'])
            tweet = client.api.get_status(id=raw_tweet_id, tweet_mode='extended')
            return tweet

        return None  # Return non if tweet is unretweeted/retweeted

    def _convert_from_military_to_normal(self, datetime_obj, is_utc=False):

        """
        :param datetime_obj: the tweet object associated with the datetime object
        :param is_utc: streamed tweet objects return the time in UTC. This timezone
        is offset by an additional 4 hours, and should require processing to indicate so.
        :return: military time converted to normal time, also with PM or AM
        """

        military = datetime.datetime.time(datetime_obj).strftime('%H:%M')
        hour = int(military[0] + military[1])

        if is_utc:
            # TODO: Fix 4 hour UTC offset
            return datetime.datetime.time(datetime_obj).strftime(f'{hour}:%M (UTC)')

        if hour in range(13, 24):
            hour -= 16
            time_of_day = "P.M."
        else:
            time_of_day = "A.M."

        final_conversion = datetime.datetime.time(datetime_obj).strftime(f'{hour}:%M {time_of_day}')
        return final_conversion

    def _convert_from_datetime_string_to_object(self, raw_date_string):

        """
        :param raw_date_string: the json string
        to convert to datetime object
        :return: the string turned into a datetime object
        as *user's* tweet.created_at datetime format

        Turning it into the tweet format will allow it to
        be converted from military time to normal time,
        as seen when done so manually.
        """

        datetime_format = datetime.datetime.strptime(raw_date_string, '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d %H:%M:%S')
        tweet_format = datetime.datetime.strptime(datetime_format, '%Y-%m-%d %H:%M:%S')
        return tweet_format

    def _get_full_text(self):

        """
        :return: the full text if found, will be truncated otherwise

        Note: a tweet from GET endpoint does not have an
        extended_text field. The tweet has to be searched
        again using some api.search method.

        Opted for api.get_status(id=id, tweet_mode=mode)
        """

        tweet_id = int(self._tweet.id)
        if hasattr(self._tweet, "text"):
            normal_text = self._tweet.text  # TODO: Retweets from stream don't have this?
        else:
            return self._tweet.full_text

        search_result = client.api.get_status(id=tweet_id, tweet_mode='extended')
        if search_result is None or search_result == "" or search_result == " ":
            return normal_text

        return search_result.full_text

    def _is_retweet(self, tweet):

        """
        :param tweet: They either start with RT
        or retweeted is set to True.
        :return: True if retweet, false otherwise
        """
        if hasattr(tweet, "retweeted_status"):
            return True
        # elif tweet.retweeted_status is not None or tweet.retweeted is True:
        #     return True

        return False

    def _adjust_fields_for_retweet(self, text):

        """
        :param text: the text for adjustments
        All other properties are retrieved from self._tweet.
        :return: tuple data in the following order:
        :returns: text, handle, twitter_url
        """

        root_screen_name = self._tweet.author.screen_name  # Root user
        retweet_screen_name = self._tweet.retweeted_status.user.screen_name  # Retweet user
        handle = f"retweet from @{retweet_screen_name}"

        for index in self._tweet.retweeted_status.entities["urls"]:
            if "twitter" in str(index):
                text += "\n\n**View full retweet:** __" + index["url"] + "__"
                break

        if str(text).startswith(f"RT @{root_screen_name}:"):
            text = text.replace(f"RT @{root_screen_name}:", "*(Self retweet)*")
        else:
            text = text.replace("@" + root_screen_name, "**@" + root_screen_name + "**", 1).replace(f"RT @{retweet_screen_name}: ", "", 1)

        if "@" + root_screen_name in text:
            text = str(text).replace("@" + root_screen_name, "**@" + root_screen_name + "**", 1)
            handle = "mention in " + handle

        handle = handle[:1].upper() + handle[1:]  # Capitalizes first letter while *retaining remaining case*
        twitter_url = f"https://www.twitter.com/{retweet_screen_name}"

        return text, handle, twitter_url


class TweetQueueWrapper:

    def __init__(self):
        self.queue = OrderedDict()
        self.is_populating = False  # So poller will update tweets in order

    def push_tweet_id_to_queue(self, tweet_id):

        """
        :param tweet_id: note that raw tweet
        objects are considered unhashable,
        at least for ordered dicts.

        Better to stored the ID, as we'll be
        repeatedly searching for tweets based
        on the ID.
        """

        self.queue[tweet_id] = None  # Values will be added later

    def insert_message_last_item(self, message):
        self.queue.update({next(reversed(self.queue)): message})

    def is_empty(self):
        if not self.queue or bool(self.queue) is False:
            return True
        return False

    def clear_queue(self):
        self.queue = self.queue.clear()

    def remove_tweet_from_queue(self, tweet_id):
        self.queue.pop(tweet_id)

    async def push_message_to_tweet_queue(self, message):

        if not message.embeds and (message.channel is not listener.social_media_channel):
            return

        if message.embeds[0].author.name != client.profile.name:
            return

        while True:
            if queue_wrapper.is_empty():
                continue

            queue_wrapper.insert_message_last_item(message)
            await asyncio.sleep(0.01)
            print(f"Pushed message to queue...")
            break


class Poll:

    def __init__(self):
        self.is_polling = False
        self._poll_rate = 1  # In seconds
        self._num_retries = 5  # If poll error

    async def poll_for_data_from_stream(self, client):

        """
        A workaround for asynchronous function unable to
        be threaded. This is function is called *last* at
        on_ready(). Bot remains operable.

        Reasoning: embeds need to be awaited.
        Listener pipeline is NOT asynchronous,
        which means embed sending can't be
        awaited there.

        This (asynchronous) function polls any data
        that was stored from the pipeline in
        2 second intervals.

        """
        social_chan_name = gsheetsAPI.get_social_media_feed_channel_name()
        commands_chan_name = gsheetsAPI.get_bot_commands_channel_name()
        listener.social_media_channel = discord.utils.get(client.get_all_channels(), name=social_chan_name)
        listener.commands_channel = discord.utils.get(client.get_all_channels(), name=commands_chan_name)
        print(f"Polling for stream...")

        if listener.error is None:
            await listener.commands_channel.send("Starting Twitter feed! No errors found.")
            print(f"...poll success!")
        else:
            await listener.commands_channel.send(f"Starting Twitter feed failed.\nError: `{listener.error}`\nGoogle this error, or try `!twitterpoll` in `15` minutes")
            print(F"Poll unsuccessful!")
            self.is_polling = False  # False by default- it may be set to true and abort mid-process.
            return

        self.is_polling = True
        while True:
            try:
                await asyncio.sleep(self._poll_rate)
                if listener.static_data and listener.dynamic_data:
                    await embed_and_send(listener.static_data, listener.dynamic_data)
                    listener.static_data = None
                    listener.dynamic_data = None
                    listener.error = None
                elif listener.error:
                    await listener.commands_channel.send(f"Twitter poll error: {listener.error}\n*Unable to update Twitter feed*. Please retry in __15__ minutes.")
                else:
                    print(f"No messages in stream listener. Retrying in 5 seconds. Error: {listener.error}")

                await asyncio.sleep(5)
            except Exception as e:
                await listener.commands_channel.send(f"Some unknown exception was caught trying to poll stream. {self._num_retries} retries remaining!\nError: `{e}`")
                print(f"Some unknown exception caught trying to poll stream, retrying!:\n\n{e}")

                if self._num_retries > 0:
                    self._num_retries -= 1
                    continue
                else:
                    self.is_polling = False
                    owner = discord.utils.get(client.guild.members, id=int(config['id']['owner']))
                    await listener.commands_channel.send(f"{owner.mention}, unable to start poller after 5 retries. See `!metrics` for more information")
                    break

    async def poll_for_tweet_updates(self):

        print(f"Polling for updates... (Populating: {queue_wrapper.is_populating} | Queue status: {queue_wrapper.queue})")
        while True:
            await asyncio.sleep(self._poll_rate)
            if queue_wrapper.is_populating or queue_wrapper.is_empty():
                continue

            console_color_green = '\033[92m'
            console_color_normal = '\033[0m'

            queue_copy = copy.copy(queue_wrapper.queue)
            # CRITICAL NOTE: Looping through a dictionary while deleting
            # its keys (regardless of where) will permanently block
            # the polling process. Loop through a copy instead,
            # then delete keys from the original reference.

            # (No exceptions are caught either. It's just a
            # nuance with async functions)

            for tweet_id, msg in queue_copy.items():
                if msg is None:
                    print(F"\t(Waiting for message(s) to be pushed or queued!)")
                    continue
                print(f"\t{console_color_green}Updating next popped tweet | Queue length: {len(queue_wrapper.queue)} | ID: {tweet_id}{console_color_normal} ")
                await self._update_tweet(tweet_id, msg)

    async def _update_tweet(self, tweet_id, message):

        """
        :param tweet_id: IDs were pushed to the
        OrderedDict, not the raw tweet objects
        :param message: Await message.edit from here

        Twitter API gives you 900 show_id and
        user_timeline requests.
        =======================================
        From: api.rate_limit_status()
        Location: ['resources']['statuses']
        ['/statuses/user_timeline'] or ['/statuses/show/:id']
        Then: ['limit'] or ['remaining']

        LIMITATION: Tweets retrieved in quick succession will have to
        wait their turn to be updated. These functions are asynchronous,
        not threaded.
        """
        counter = 0
        update_rate = 1

        while counter < 3:
            print(f"\tGetting tweet from id {tweet_id}... ({counter}/3)")
            await asyncio.sleep(update_rate)
            tweet = client.api.get_status(id=tweet_id, tweet_mode='extended')
            print(f"\tTweet captured...")
            rates_id = client.get_rates_id()
            print(f"\tRates captured...")
            favorites, retweets = tweet_data_wrapper.get_dynamic_data(tweet)

            embed = message.embeds[0]
            if embed is None:
                print(f"\tEmbed is none!")
            embed.set_footer(text=f"💬 0 | 👍 {favorites} | ❤️{favorites} | 🔄 {retweets} • Custom feed developed by Lawrence Chiappelli")
            await message.edit(embed=embed)
            counter += 1

        print(f"\t\tFINISHED UPDATING TWEET!")
        del queue_wrapper.queue[tweet_id]
        return


async def embed_and_send(static_data, dynamic_data):

    """
    :param static_data: tuple of data that never changes
    :param dynamic_data: tuple of data that semi-frequently changes
    :return: if the designated channel is none, otherwise send embed

    Note: replies are part of the premium API.
    """

    text, date, handle, followers, following, username, icon_url, thumbnail_url, website_url, twitter_url, img_url = static_data
    favorites, retweets = dynamic_data

    embed = discord.Embed(title=f"__{handle}__", url=twitter_url, description=f"{following} following | {followers} followers", color=0x8080ff)
    embed.set_author(name=username, icon_url=icon_url, url=website_url)
    embed.set_thumbnail(url=thumbnail_url)
    embed.add_field(name=date, value=text, inline=False)
    embed.set_footer(text=f"💬 0 | 👍 {favorites} | ❤️{favorites} | 🔄 {retweets} • Custom feed developed by Lawrence Chiappelli")

    if img_url is not None:
        embed.set_image(url=img_url)

    try:
        await listener.social_media_channel.send(embed=embed)
    except Exception as e:
        warnings.warn(f"Unable to find the social media channel for tweets!:\n{e}")


async def populate_channel_with_tweets(context):

    """
    :param debug_channel: the channel typed in to debug messages
    """

    bot_commands_channel_name = gsheetsAPI.get_bot_commands_channel_name()
    debug_channel = discord.utils.get(context.message.guild.channels, name=bot_commands_channel_name)

    num_tweets = 20
    queue_wrapper.is_populating = True

    while num_tweets != 0:
        try:
            static_data = tweet_data_wrapper.get_static_data(client.profile, num_tweets-1)
            dynamic_data = tweet_data_wrapper.get_dynamic_data()
            await embed_and_send(static_data, dynamic_data)
            await debug_channel.send(f"✅ Tweet {num_tweets-1} retrieved and sent successfully.")
        except Exception as e:
            await debug_channel.send(f"❌ Tweet {num_tweets-1} retrieved unsuccessfully:\n<{e}>")
        num_tweets -= 1
        await asyncio.sleep(1)

    queue_wrapper.is_populating = False


async def get_last_tweet():

    """
    :return: nothing

    For debugging purposes- gets the last tweet of the
    currently hardcoded user ID.
    """

    static_data = tweet_data_wrapper.get_static_data(client.profile, 0)
    dynamic_data = tweet_data_wrapper.get_dynamic_data()
    await embed_and_send(static_data, dynamic_data)

twitter_poller = Poll()  # Cut+paste to worker if this should automatically start
tweet_data_wrapper = TweetDataRetrieverWrapper()
queue_wrapper = TweetQueueWrapper()
config = configparser.get_parsed_config()
listener = StdOutListener()
profile = TweepyClient().api.get_user(TweepyClient().user_id)  # To make a single API call
client = TweepyClient(profile)  # Now initialized the client with one profile
thread = threading.Thread(target=listener.thread_stream, args=[])

# TODO: Confirm if the following is needed to retrieve the instances' data
# The motivation for this was due to getting conflicting results with both options
# for server metrics. This may be a symptom of a deeper problem somewhere.

# TODO: If so, it might be better to access the instance directly
# instead of calling a function from the module.


def force_thread_start_for_auth():

    """
    :return:

    Motivation: in instances
    where 420 error occurs, users
    can type the necessary command
    to connect the stream account.

    This may happen during each initial
    bot run instance.

    Rate limits reset after 15 minutes.
    """

    thread.start()


# --------------#
thread.start()  #  Comment / uncomment during development!! (Or keep in mind rate limits when testing)
# --------------#
