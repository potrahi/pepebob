## pepebob
pepebob is a telegram bot which you can learn to talk or at least make your telegram group a little bit funnier

python implementation of and inspired by [pepeground-bot](https://github.com/pepeground/pepeground-bot)

## Prerequisites

Python 3.8.0<br>
Docker<br>
Docker Compose<br>
Postgresql<br>
Mongodb<br>

## Installation

First, you need to create your own .env file inside the root directory, where you will define the required parameters for this app.

Here is a template of .env file:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_NAME=your_telegram_bot_name
TELEGRAM_BOT_ANCHORS=пепе,pepe,переграунд,pepeground,пепеграундес,pepegroundes,pepepot
TELEGRAM_BOT_ASYNC_LEARN=false
TELEGRAM_BOT_CLEANUP_LIMIT=1000

CACHE_HOST=localhost
CACHE_PORT=27017
CACHE_NAME=your_cache_name

DATABASE_ENGINE=postgresql
DATABASE_HOST=localhost
DATABASE_NAME=your_db_name
DATABASE_PORT=5432
DATABASE_USER=your_db_user_name
DATABASE_PASSWORD=your_db_password

PUNCTUATION_END_SENTENCE=.,!,?
```
I guess you understand where to fill your data—for example, TELEGRAM_BOT_TOKEN, etc.

Your token, together with your bot, you can find how to get on the [official telegram page](https://core.telegram.org/bots/tutorial)

If you don't want to install Postgresql or MongoDB on your local machine, the following sentence is for you.<br>
All you need is a [Docker and Docker Compose](https://docs.docker.com/compose/install/)<br>
After you have installed Docker and Docker Compose, open the terminal, go to the app folder and run this command:
```bash
docker compose up -d
```
It should run and build this bot, together with Postgresql, the initial SQL script for Postgresql, and Mongodb.

## Annotatio

This bot can generate sentences based on your communication with him directly or from the group chat. Sometimes, these sentences don't make sense, and sometimes, they can be funny. In any case, it requires some time until his DB of words and pairs is enough to create something. During his learning, the bot will not send any messages, so you should be patient.