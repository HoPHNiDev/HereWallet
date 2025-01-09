from utils.database import DataBase
from utils.launch import start
import asyncio


if __name__ == "__main__":
    db = DataBase()
    db.create()
    del db

    asyncio.run(start())
