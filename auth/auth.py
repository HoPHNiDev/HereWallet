import asyncio, os, re, json
import string
from pyrogram import Client
from pyrogram.raw.functions import messages
from pyrogram.raw.types import InputBotAppShortName, DataJSON
from utils.logger import logger
from utils.database import DataBase
from config.config import Config, get_random_proxy
from random import choice


class Auth:
    __workdir = f"{os.getcwd()}/sessions"
    __default_platform = "web"

    def __init__(
        self,
        file_name: str,
        api_id: int = None,
        api_hash: str = None,
        phone_number=None,
        bot_token=None,
        proxy=None,
    ) -> None:
        logger.info(f"Auth to {file_name} with {api_id}, {api_hash} {phone_number}")
        self.__file_name = str(file_name)
        self.__api_id = api_id
        self.__api_hash = api_hash
        self.__phone_number = phone_number
        self.__bot_token = bot_token
        if proxy:
            self.__proxy = {
                "scheme": "socks5",
                "hostname": proxy.split(":")[0],
                "port": int(proxy.split(":")[1]),
                "username": proxy.split(":")[2],
                "password": proxy.split(":")[3],
            }
        else:
            self.__proxy = None
        if self.__bot_token:
            self.__app = Client(
                name=self.__file_name,
                api_id=self.__api_id,
                api_hash=self.__api_hash,
                bot_token=self.__bot_token,
                workdir=self.__workdir,
            )
        else:
            self.__app = Client(
                name=self.__file_name,
                api_id=self.__api_id,
                api_hash=self.__api_hash,
                phone_number=self.__phone_number,
                app_version="7.6.1",
                workdir=self.__workdir,
                proxy=self.__proxy,
            )

    async def __aenter__(self):
        await self.__app.start()
        self.me = await self.__app.get_me()
        logger.info(f"Successfully logged in to as {self.me.username}")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.info(
            f"Called exit with exc_type: {exc_type}, exc_value: {exc_value}, traceback: {traceback}"
        )
        await self.__app.stop()
        logger.info("Successfully logged out and exit class")

    async def get_user_id(self):
        logger.info("GETTING USER ID")
        logger.debug(f"User ID: {self.me.id}")
        return self.me.id

    async def run(self):
        await self.__app.run()

    async def join_channel(self, channel):
        logger.info(f"JOINING CHANNEL @{channel}")
        await self.__app.join_chat(channel)

    async def check_user_messages(self):
        try:
            async for message in self.__app.get_chat_history(
                Config.here_wallet_id, limit=100
            ):
                if message.from_user and message.from_user.id == Config.here_wallet_id:
                    print(
                        f"User {message.from_user.id} has sent a message in the chat {message.chat.id}."
                    )
                    return True
                print(
                    f"User {message.from_user.id} has not sent any messages in the chat {message.chat.id}."
                )
                return False
        except Exception as e:
            logger.error(f"Error getting user messages: {e}")
            return False

    async def request_web_view(self, ref_code: str):
        if self.me.username is None:
            await self.set_username()
        if not await self.check_user_messages():
            logger.info("STARTING HERE WALLET")
            await self.__app.send_message(Config.here_wallet_username, "/start")
        logger.info(f"REQUESTING HERE WALLET WEB VIEW WITH REFERRAL CODE {ref_code}")
        result = await self.__app.invoke(
            query=messages.RequestAppWebView(
                peer=await self.__app.resolve_peer("me"),
                app=InputBotAppShortName(
                    bot_id=await self.__app.resolve_peer(Config.here_wallet_id),
                    short_name="app",
                ),
                platform=self.__default_platform,
                write_allowed=True,
                start_param=str(ref_code),
                theme_params=DataJSON(
                    data='{"bg_color":"#212121","button_color":"#8774e1","button_text_color":"#ffffff","hint_color":"#aaaaaa","link_color":"#8774e1","secondary_bg_color":"#181818","text_color":"#ffffff","header_bg_color":"#212121","accent_text_color":"#8774e1","section_bg_color":"#212121","section_header_text_color":"#8774e1","subtitle_text_color":"#aaaaaa","destructive_text_color":"#ff595a"}'
                ),
            )
        )
        logger.debug(result)
        result.url = result.url.replace(
            re.search(r"tgWebAppVersion=\d.\d", result.url)[0], "tgWebAppVersion=7.6"
        )
        return result

    async def random_username(self, first_name, last_name):
        logger.info("GENERATING RANDOM USERNAME")
        random_number = "".join(choice(string.digits) for i in range(2))
        username = f"{first_name}{last_name}{random_number}"
        return username

    async def set_username(self):
        logger.info("User has no username, updating username")
        username = await self.random_username(self.me.first_name, self.me.last_name)
        logger.info(f"NEW USERNAME: {username}")
        await self.__app.set_username(username)
        return True


def create_account_data_func(user_id, file_name, api_id, api_hash, phone_number):
    db = DataBase()
    db.create_account_data(user_id, file_name, api_id, api_hash, phone_number)


def update_account_data_func(user_id: int, data: dict):
    db = DataBase()
    db.update_account_data(user_id=user_id, data=data)


def get_all_done_accounts_func():
    db = DataBase()
    return db.get_all_accounts()


@logger.catch
async def new_account(file_path=""):
    logger.debug(f"{file_path} | {os.getcwd()}/data/{file_path}")
    db = DataBase()
    if file_path != "":
        with open(f"{os.getcwd()}/data/{file_path}", "r") as f:
            logger.debug(f)
            accounts = f.readlines()
            logger.debug(accounts)
            for i in range(0, len(accounts)):
                account = accounts[i].split("|")
                file_name = account[0]
                api_id = account[1]
                api_hash = account[2]
                phone_number = account[3]

                async with Auth(file_name, api_id, api_hash, phone_number) as app:
                    user_id = await app.get_user_id()

                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    create_account_data_func,
                    user_id,
                    file_name,
                    api_id,
                    api_hash,
                    phone_number,
                )
                proxy = get_random_proxy()
                if proxy:
                    await loop.run_in_executor(
                        None, update_account_data_func, user_id, {"proxy": proxy}
                    )
                    logger.info(f"Proxy for account {file_name} added to DB")

    else:
        while True:
            logger.info("NO ACCOUNT FILE SPECIFIED, USING INTERACTIVE MODE")
            file_name = input('Enter account file name (to exit write "ex"): ')
            if file_name == "ex":
                break
            api_id = int(input('Enter API ID (to exit write "ex"): '))
            if api_id == "ex":
                break
            api_hash = input('Enter API HASH (to exit write "ex"): ')
            if api_hash == "ex":
                break
            phone_number = input('Enter phone number (to exit write "ex"): ')
            if phone_number == "ex":
                break

            async with Auth(file_name, api_id, api_hash, phone_number) as app:
                user_id = await app.get_user_id()

            await db.create_account_data(
                user_id=user_id,
                file_path=file_name,
                api_id=api_id,
                api_hash=api_hash,
                phone_number=phone_number,
            )


async def new_account_from_json(SESSION_DIR="./sessions"):
    session_files = [
        os.path.join(SESSION_DIR, f)
        for f in os.listdir(SESSION_DIR)
        if f.endswith(".session")
    ]
    loop = asyncio.get_event_loop()

    accounts_list = await loop.run_in_executor(None, get_all_done_accounts_func)
    for session_file in session_files:
        logger.debug(f"Checking {session_file}")
        file_name = session_file.replace("./sessions/", "").replace(".session", "")
        if file_name in accounts_list:
            logger.debug(f"{file_name} already exists in DB")
            continue
        try:
            with open(f"./sessions_data/{file_name}.json", "r") as f:
                session_data = json.load(f)
        except:
            continue

        API_ID = session_data["app_id"]
        API_HASH = session_data["app_hash"]
        phone_number = session_data["phone"]

        async with Auth(file_name, API_ID, API_HASH, phone_number) as app:
            user_id = await app.get_user_id()

        await loop.run_in_executor(
            None,
            create_account_data_func,
            user_id,
            file_name,
            API_ID,
            API_HASH,
            phone_number,
        )
        logger.info(f"Account {file_name} added to DB")

        proxy = get_random_proxy()
        if proxy:
            await loop.run_in_executor(
                None, update_account_data_func, user_id, {"proxy": proxy}
            )
            logger.info(f"Proxy for account {file_name} added to DB")


@logger.catch
async def get_wallet_url(account):
    logger.debug("get_wallet_url funciton called")

    logger.debug(account)
    async with Auth(
        account[1], account[2], account[3], account[4], proxy=account["proxy"]
    ) as app:
        result = await app.request_web_view(account["referrer"])
        user_id = await app.get_user_id()
        await app.join_channel("hotonnear")
        await app.join_channel("hapi_ann")
        logger.info(f"URL: {result.url}")
        return {"url": result.url, "user_id": user_id}


bot = Client(
    "log_bot",
    api_id=Config.api_id,
    api_hash=Config.api_hash,
    bot_token=Config.bot_token,
    workdir=f"{os.getcwd()}/sessions",
)


async def bot_send_logs(account, message, type="info"):
    try:
        await bot.send_message(
            Config.receiver_id,
            f"""
<b>Account</b>: {account}
<i>Type</i>: {type}
<b>Message</b>: {message}
    """,
        )
        logger.info(
            f"[{message}] about {account} typeof {type} sent to {Config.receiver_id}"
        )
    except Exception as e:
        logger.error(f"Error while sending message {e}")
