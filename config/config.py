import asyncio
import os
from random import choice
from dotenv import load_dotenv
from os import getenv as env
from utils.logger import logger
from threading import Lock

lock = Lock()

load_dotenv()


class Config:
    here_wallet_id = 6739011720
    here_wallet_username = "herewalletbot"

    bot_token = env("BOT_TOKEN")
    api_id = env("API_ID")
    api_hash = env("API_HASH")

    receiver_id = env("RECEIVER_ID")

    main_here_wallet_url = env("MAIN_URL")
    main_seed_phrase = env("MAIN_SEED_PHRASE")
    main_username = env("MAIN_USERNAME")
    main_referral_code = env("MAIN_REF_CODE")

    hot_address = env("HOT_ADDRESS")
    solana_address = env("SOLANA_ADDRESS")
    ton_address = env("TON_ADDRESS")
    eth_address = env("ETH_ADDRESS")
    bnb_address = env("BNB_ADDRESS")
    near_address = env("NEAR_ADDRESS")
    tron_address = env("TRON_ADDRESS")

    main_proxy = env("MAIN_PROXY")
    dolphin_api_key = env("DOLPHIN_API_KEY")
    ads_api_key = env("ADS_API_KEY")

    using_anti_detect_browser = (
        None  # None for not use, "Dolphin" for Dolphin, "Ads" for AdsPower
    )

    solana_chain = "1001"

    ton_chain = "1111"
    ton_contract = "native"
    ton_first_mission_id = 2
    ton_last_mission_id = 2

    eth_chain = "8453"
    eth_contract = "native"
    eth_usdc_contract = f"0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
    eth_weth_contract = f"0x4200000000000000000000000000000000000006"
    eth_first_mission_id = 1
    eth_last_mission_id = 4

    bnb_chain = "56"
    bnb_contract = "native"
    bnb_usdt_contract = f"0x55d398326f99059ff775485246999027b3197955"
    bnb_wbnb_contract = f"0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"
    bnb_slippage = eth_slippage = 0.005
    bnb_first_mission_id = 3
    bnb_last_mission_id = 5

    near_chain = "1010"
    near_contract = "native"
    near_uwon_contract = "438e48ed4ce6beecf503d43b9dbd3c30d516e7fd.factory.bridge.near"
    near_slippage = sol_slippage = tron_slippage = 0.02

    tron_chain = "999"
    tron_contract = "native"
    tron_first_mission_id = 2
    tron_last_mission_id = 2

    default_amount_multiplier = 1000000000000000000
    ton_default_amount_multiplier = 1000000000
    near_default_amount_multiplier = 1000000000000000000000000
    tron_default_amount_multiplier = 1000000
    click_wait_default = 2
    hot_password = "Discover"
    hot_chain = "987"
    hot_first_mission_id = 3
    default_claim_inverval = 2250

    transfer_bnb_amount = 0.02
    transfer_near_amount = 1.7
    transfer_ton_amount = 0.35
    transfer_tron_amount = 10
    transfer_eth_amount = 0.0045


def ref_code_action(action="get", ref_code=None):
    with lock:
        if action == "get":
            with open(f"{os.getcwd()}/data/ref_users.txt", "r+") as f:
                user_ids = f.readlines()

            if not user_ids or len(user_ids) == 0:
                logger.error("No users in ref_users.txt")
                return None

            user_id = user_ids[0]
            user_ids.remove(user_id)

            with open(f"{os.getcwd()}/data/ref_users.txt", "w") as f:
                f.writelines(user_ids)

            return user_id
        elif action == "append":
            logger.debug("Appending new ref code to ref_users.txt")
            with open(f"{os.getcwd()}/data/ref_users.txt", "a") as f:
                f.write(str(ref_code) + "\n")


def get_random_proxy():
    with lock:
        logger.debug("Getting random proxy")
        with open(f"{os.getcwd()}/data/proxy.txt", "r+") as f:
            proxies = f.readlines()

        if not proxies or len(proxies) == 0:
            logger.error("No proxies in proxy.txt")
            return None

        proxy = choice(proxies).strip()
        try:
            proxies.remove(proxy)
        except:
            proxies.remove(proxy + "\n")

        with open(f"{os.getcwd()}/data/proxy.txt", "w") as f:
            f.writelines(proxies)

        return proxy


# {'seed_phrase': seed_phrase, 'hot_address': addresses['near_address'], 'sol_address': addresses['solana_address'], 'eth_address': addresses['bnb_address'], 'base_address': addresses['bnb_address'], 'near_address': addresses['near_address'], 'ton_address': addresses['ton_address'], 'tron_address': addresses['tron_address']}
def generate_sign_up_message(data):
    return f"""
    
✅ Signed up Successfully!
Seed_phrase: {data['seed_phrase']}
Hot Address: {data['hot_address']}
Solana Address: {data['sol_address']}
Eth Address: {data['eth_address']}
Base Address: {data['base_address']}
Near Address: {data['near_address']}
Ton Address: {data['ton_address']}
Tron Address: {data['tron_address']}"""


def start_event_loop(loop):
    asyncio.set_event_loop(loop)  # Устанавливаем цикл событий для потока
    loop.run_forever()
