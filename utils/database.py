import sqlite3
from utils.logger import logger
from threading import Lock

lock = Lock()


class DataBase:
    __DB_LOCATION = "db.db"

    def __init__(self) -> None:
        logger.info(f"CONNECTING TO DB {self.__DB_LOCATION}")
        self.__db = sqlite3.connect(self.__DB_LOCATION)
        self.__db.row_factory = sqlite3.Row
        self.__cur = self.__db.cursor()

    def __del__(self) -> None:
        logger.info("CLOSING DB CONNECTION")
        self.__db.close()

    def commit(self) -> None:
        logger.info("COMMITIING")
        self.__db.commit()

    def create(self):
        with lock:
            logger.info("CHECKING DB EXISTENCE, AND CREATE IF NOT EXISTS")
            self.__cur.execute(
                "CREATE TABLE IF NOT EXISTS accounts(user_id INTEGER PRIMARY KEY, file_name STRING, api_id STRING, api_hash STRING, phone_number STRING, done INTEGER, seed_phrase STRING, bonus_claimed INTEGER, eth_mission_id INTEGER, bnb_mission_id INTEGER, ton_mission_id INTEGER, sol_mission_id INTEGER, tron_mission_id INTEGER, hot_address STRING, eth_address STRING, sol_address STRING, ton_address STRING, base_address STRING, tron_address STRING, near_address STRING, proxy STRING, ref_code INTEGER, referrer INTEGER, hapi_score_done INTEGER, village_id INTEGER, claim_hot INTEGER, claim_max INTEGER, cave_done INTEGER, boosters_done INTEGER, profile_id INTEGER, logged_in INTEGER)"
            )

            self.commit()

    def get_account_data(self, user_id):
        logger.debug(user_id)
        with lock:
            self.__cur.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,))

            account_data = self.__cur.fetchone()
            logger.debug(f"{account_data}")
            return account_data

    def check_account_existence(self, user_id):
        logger.debug(user_id)
        self.__cur.execute(
            f"""SELECT user_id FROM accounts WHERE user_id = {int(user_id)}"""
        )
        items = self.__cur.fetchall()
        logger.debug(items)
        if len(items) > 0:
            return True
        return False

    def create_account_data(
        self,
        user_id: int,
        file_path: str,
        api_id: str | int,
        api_hash: str,
        phone_number: str | int = "",
    ):
        logger.debug(f"{user_id}, {file_path}, {api_id}, {api_hash}, {phone_number}")

        with lock:
            if not self.check_account_existence(user_id):
                values = (
                    user_id,
                    file_path,
                    api_id,
                    api_hash,
                    phone_number,
                    0,
                    "",
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                )
                self.__cur.execute(
                    "INSERT INTO accounts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    values,
                )
                self.commit()
                logger.debug("DONE")
            else:
                logger.debug("ALREADY EXISTS")

    def update_account_data(self, user_id: int, data):
        logger.debug(f"{user_id}, {data}")
        with lock:
            for data_name in data.keys():
                logger.info(f"UPDATING DATA FOR {data_name} INTO {data[data_name]}")
                self.__cur.execute(
                    """UPDATE accounts SET {dn} = ? WHERE user_id = ?""".format(
                        dn=data_name
                    ),
                    (data[data_name], user_id),
                )
            self.commit()

    def get_all_not_done_accounts(self):
        with lock:
            self.__cur.execute("SELECT * FROM accounts WHERE done = 0")

            account_data = self.__cur.fetchall()
            logger.debug(account_data)
            return account_data

    def get_all_accounts(self) -> list:
        with lock:
            self.__cur.execute("SELECT * FROM accounts")

            account_data = self.__cur.fetchall()
            accounts_list = []
            for account in account_data:
                accounts_list.append(account["file_name"])
            logger.debug(account_data)
            logger.debug(accounts_list)
            return accounts_list
