# Electricity telegram bot
Bot that will send telegram message in case of electricity state was changed

## How to install:
1. Install python > 3.10
2. Install `make` and `nohup`
3. Install poetry `pip install poetry`
4. Install package `poetry install`
5. Create in project folder file named `.env` and specify there `API_TOKEN`, `CHAT_ID` and `IP_TO_CHECK`, example can be taken from `.test.env` file
6. Bot is ready, run it via `electricitybot` command or via `make run` command
