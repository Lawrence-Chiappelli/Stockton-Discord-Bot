# Stockton University Discord Bot

This repository contains a private Discord bot for Stockton University's eSports program's main Discord server.

This bot automates user authentication and dynamically updates the gaming lab's PC usage via web scraping. Additional features may be available as development progresses.

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

*In short, the above non-python files required for hosting on Heroku. They must remain in the root directory.* I recommend the free version of Heroku if you need a hosting solution for development or production purposes.

## Config file

This bot queries customizable information used in a *Google Sheets document*. For access to this document, please contact me or browse the Discord server's `#help-directory` for more information.

## Packages:

- ```StocktonBotPackage```
Contains modules, functionality and utility unique to Stockton Esports Discord server.

  - ```Features```
    Contains interactive properties for server members.        
    
    - ```command_functionality.py``` - controls logic for user-entered commands. If a user types a valid command in a text channel, this module will direct you to your desired functionality. Type `!help` for more info. (Note: the discord.py command extension framework is used)              
    
    - ```helpcontactinfo.py``` - Used for the `#help-directory` contact information panels. By typing `!helppanel`, it will retrieve every entry in the Google Sheets configuration file and display everyone's info in one-fell sweep. Contains customizable descriptions and contact information, provided users have access
    
    Make sure to type !help for instructions on *where* to enter commands. You may refer to `config.ini` for more context, but as it currently stands, the Google Sheets config is being used in place of this. 
    
  - ```DevUtilities```
  Contains utilities for programmers and server moderators.
  
    - ```configparser.py``` - A shorthand way of receiving the parsed configuration file `config.ini`. While currently short in scope, the parser may need additional functionality in the possible event that `config.ini` becomes more complex.
    
    - ```dropboxAPI.py``` - Shorthand methods of retrieving a private JSON file that's used to connect to the Google Sheets API.
  
    - ```gaming_lab_api.py``` - a pseudo-API being developed in-place of the actual [labstats](https://labstats.com/) API locked behind University credentials. It's built around Selenium- it being the supporting structure that scrapes data from main [Stockton Esports](https://sites.google.com/stockton.edu/stockton-esports/gaming-lab?authuser=0) website.                      
    
    - ```ghseetsAPI.py``` - Contains methods to pull individual sheet tabs or specific pieces of data from the Google Sheets config document. For contributors, be wary of your API rate limits (more information can be found [here](https://developers.google.com/analytics/devguides/config/mgmt/v3/limits-quotas))- it should be noted that **the bot will make the most API calls from this module.**
    
    - ```validators.py``` -  A shorthand method of checking the validity of command execution. A couple things to note about this: the command extension framework does provide built-in validation methods, but it is temporarily unused until there is a need to a validate more general checks. Furthermore, a *couple* lines of codes may be repeated from here in `command_functionality.py`- it's mainly to assist me during development so that I can more easily focus on the command's task at hand. 

## Contributor / Installation instructions

Interested in contributing to the bot, or simply want to install it in your own server? Check out the [Wiki](https://github.com/Lawrence-Chiappelli/Stockton-Discord-Bot/wiki) for instructions.
