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
1. build docker image with `docker build . -t yurnov/electricitybot`
2. start docker container with `docker run -e API_TOKEN=${API_TOKEN} -e CHAT_ID=${CHAT_ID} -e IP_TO_CHECK=${IP_TO_CHECK} -d --rm yurnov/electricitybot`
Do not forget to create enviroment variables with `API_TOKEN`, `CHAT_ID` and `IP_TO_CHECK` prior run.