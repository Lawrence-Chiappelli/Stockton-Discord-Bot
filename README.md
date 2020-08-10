# Stockton University Discord Bot

This repository contains a private Discord bot for Stockton University's eSports' main Discord server.

This bot automates user authentication and dynamically updates the gaming lab's PC usage via web scraping. See additional features in action at the bottom of this README.

- The end-goal is to have this bot utilized long term.
- Contributions to the current bot is encouraged.
- Check Wiki for contribution and installation instructions.
- This repo is also intended as part of my portfolio. 
# Repository demystified

The following is an explanation of the repository's project structure, whether you are simply curious or a potential contributor.

## Heroku Files:

- ```bot.py``` - the "brains" of the code. It directs end-user functionality to different modules. Set this as your script path.
- ```config.ini``` - contains a unique configuration specific to the needs of Discord server. Modules will depend on this.
- ```Aptfile``` - "[Heroku](https://heroku.com) will ... install these packages ... when you deploy your application"
- ```Procfile``` - "Heroku apps include a Procfile that specifies the commands that are executed by the app on startup"
- ```runtime.txt``` - "The Heroku Runtime is responsible for provisioning and orchestrating containers (dynos), managing and monitoring their -lifecycle, providing proper network configuration, HTTP routing, log aggregation, and more."
- ```requirements.txt``` - "The requirements. txt file lists the app dependencies together. When an app is deployed, Heroku reads this file and installs the appropriate Python dependencies using the pip install -r command."

*In short, the above non-python files required for hosting on Heroku. They must remain in the root directory.* I recommend the free version of Heroku if you need a hosting solution during development.

## Packages:

- ```StocktonBotPackage```
Contains modules, functionality and utility unique to Stockton Esports Discord server.

  - ```Features```
    Contains interactive properties for server members.
    
    - ```customcommands.py``` - controls logic for user-entered commands. If a user types a valid command in a text channel, this module will direct you to your desired functionality. Type `!help` for more info. (Note: the discord.py command extension framework is used)
    
    - ```twitterfeed.py``` - a real-time Tweet streamer that maximizes asynchronous programming to continuously update Stockton's tweets via Discord embeds. Type `!populate` to populate the `#social-media-feed` channel with the last 20 tweets.
    
    - ```helpcontactinfo.py``` - a series of contact info-related embeds that can be sent out by entering `!helppanel`. These embeds are customizable through a Google Sheets config file. 
    
    Make sure to type !help for instructions on *where* to enter commands. Such configuration can also be observed in config.ini. 
    
  - ```DevUtilities```
  Contains utilities for programmers and server moderators.          
  
    - ```configparser.py``` - A shorthand way of receiving the parsed configuration file `config.ini`. While currently short in scope, the parser may need additional functionality in the possible event that `config.ini` becomes more complex.        
    
    - ```dropboxAPI.py``` - Used to access the API credentials needed to connect to the Google Sheets config document. The file contained in the dropbox account is a raw JSON file- the motivation to have this file separate is to work around the lack of environment variable support coming from a non-Python file.
        
    - ```gaminglabapi.py``` - a pseudo-API being developed in-place of the actual [labstats](https://labstats.com/) API locked behind University credentials. It's built around Selenium- it being the supporting structure that scrapes data from main [Stockton Esports](https://sites.google.com/stockton.edu/stockton-esports/gaming-lab?authuser=0) website.    
    
     - ```gsheetsAPI.py``` - Used to retrieve customizable data from a Google Sheets file, including but not limited to entire sheets and specific pieces of data. **Note**: the majority of API calls will occur here, so please be wary of your rate limits. More info on rate limits [here](https://developers.google.com/sheets/api/limits).
    
    - ```validators.py``` -  A shorthand method of checking the validity of command execution. This is used in combination with the Discord command extension's built-in validators.
    
## Google Sheets config file

This bot queries customizable information used in a private Google Sheets document. Please refer to the [Wiki](https://github.com/Lawrence-Chiappelli/Stockton-Discord-Bot/wiki) for more information regarding this document.

## Contributor / Installation instructions

Interested in contributing to the bot, or simply want to install it in your own server? Check out the [Wiki](https://github.com/Lawrence-Chiappelli/Stockton-Discord-Bot/wiki) for instructions.

<h1 align="center">Gallery</h1>

<p align="center">
  <kbd>
    Help Directory - <b>!helppanel</b>
  </kbd>
<br><br>
  <kbd>
    <img src="https://imgur.com/SyZMzVD.gif"/>
  </kbd>
<br><br>
  
<p align="center">
  <kbd>
    Game Selection - <b>!gameselection</b>
  </kbd>
<br><br>
  <kbd>
    <img src="https://imgur.com/jvFp6aK.gif"/>
  </kbd>
<br><br>

<p align="center">
  <kbd>
    Real-time Gaming Lab PC usage - <b>!gamelab</b>
  </kbd>
<br><br>
  <kbd>
    <img src="https://imgur.com/DHdc88a.gif"/>
  </kbd>
</p>