import asyncio
import os
import telegram
import json
from pathlib import Path
from Utils.DBHelper import DBHelperSingleton
from Utils.DBHelper import DBLogSingleton
from datetime import datetime

os.chdir(Path(__file__).parent.parent.absolute())
print(os.getcwd())
with open("config/config.json") as file:
    try:
        config = json.load(file)
        _token = config["token"]
    except KeyError as e:
        _token = ""


async def main():
    if _token == "":
        return None
    bot = telegram.Bot(_token)
    async with bot:
        print(await bot.get_me())


if __name__ == '__main__':
    db_instance = DBHelperSingleton.instance()
    var = db_instance.current_version
    log_instance = DBLogSingleton.instance()
    log_instance.ERROR("main", "mainTest", "test",
                                    datetime.now())
    print(var)
    asyncio.run(main())
