# Electricity telegram bot
Bot that will send telegram message in case of electricity state was changed.

![_](_.png)

## How to install:
1. Install python > 3.10
2. Install `make` and `nohup`
3. Install poetry `pip install poetry`
4. Install package `poetry install`
5. Create in project folder file named `.env` and specify there `API_TOKEN`, `CHAT_ID` and `IP_TO_CHECK`, example can be taken from `.test.env` file
6. Bot is ready, run it via `poetry run electricitybot` command or via `make run` command

Bot will ping provided IP adress specified in `IP_TO_CHECK` variable. In case if there will be no response for 4 ping requests in a row, bot will send message about power outage and vice versa.

## How to use in Docker
1. build docker image with `docker build . -t f1ashhimself/electricitybot`
2. start docker container with `e f1ashhimself/electricitybot`
Do not forget to create enviroment variables with `API_TOKEN`, `CHAT_ID` and `IP_TO_CHECK` prior run.

## Using with Topic in Group chats
Create `THREAD_ID` value for `message_thread_id` (please find [Bot API documentation](https://core.telegram.org/bots/api#sendmessage)) in `.env` file or pass `THREAD_ID` enviroment variable into container to send notification to selected Topic in Group chats with over 100 members where Topic enabled. Bot will sent notofaction to Topic called `General` for Group chats with Topic if `THREAD_ID` is not set.
