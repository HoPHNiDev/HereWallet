import asyncio, threading, json, time, re, decimal, pyperclip
import seleniumwire.webdriver as uc
from seleniumwire.webdriver import FirefoxOptions, Firefox
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from random import choice, randint
from auth.auth import get_wallet_url, bot_send_logs, bot
from auth.dolphin import Dolphin
from auth.adspower import AdsPower
from utils.database import DataBase
from config.config import (
    Config,
    ref_code_action,
    start_event_loop,
)
from utils.logger import logger
from threading import Thread, Timer, BoundedSemaphore, Lock
from datetime import datetime, timedelta

timer_threads = []
transfer_accounts_in_usage = 0
transfer_eligability = True
lock = Lock()


class WebAutomation:
    __here_wallet_url = "https://tgapp.herewallet.app/"

    def __init__(
        self,
        browser: str = "chrome",
        loop=None,
        proxy: str | None = None,
        head: bool = False,
        account=None,
        profile_id: int = None,
    ):
        global transfer_accounts_in_usage
        self.loop = loop
        self.logged_in = bool(account["logged_in"]) if not head else True
        self.head = head
        if self.head:
            transfer_accounts_in_usage += 1
        self.account = account
        self.profile_id = profile_id
        self.log("Initializing webAutomation", "info")

        data = asyncio.run(get_wallet_url(account)) if not head else None
        self.web_page_url = data["url"] if not head else Config.main_here_wallet_url

        self.village_ids = [
            "13716",
            "175513",
            "208522",
            "18907",
            "17426",
            "104162",
            "255893",
            "15362",
            "25409",
            "39167",
            "34235",
            "41755",
            "84947",
            "31080",
            "39400",
        ]

        if profile_id:
            if Config.using_anti_detect_browser == "Dolphin":
                self.dolphin = Dolphin(Config.dolphin_api_key)
                self.port = self.dolphin.get_port(profile_id)
                options = ChromeOptions()
                service = Service(
                    executable_path="/Users/hophni/Documents/HereWallet/auto/webdriver/chromedriver"
                )
                options.debugger_address = f"127.0.0.1:{self.port}"

            elif Config.using_anti_detect_browser == "Ads":
                self.adspower = AdsPower(self.profile_id)
                self.port = self.adspower.port
                self.webdriver = self.adspower.webdriver
                options = ChromeOptions()
                service = Service(executable_path=self.webdriver)
                options.debugger_address = self.port

            self.driver = uc.Chrome(service=service, options=options)
        else:
            user_agent = choice(
                [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                ]
            )
            if head:
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"

            if browser == "chrome":
                service = Service(
                    executable_path="/Users/hophni/Documents/HereWallet/auto/webdriver/chromedriver"
                )
                options = uc.ChromeOptions()
                options.add_argument("--auto-open-devtools-for-tabs")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--start-maximized")
                options.add_argument("--no-sandbox")
                options.add_argument(f"user-agent={user_agent}")

                if proxy:
                    self.log(f"Proxy server is {proxy}", "info")
                    options.add_argument(f"--proxy-server={proxy}")
                self.driver = uc.Chrome(
                    service=service, seleniumwire_options={}, options=options
                )

                self.__randomize_fingerprint()

            elif browser == "firefox":
                options = FirefoxOptions()
                if proxy:
                    options.set_preference("network.proxy.type", 1)
                    options.set_preference("network.proxy.http", proxy.split(":")[0])
                    options.set_preference(
                        "network.proxy.http_port", int(proxy.split(":")[1])
                    )
                    options.set_preference("network.proxy.ssl", proxy.split(":")[0])
                    options.set_preference(
                        "network.proxy.ssl_port", int(proxy.split(":")[1])
                    )
                self.driver = Firefox(options=options)
            else:
                raise ValueError("Unsupported browser")

    def initialize_urls(self):
        self.__home_page_url = f"{self.__here_wallet_url}home"
        self.__settings_page_url = f"{self.__here_wallet_url}settings"
        self.__referral_page_url = f"{self.__settings_page_url}/referral"
        self.__hot_page_url = f"{self.__here_wallet_url}hot"
        self.__transfer_url = f"{self.__here_wallet_url}transfer"
        self.__swaps_url = f"{self.__here_wallet_url}swaps"
        self.__bridge_url = f"{self.__here_wallet_url}bridge"
        self.__missions_url = f"{self.__here_wallet_url}missions"
        self.__village_url = f"{self.__hot_page_url}/village"
        self.__cave_url = f"{self.__hot_page_url}/cave"
        self.__hapi_score_url = f"{self.__here_wallet_url}browser/score.hapi.mobi"
        self.bnb_mission_url = f"{self.__missions_url}/bnb"
        self.eth_mission_url = f"{self.__missions_url}/base"
        self.sol_mission_url = f"{self.__missions_url}/solana"
        self.ton_mission_url = f"{self.__missions_url}/ton"
        self.tron_mission_url = f"{self.__missions_url}/tron"
        self.hot_mission_url = f"{self.__missions_url}/hot"
        self.boosters_mission_url = f"{self.__missions_url}/boosters"
        self.addresses_url = f"{self.__here_wallet_url}account-address"

    def __del__(self):
        global transfer_accounts_in_usage
        self.log(f"Closing web automation", "info")
        if self.head:
            transfer_accounts_in_usage = transfer_accounts_in_usage - 1
        self.driver.quit()

    def log(self, msg, level="debug"):
        account_name = (
            self.account["file_name"] if not self.head else Config.main_username
        )
        if level.lower() == "debug":
            logger.debug(f"<yellow>[{account_name}]</yellow> | {msg}")
        elif level.lower() == "info":
            logger.info(f"<yellow>[{account_name}]</yellow> | {msg}")
        elif level.lower() == "error":
            error_send = asyncio.run_coroutine_threadsafe(
                bot_send_logs(account_name, message=msg), self.loop
            )
            error_send.result()
            logger.error(f"<yellow>[{account_name}]</yellow> | {msg}")

    def __randomize_fingerprint(self):
        self.log(f"Randomizing fingerprint", "info")
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def __find_element_x(self, path, find_by="XPATH"):
        self.log(f"Finding element {path} by {find_by}")
        if find_by == "XPATH":
            return self.driver.find_element(By.XPATH, path)
        elif find_by == "ID":
            return self.driver.find_element(By.ID, path)

    def __wait_element(self, path, timeout=10, find_by="XPATH"):
        self.log(f"Waiting element {path} by {find_by} within {timeout} seconds")
        if find_by == "XPATH":
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, path))
            )
        elif find_by == "ID":
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, path))
            )

    def __wait_element_disappear(self, path, timeout=10, find_by="XPATH"):
        self.log(
            f"Waiting element disappear {path} by {find_by} within {timeout} seconds"
        )
        if find_by == "XPATH":
            return WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.XPATH, path))
            )
        elif find_by == "ID":
            return WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.ID, path))
            )

    def __wait_frame_and_switch(self, path, timeout=10, find_by="XPATH"):
        self.log(f"Waiting frame {path} by {find_by} within {timeout} seconds")
        if find_by == "XPATH":
            return WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, path))
            )
        elif find_by == "ID":
            return WebDriverWait(self.driver, timeout).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, path))
            )

    def __wait_element_clickable(self, path, timeout=10, find_by="XPATH"):
        self.log(
            f"Waiting element is clickable {path} by {find_by} within {timeout} seconds"
        )
        if find_by == "XPATH":
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, path))
            )
        elif find_by == "ID":
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.ID, path))
            )

    def click(self, path):
        logger.debug(f"Clicking {path}")
        # self.driver.execute_script("arguments[0].click();", path)
        path.click()

    def wait_element(self, path, timeout=10, find_by="XPATH"):
        return self.__wait_element(path, timeout, find_by)

    def get_transfer_url(self, chain, contract, address, amount):
        self.log(
            f"Getting transfer url for {chain} TOKEN to {address} of {int(amount)}"
        )
        return f"{self.__transfer_url}/review?token={chain}:{contract}&amount={int(amount)}&receiver={address}"

    def get_swap_url(self, chain, from_contract, to_contract, slippage):
        self.log(
            f"Getting swap url for {chain} chain from {from_contract} to {to_contract} with slippage {slippage}"
        )
        return f"{self.__swaps_url}?amount=0&from={chain}:{from_contract}&to={chain}:{to_contract}&slippage={slippage}"

    def get_bridge_url(self, token, from_chain, to_chain):
        self.log(f"Getting bridge url for {token} from {from_chain} to {to_chain}")
        return f"{self.__bridge_url}?token={token}&bridge={from_chain}:{to_chain}"

    def get_addresses_from_rq(self):
        for i in range(100):
            time.sleep(2)
            self.log("Trying to find Sync request")
            print(self.driver.requests)
            for request in self.driver.requests:
                print(request.url)
                if (
                    request.method == "POST"
                    and request.url
                    == "https://api0.herewallet.app/api/v1/user/sync/balance"
                ):
                    self.log("Sync request found", "error")
                    self.log(f"{request.url} {request.headers}")
                    if request.body:
                        body = json.loads(request.body.decode("utf-8"))
                        self.log(body)
                        eth_address = body["address"]["1"]
                        solana_address = body["address"][Config.solana_chain]
                        hot_address = body["address"][Config.near_chain]
                        base_address = body["address"][Config.eth_chain]
                        ton_address = body["address"][Config.ton_chain]
                        tron_address = body["address"][Config.tron_chain]

                        return (
                            eth_address,
                            solana_address,
                            hot_address,
                            base_address,
                            ton_address,
                            tron_address,
                        )

    def get_addresses(self):
        addresses = {
            "tron_address": "",
            "sol_address": "",
            "optimism_address": "",
            "near_address": "",
            "ton_address": "",
            "eth_address": "",
        }

        for i in range(6):
            for j in range(2):
                try:
                    self.open_page(self.addresses_url)
                    address_page = self.__wait_element(
                        f'//*[@id="root"]/div/div/div/div[{i+1}]', 20
                    )
                    time.sleep(5)

                    self.click(address_page)
                    addresses[list(addresses.keys())[i]] = self.__wait_element(
                        '//*[@id="root"]/div/div/div[3]/div/p[2]', 20
                    ).text
                    break
                except:
                    self.log(
                        f"Error getting address, trying {j+1} time {list(addresses.keys())[i]}",
                        "error",
                    )
                    continue

        del addresses["optimism_address"]
        addresses["hot_address"] = addresses["near_address"]
        addresses["base_address"] = addresses["eth_address"]
        return addresses

    def get_ref_code(self):
        self.open_page(self.__referral_page_url)
        time.sleep(2)

        invite_friend_button = self.__wait_element(
            '//*[@id="root"]/div/div/div/div/button[1]', 60
        )
        if invite_friend_button.get_attribute("disabled") is None:
            self.click(invite_friend_button)
        else:
            self.log(f"Cannot find invite friend button", "error")
            return False
        time.sleep(2)
        get_ref_link_button = self.__wait_element(
            "/html/body/div[4]/div/div[2]/div/button", 60
        )
        if get_ref_link_button.get_attribute("disabled") is None:
            self.click(get_ref_link_button)
        time.sleep(2)

        ref_link = pyperclip.paste()
        self.log(f"Copied referral link: {ref_link}")
        ref_code = re.search(r"startapp=(\d+)", ref_link).group(1)
        self.log(f"Referral Code is {ref_code}")

        return ref_code

    def get_log_message(self):
        for i in range(200):
            try:
                time.sleep(1)
                success_message = self.__find_element_x(
                    f"/html/body/div[1][not(@id='root')]"
                ).text
                if success_message != "":
                    self.log(f"Message is {success_message}")
                    return success_message
            except:
                pass

    def open_page(self, url):
        self.log(f"OPENING PAGE {url}", "info")

        self.driver.get(url)

    def switch_window(self, window: int):
        self.log(f"Switching window to {window}")
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[window])

    def home_page(self):
        self.open_page(self.web_page_url)
        time.sleep(2)

    def login(self, seed_phrase: str):
        try:
            wait_here_tabs = self.__wait_element("here-tabs", 10, "ID")
            if wait_here_tabs:
                return True
        except:
            self.log(f"LOGGING IN", "info")
            self.log(f"SEED PHRASE - [{seed_phrase}]")
            self.seed_phrase = seed_phrase
            self.__wait_element('//*[@id="root"]/div/div/h1', 60)
            go_to_login_page_button = self.__find_element_x(
                '//*[@id="root"]/div/div/button'
            )
            if go_to_login_page_button.get_attribute("disabled") is None:
                self.click(go_to_login_page_button)
            login_input = self.__find_element_x(
                '//*[@id="root"]/div/div/div[1]/label/textarea'
            ).send_keys(seed_phrase)
            self.driver.implicitly_wait(5)
            click_login_button = self.__find_element_x(
                '//*[@id="root"]/div/div/div[2]/button'
            )
            self.click(click_login_button)
            submit_login_button = self.__wait_element(
                '//*[@id="root"]/div/div/div[2]/button', 100
            )
            self.click(submit_login_button)
            for i in range(100):
                try:
                    wait_here_tabs = self.__wait_element("here-tabs", 2, "ID")
                    break
                except:
                    pass
                try:
                    self.__wait_frame_and_switch('//*[@id="captcha"]//div/iframe', 2)
                    captcha_checkbox = self.__wait_element(
                        "/html/body//div/div/div[1]/div/label", 60
                    )
                    self.click(captcha_checkbox)
                    wait_here_tabs = self.__wait_element("here-tabs", 100, "ID")
                    break
                except:
                    pass

            captcha = self.__find_element_x("/html/body/div[1]")
            self.log(captcha.text == "")
            self.logged_in = True
            time.sleep(10)
            return False

    def sign_up(self):
        time.sleep(10)
        self.log(f"SIGNING UP")
        self.__wait_element('//*[@id="root"]/div/div/h1', 60)

        go_to_sign_up_page_button = self.__wait_element(
            '//*[@id="root"]/div/div/div[2]/button', 20
        )
        if go_to_sign_up_page_button.get_attribute("disabled") is None:
            self.click(go_to_sign_up_page_button)
        copy_button = self.__wait_element(
            '//*[@id="root"]/div/div/div[3]/div/div[1]/button', 20
        )
        seed_phrase = self.__find_element_x(
            '//*[@id="root"]/div/div/div[3]/div/div[2]/div'
        ).text
        self.seed_phrase = seed_phrase
        time.sleep(10)
        click_sign_up_button = self.__find_element_x(
            '//*[@id="root"]/div/div/div[4]/button'
        )
        self.click(click_sign_up_button)
        for i in range(100):
            try:
                wait_here_tabs = self.__wait_element("here-tabs", 2, "ID")
                break
            except:
                pass
            try:

                self.__wait_frame_and_switch(
                    "//iframe[@title='Widget containing a Cloudflare security challenge']",
                    2,
                )
                captcha_checkbox = self.__wait_element(
                    "/html/body/div/div/div[1]/div/label", 60
                )
                self.click(captcha_checkbox)
                wait_here_tabs = self.__wait_element("here-tabs", 100, "ID")
                break
            except:
                pass

        self.log(f"Seed Phrase: {seed_phrase}", level="debug")

        self.logged_in = True

        send_sign_up_data = asyncio.run_coroutine_threadsafe(
            bot_send_logs(
                account=self.account["file_name"],
                message=f"✅ Signed up Successfully!\n\nSeed Phrase: {seed_phrase}",
            ),
            self.loop,
        )
        send_sign_up_data.result()
        return {"seed_phrase": seed_phrase}

    def logout(self):
        self.log(f"LOGGING OUT", "info")
        self.open_page(self.__settings_page_url)
        login_button = self.__wait_element(
            '//*[@id="root"]/div/div/div/div[4]/button', 30
        )
        self.click(login_button)
        label_text = self.__wait_element('//*[@id="root"]/div/div/div/label/p', 30).text
        self.log(type(label_text))
        seed_phrase_id = re.search(r"Введите #(\d+) слово вашей Seed-фразы", label_text)
        seed_phrase_id = (
            seed_phrase_id
            if seed_phrase_id != None
            else re.search(r"Enter word #(\d+) from your seed phrase", label_text)
        )
        self.log(seed_phrase_id)
        required_seed_phrase = self.seed_phrase.split(" ")[
            int(seed_phrase_id.group(1)) - 1
        ]

        seed_phrase_input = self.__find_element_x(
            '//*[@id="root"]/div/div/div/label/div/input'
        )
        seed_phrase_input.send_keys(required_seed_phrase)

        login_button = self.__find_element_x('//*[@id="root"]/div/div/button')
        self.click(login_button)

    def claim_bonus_hot(self):
        self.open_page(self.__hot_page_url)
        try:
            follow_button = self.__wait_element(
                "/html/body/div[4]/div/div[2]/div/button", 60
            )
            time.sleep(3)
            self.click(follow_button)
        except:
            self.log(f"Follow button not found", "error")
            hot_balance = float(
                self.__find_element_x(
                    '//*[@id="root"]/div/div/div[2]/div/div[2]/div[3]/p[2]'
                ).text
            )
            if hot_balance >= 0.01:
                return True
            return False
        claim_button = self.__find_element_x("/html/body/div[4]/div/div[2]/div/button")
        self.click(claim_button)
        claim_success = self.__wait_element_disappear("/html/body/div[4]", 60)
        return True

    def get_balance(self, hot=False):
        self.log("Getting total balance", "info")
        self.log(self.driver.current_url)
        if (
            self.driver.current_url != self.__home_page_url
            and self.driver.current_url != self.__here_wallet_url
        ):
            self.open_page(self.__home_page_url)
        time.sleep(60)

        if hot:
            hot_balance_element = self.__wait_element(
                '//*[@id="root"]/div/div/div[1]/div/div/div[4]/div[1]/div[2]/div/p', 20
            ).text
            hot_balance = float(hot_balance_element)
            self.log(f"HOT Balance: ${hot_balance}")
            return hot_balance

        total_balance_element = self.__wait_element(
            '//*[@id="root"]/div/div/div[1]/div/div/div[2]/div[1]/div[1]/div/div/h2', 20
        ).text
        total_balance = float(total_balance_element.replace("$", ""))
        self.log(f"Balance: ${total_balance}")

        chains_block = self.__find_element_x(
            '//*[@id="root"]/div/div/div[1]/div/div/div[6]'
        )
        chains = chains_block.find_elements(By.XPATH, "./*")
        self.log(len(chains))

        for j in range(3):
            try:
                balance = {"total_balance": total_balance}
                for i in range(2, (len(chains))):
                    try:
                        second_balance_element_text = self.__find_element_x(
                            f'//*[@id="root"]/div/div/div[1]/div/div/div[6]/div[{i}]/div[2]/p[1]'
                        ).text
                        # //*[@id="root"]/div/div/div[1]/div/div/div[6]/div[3]
                        if second_balance_element_text == "FREE":
                            continue
                    except:
                        pass
                    parent_chain = chains_block.find_element(By.XPATH, f"div[{i}]")
                    child_chain = parent_chain.find_elements(By.XPATH, "./*")
                    if len(child_chain) > 1:
                        chain_name = chains_block.find_element(
                            By.XPATH, f"div[{i}]/div[1]/div[1]/p[1]"
                        ).text
                        child_chain_name = parent_chain.find_element(
                            By.XPATH, f"div[2]/p[1]"
                        ).text

                        if chain_name == child_chain_name:
                            chain_balance_in_usd_element = chains_block.find_element(
                                By.XPATH, f"div[{i}]/div[2]/div/p"
                            ).text
                            chain_balance_in_usd = float(
                                chain_balance_in_usd_element.replace("$", "")
                            )
                            chain_balance_element = chains_block.find_element(
                                By.XPATH, f"div[{i}]/div[2]/p[2]"
                            ).text
                            chain_balance = float(chain_balance_element)
                            balance[f"{chain_name}/USD"] = chain_balance_in_usd
                            balance[f"{chain_name}"] = chain_balance
                        continue

                    chain_name = chains_block.find_element(
                        By.XPATH, f"div[{i}]/div/div[1]/p[1]"
                    ).text
                    chain_balance_in_usd_element = chains_block.find_element(
                        By.XPATH, f"div[{i}]/div/div[2]/p[1]"
                    ).text
                    chain_balance_in_usd = float(
                        chain_balance_in_usd_element.replace("$", "")
                    )
                    chain_balance_element = chains_block.find_element(
                        By.XPATH, f"div[{i}]/div/div[2]/p[2]"
                    ).text
                    self.log(chain_balance_element)
                    if "~" in chain_balance_element:
                        chain_balance_element = chain_balance_element.replace("~", "")
                    chain_balance = float(chain_balance_element)
                    balance[f"{chain_name}/USD"] = chain_balance_in_usd
                    balance[f"{chain_name}"] = chain_balance
                self.log(balance)
                return balance
            except:
                time.sleep(20)
        raise LookupError

    def configure_transfer_account(self):
        self.open_page(Config.main_here_wallet_url)
        self.login(Config.main_seed_phrase)

    def transfer(self, chain: str, address: str, amount: int = 0):
        self.log(
            f"Transferring tokens on {chain} chain, amount of {amount} to {address}",
            "info",
        )
        if chain == Config.eth_chain:
            amount = (
                decimal.Decimal(
                    round((amount if amount != 0 else Config.transfer_eth_amount), 6)
                )
                * Config.default_amount_multiplier
            )
            contract = Config.eth_contract
        if chain == Config.bnb_chain:
            amount = (
                decimal.Decimal(
                    round((amount if amount != 0 else Config.transfer_bnb_amount), 5)
                )
                * Config.default_amount_multiplier
            )
            contract = Config.bnb_contract
        if chain == Config.near_chain:
            amount = (
                decimal.Decimal(amount if amount != 0 else Config.transfer_near_amount)
                * Config.near_default_amount_multiplier
            )
            contract = Config.near_contract
        if chain == Config.ton_chain:
            amount = (
                decimal.Decimal(amount if amount != 0 else Config.transfer_ton_amount)
                * Config.ton_default_amount_multiplier
            )
            contract = Config.ton_contract
        if chain == Config.tron_chain:
            amount = (
                decimal.Decimal(amount if amount != 0 else Config.transfer_tron_amount)
                * Config.tron_default_amount_multiplier
            )
            contract = Config.tron_contract

        transfer_url = self.get_transfer_url(chain, contract, address, amount)
        self.open_page(transfer_url)

        transfer_submit_button = self.__wait_element(
            '//*[@id="root"]/div/div/button[1]', 60
        )
        time.sleep(10)
        self.click(transfer_submit_button)
        try:
            transfer_success_button = self.__wait_element(
                '//*[@id="root"]/div/div/button', 100
            )
            self.log(f"Transferred successfully!", "info")
            return True
        except Exception as e:
            self.log(e)
            return False

    def swap(self, chain, from_contract, to_contract, amount=None):
        if chain == Config.eth_chain:
            slippage = Config.eth_slippage
            amount = 0.0025 if amount is None else amount
        elif chain == Config.bnb_chain:
            slippage = Config.bnb_slippage
            amount = 0.0025 if amount is None else amount
        elif chain == Config.near_chain:
            slippage = Config.near_slippage
            amount = 0.0025 if amount is None else amount

        swap_url = self.get_swap_url(chain, from_contract, to_contract, slippage)
        self.open_page(swap_url)

        change_currency_to_usd_button = self.__wait_element(
            '//*[@id="root"]/div/div/div[1]/div[2]/div[3]/button[1]', 20
        )
        self.click(change_currency_to_usd_button)
        time.sleep(5)
        if str(amount).lower() == "all" or str(amount).lower() == "max":
            amount_max_button = self.__find_element_x(
                '//*[@id="root"]/div/div/div[1]/div[2]/div[3]/button[2]'
            )
            self.click(amount_max_button)
        else:
            amount_input = self.__find_element_x(
                '//*[@id="root"]/div/div/div[1]/div[2]/div[1]/input'
            )
            amount_input.send_keys(str(amount).replace(".", ","))

        view_swap_button_load = self.__wait_element_disappear(
            '//*[@id="root"]/div/div/div[1]/button/svg', 30
        )
        time.sleep(30)
        view_swap_button = self.__find_element_x(
            '//*[@id="root"]/div/div/div[1]/button'
        )
        if view_swap_button.get_attribute("disabled") is None:
            self.click(view_swap_button)
        else:
            self.log(
                f"Swap chain: {chain} | amount {amount} | from {from_contract} to {to_contract} -> Not enough money",
                "error",
            )
            return False
        submit_swap_button = self.__wait_element(
            '//*[@id="root"]/div/div/div/button[1]', 20
        )
        self.click(submit_swap_button)

        try:
            success_img = self.__wait_element(
                '//*[@id="root"]/div/div/div/div[2]/button', 200
            )
            # //*[@id="root"]/div/div/div/div[1]/div[4]/div/div/img[1]
            self.log(
                f"Swap of amount {amount} on {chain} chain from contract {from_contract} to contract {to_contract} was successful",
                "info",
            )
            return True
        except:
            self.log(
                f"Swap chain: {chain} | amount {amount} | from {from_contract} to {to_contract} -> Something went wrong",
                "error",
            )
            return False

    def bridge(self, token, from_chain, to_chain, amount=None):
        self.log(
            f"Bridge of amount {amount} on {token} from {from_chain} to {to_chain}"
        )
        if token == "ETH":
            amount = amount if amount is not None else 2

        bridge_url = self.get_bridge_url(token, from_chain, to_chain)
        self.open_page(bridge_url)

        change_currency_to_usd = self.__wait_element(
            '//*[@id="root"]/div/div/div[2]/div[3]/button[1]', 30
        )
        self.click(change_currency_to_usd)

        time.sleep(5)
        if str(amount).lower() == "all" or str(amount).lower() == "max":
            choice_max_amount = self.__find_element_x(
                '//*[@id="root"]/div/div/div[2]/div[3]/button[2]'
            )
            self.click(choice_max_amount)
        else:
            amount_input = self.__find_element_x(
                '//*[@id="root"]/div/div/div[2]/div[1]/input'
            )
            amount_input.send_keys(str(amount))

        view_loading = self.__wait_element_disappear(
            '//*[@id="root"]/div/div/button/svg', 30
        )
        time.sleep(30)
        view_bridge_button = self.__find_element_x('//*[@id="root"]/div/div/button')
        if view_bridge_button.get_attribute("disabled") is None:
            self.click(view_bridge_button)
        else:
            self.log(
                f"Bridge TOKEN: {token} | amount {amount} | from {from_chain} to {to_chain} -> Not enough money",
                "error",
            )
            return False
        submit_bridge_button = self.__wait_element(
            '//*[@id="root"]/div/div/div/div/button[1]', 30
        )
        self.click(submit_bridge_button)

        try:
            success_img = self.__wait_element(
                '//*[@id="root"]/div/div/div/div/div[1]/img', 100
            )
            self.log(
                f"Bridge of amount {amount} on {token} token from chain {from_chain} to chain {to_chain} was successful",
                "info",
            )
            return True  # Bridge was successful
        except:
            self.log(
                f"Bridge token: {token} | amount {amount} | from {from_chain} to {to_chain} -> Something went wrong",
                "error",
            )
            return False

    def claim_mission_reward(self, chain, mission_id: int, claim_button_id: int = 1):
        self.log(f"chain: {chain}, mission_id: {mission_id}")
        if chain == Config.eth_chain:
            mission_page = self.eth_mission_url
        elif chain == Config.bnb_chain:
            mission_page = self.bnb_mission_url
        elif chain == Config.ton_chain:
            mission_page = self.ton_mission_url
        elif chain == Config.tron_chain:
            mission_page = self.tron_mission_url
        elif chain == Config.hot_chain:
            mission_page = self.hot_mission_url

        self.open_page(mission_page)

        status = self.__wait_element(
            f'//*[@id="root"]/div/div/div[2]/div[3]/div[{mission_id + 1}]/div/div/div/p',
            30,
        )
        time.sleep(5)
        status = status.text
        self.log(status)
        if status == "Completed" or status == "Выполнено":
            self.log(
                f"Claim mission on {chain} with ID: {mission_id} -> Mission is already completed",
                "error",
            )
            return True  # mission is already completed, don't try to claim again

        mission_element = self.__wait_element(
            f'//*[@id="root"]/div/div/div[2]/div[3]/div[{mission_id + 1}]', 20
        )
        self.driver.execute_script("arguments[0].scrollIntoView();", mission_element)

        mission_element_is_clickable = self.__wait_element_clickable(
            f'//*[@id="root"]/div/div/div[2]/div[3]/div[{mission_id + 1}]', 20
        )

        self.click(mission_element)

        if claim_button_id > 0:
            claim_button = self.__wait_element(
                f"/html/body/div[4]/div/div[2]/div/div/button[{claim_button_id}]", 20
            )
            claim_button_is_clickable = self.__wait_element_clickable(
                f"/html/body/div[4]/div/div[2]/div/div/button[{claim_button_id}]", 20
            )
            self.click(claim_button)
        else:
            claim_button = self.__wait_element(
                "/html/body/div[4]/div/div[2]/div/div/button", 20
            )
            claim_button_is_clickable = self.__wait_element_clickable(
                f"/html/body/div[4]/div/div[2]/div/div/button", 20
            )
            self.click(claim_button)

        success_message = self.get_log_message()

        if (
            success_message == "Mission completed!"
            or success_message == "HOT claimed!"
            or success_message == "HOT получен!"
        ):
            self.log(
                f"Claim mission reward on {chain} chain for mission ID {mission_id} was successful [{success_message}]",
                "info",
            )
            return True
        elif success_message == "Payment have been processed already":
            self.log(
                f"Payment have been processed already for mission ID {mission_id}",
                "error",
            )
            return True
        else:
            return False

    def claim_mining_hot(self):
        self.open_page(self.__hot_page_url)
        self.__wait_element(
            '//*[@id="root"]/div/div/div[2]/div/div[3]/div/div[2]/div[2]/button', 40
        )
        time.sleep(5)
        while True:
            claim_button = self.__find_element_x(
                '//*[@id="root"]/div/div/div[2]/div/div[3]/div/div[2]/div[2]/button'
            )
            self.log(claim_button.text)
            if claim_button.text == "Новости" or claim_button.text == "Check NEWS":
                self.click(claim_button)
                try:
                    self.log("Hot claim PASSWORD required...", "info")
                    watch_video_modal = self.__wait_element(
                        "/html/body/div[4]/div/div[2]/div", 10
                    )
                    watch_video_button = self.__find_element_x(
                        "/html/body/div[4]/div/div[2]/div/div/div[2]/button"
                    )
                    if watch_video_button.get_attribute("disabled") is None:
                        self.click(watch_video_button)
                    watch_video_button_2 = self.__wait_element(
                        "/html/body/div[4]/div/div[2]/div/div/div[2]/button[2]", 60
                    )
                    submit_password_button = self.__find_element_x(
                        "/html/body/div[4]/div/div[2]/div/div/div[2]/button[1]"
                    )
                    if submit_password_button.get_attribute("disabled") is None:
                        self.click(submit_password_button)
                    enter_password_input = self.__wait_element(
                        '//*[@id="root"]/div/div/div/label/div/input', 60
                    )
                    enter_password_input.send_keys(Config.hot_password)
                    submit_password_button = self.__find_element_x(
                        '//*[@id="root"]/div/div/div/div/button'
                    )
                    if submit_password_button.get_attribute("disabled") is None:
                        self.click(submit_password_button)
                except:
                    pass
            if claim_button.get_attribute("disabled") is None:
                count_input = self.__wait_element(
                    '//*[@id="root"]/div/div/div[2]/div/div[2]/div[2]/h1', 30
                ).text
                self.log(count_input)
                current_mined_hot = float(count_input)
                self.log(f"Claiming {current_mined_hot} hot")
                self.click(claim_button)
                claiming = self.__wait_element_disappear(
                    '//*[@id="root"]/div/div/div[2]/div/div[3]/div/div[2]/div[2]/button/svg',
                    30,
                )
                time.sleep(60)
            else:
                self.log("Cannot claim hot, button is disabled", "info")
                return False
            try:
                bombs_count = int(
                    self.__find_element_x(
                        '//*[@id="root"]/div/div/div[2]/div/div[1]/div[2]/div[1]/p'
                    ).text
                )
            except:
                self.log("Cannot find bombs count", "error")
                return True
            if bombs_count == 0:
                self.log("Success! No more bombs to claim", "info")
                return True

            open_bomb_modal_button = self.__find_element_x(
                '//*[@id="root"]/div/div/div[2]/div/div[3]/div[1]'
            )
            self.click(open_bomb_modal_button)

            choice_bomb = self.__wait_element(
                f"/html/body/div[4]/div/div[2]/div/div/div[1]"
            )

            if choice_bomb:
                self.click(choice_bomb)
                activate_bomb_button = self.__find_element_x(
                    "/html/body/div[4]/div/div[2]/div/button"
                )
                if activate_bomb_button.get_attribute("disabled") is None:
                    self.click(activate_bomb_button)
                    activating = self.__wait_element_disappear(
                        "/html/body/div[4]/div/div[2]", 60
                    )
                    if activating:
                        self.log(f"Bomb activated => Success!")
                else:
                    self.log(f"Bomb activation => Something went wrong", "error")
                    return False
            else:
                self.log(f"Cannot activate bomb => No bomb button", "error")
                return False

    def first_mission(self):
        if self.get_balance(hot=True) == 0.21:
            return True

        self.open_page("https://tgapp.herewallet.app/missions")

        mission_button = self.__wait_element(
            '//*[@id="root"]/div/div/div[1]/div/div[1]', 60
        )
        if mission_button:
            self.click(mission_button)

        required_seed_phrase_text = self.__wait_element(
            "/html/body/div[4]/div/div[2]/div/div[1]/p", 60
        ).get_attribute("innerHTML")

        required_seed_phrase_id = int(
            re.search(r"Select (\d+)", required_seed_phrase_text).group(1)
        )
        self.log(f"Required seed phrase id: {required_seed_phrase_id}")

        required_seed_phrase_word = self.seed_phrase.split(" ")[
            required_seed_phrase_id - 1
        ]
        self.log(f"Required seed phrase word: {required_seed_phrase_word}")

        for i in range(1, 8):
            block_seed_phrase = self.__find_element_x(
                f"/html/body/div[4]/div/div[2]/div/div[1]/div/div[{i}]/p"
            )
            self.log(
                f"{i} - Block seed phrase: {block_seed_phrase.get_attribute('innerHTML')}"
            )

            if (
                block_seed_phrase.get_attribute("innerHTML").strip()
                == required_seed_phrase_word
            ):
                self.click(block_seed_phrase)
                break

        time.sleep(5)
        claim_button = self.__wait_element(
            "/html/body/div[4]/div/div[2]/div/div[2]/button", 5
        )
        if claim_button.get_attribute("disabled") is None:
            self.click(claim_button)
        else:
            self.first_mission()

        success_message = self.get_log_message()

        if (
            success_message == "Mission completed!"
            or success_message == "HOT claimed!"
            or success_message == "HOT получен!"
        ):
            self.log(f"First mission completed => Success! [{success_message}]", "info")
            return True
        elif success_message == "Payment have been processed already":
            self.log(
                f"First mission completed => Payment have been processed already for first mission",
                "info",
            )
            return True
        else:
            return False

    def join_village(self, village_id: str):

        self.open_page(f"{self.__village_url}/{village_id}")
        time.sleep(20)
        main_block = self.__wait_element(
            '//*[@id="root"]/div/div/div[3]/div/div/div[1]', 60
        )
        main_block_count = len(main_block.find_elements(By.XPATH, "./div"))
        self.log(f"Main block count: {main_block_count}")

        join_block_id = main_block_count - 1

        buttons_parent_element = self.__wait_element(
            f'//*[@id="root"]/div/div/div[3]/div/div/div[1]/div[{join_block_id}]', 60
        )

        buttons_count = len(buttons_parent_element.find_elements(By.TAG_NAME, "button"))
        self.log(f"Buttons count: {buttons_count}")
        if buttons_count == 4:
            return True
        if buttons_count == 0:
            return "Private"

        join_button = self.__wait_element(
            f'//*[@id="root"]/div/div/div[3]/div/div/div[1]/div[{join_block_id}]/button[3]',
            10,
        )
        if join_button:
            self.click(join_button)

        submit_join_button = self.__wait_element(
            "/html/body/div[4]/div/div[2]/div/button", 30
        )

        if submit_join_button.get_attribute("disabled") is None:
            self.click(submit_join_button)

        success_message = self.get_log_message()
        if success_message == "You have joined the village":
            self.log(f"Join village => Success! [{success_message}]", "info")
            return True
        else:
            self.log(f"Join village => Failed! [{success_message}]", "error")
            return False

    def hapi_score_missions(self):
        self.open_page(self.__hapi_score_url)

        self.__wait_frame_and_switch('//*[@id="root"]/div/div/iframe', 30)

        for i in range(100):
            time.sleep(1)
            networks_tab = self.__wait_element(
                '//*[@id="root"]/div[2]/div/div[2]/div[2]', 100
            )
            no_scrollbar_in_tab = "no-scrollbar" in networks_tab.get_attribute("class")
            if no_scrollbar_in_tab:
                switch_to_near_button = self.__find_element_x(
                    '//*[@id="root"]/div[2]/div/div[2]/div[2]/div[2]'
                )
                self.click(switch_to_near_button)
                break
        try:
            wait_mint_button = self.__wait_element(
                f'//*[@id="root"]/div[2]/div/div[2]/div[4]/div/div[1]/button', 60
            )
        except:
            wait_mint_button = False

        if wait_mint_button:
            for i in range(100):
                time.sleep(1)
                mint_button = self.__find_element_x(
                    '//*[@id="root"]/div[2]/div/div[2]/div[4]/div/div[1]/button'
                )
                if mint_button.get_attribute("disabled") is None:
                    time.sleep(10)
                    hapi_score = self.__find_element_x(
                        '//*[@id="root"]/div[2]/div/div[2]/div[3]/div/div[3]/span[1]'
                    ).text
                    if int(hapi_score) > 30:
                        self.click(mint_button)
                    else:
                        self.log("Hapi score is less than 30", "info")
                        return False
                    break
            else:
                self.log("Mint button not found or disabled", "error")
                return False

            self.driver.switch_to.default_content()
            submit_mint_button = self.__wait_element(
                "/html/body/div[4]/div/div[2]/div/button[1]", 30
            )
            if (
                submit_mint_button
                and submit_mint_button.get_attribute("disabled") is None
            ):
                self.click(submit_mint_button)
            else:
                self.log("Submit mint button not found or disabled", "error")
                return False
            # [-32700] Parse error: Failed parsing args: data did not match any variant of untagged enum TransactionInfo

            self.__wait_frame_and_switch('//*[@id="root"]/div/div/iframe', 30)

        level_id = 0
        block_id = 0
        try:
            second_level = self.__wait_element(
                '//*[@id="root"]/div[2]/div/div[2]/div[4]/div[2]/div[2]/button', 100
            )
            level_id = 4
            block_id = 2
        except:
            try:
                second_level = self.__wait_element(
                    '//*[@id="root"]/div[2]/div/div[2]/div[4]/div[3]/div[2]/button', 5
                )
                level_id = 4
                block_id = 3
                # //*[@id="root"]/div[2]/div/div[2]/div[5]/div[3]/div[2]/button
            except:
                for i in range(5, 7):
                    for j in range(2, 4):
                        try:
                            second_level = self.__wait_element(
                                f'//*[@id="root"]/div[2]/div/div[2]/div[{i}]/div[{j}]/div[2]/button',
                                5,
                            )
                            level_id = i
                            block_id = j
                            break
                        except:
                            pass
                    if level_id == 0 and block_id == 0:
                        break

        if second_level and second_level.get_attribute("disabled") is None:
            self.click(second_level)
        elif second_level.get_attribute("disabled") is not None:
            self.log("Check news button is disabled")
        else:
            self.log("Check news button not found or disabled", "error")
            return False

        time.sleep(2)
        self.switch_window(0)
        self.__wait_frame_and_switch('//*[@id="root"]/div/div/iframe', 30)

        third_level = self.__wait_element(
            f'//*[@id="root"]/div[2]/div/div[2]/div[{level_id}]/div[{block_id}]/div[3]',
            60,
        )
        if third_level:
            self.click(third_level)
        else:
            self.log("Check news button not found", "error")
            return False

        connect_telegram = self.__wait_element(
            "/html/body/div[5]/div/div[2]/div/div[2]/div[2]/div[1]", 60
        )
        if connect_telegram:
            self.click(connect_telegram)
        else:
            self.log("Connect Telegram button not found", "error")
            return False

        connect_success = self.__wait_element(
            "/html/body/div[5]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/div", 60
        )
        if connect_success and connect_success.text == "Completed":
            self.log("Hapi score missions are successfully completed!", "info")
            return True
        # Telegram connected successfully

    def cave(self):
        self.open_page(self.__cave_url)

        submit_button_xpath = "/html/body/div[4]/div/div[2]/div/button"

        wooden_storage = self.__wait_element(
            '//*[@id="root"]/div/div/div[4]/div/div[2]/div', 60
        )
        wooden_level_p = self.__find_element_x(
            '//*[@id="root"]/div/div/div[4]/div/div[2]/div/div/div/p[2]'
        ).text
        wooden_level = int(re.search(r"(\d+)", wooden_level_p).group(1))
        self.log(wooden_level)

        fireplace = self.__find_element_x(
            '//*[@id="root"]/div/div/div[4]/div/div[3]/div[1]'
        )
        fireplace_level_p = self.__find_element_x(
            '//*[@id="root"]/div/div/div[4]/div/div[3]/div[1]/div/div/p[2]'
        ).text
        fireplace_level = int(re.search(r"(\d+)", fireplace_level_p).group(1))
        self.log(fireplace_level)

        # wooden_update
        for wooden_id in range(2 - wooden_level):
            wooden_storage = self.__wait_element(
                '//*[@id="root"]/div/div/div[4]/div/div[2]/div', 20
            )
            self.click(wooden_storage)
            time.sleep(1)
            submit_button = self.__wait_element(submit_button_xpath, 30)
            if submit_button.get_attribute("disabled") is None:
                self.click(submit_button)
            time.sleep(1)
            success_image = self.__wait_element(
                "/html/body/div[4]/div/div[2]/div/img", 120
            )
            time.sleep(1)
            submit_button = self.__wait_element(submit_button_xpath, 30)
            if submit_button.get_attribute("disabled") is None:
                self.click(submit_button)
            modal_disappear = self.__wait_element_disappear("/html/body/div[4]", 30)
            time.sleep(2)

        # fireplace_update
        for fireplace_id in range(3 - fireplace_level):
            fireplace = self.__wait_element(
                '//*[@id="root"]/div/div/div[4]/div/div[3]/div[1]', 20
            )
            self.click(fireplace)
            time.sleep(1)
            submit_button = self.__wait_element(submit_button_xpath, 30)
            if submit_button.get_attribute("disabled") is None:
                self.click(submit_button)
            time.sleep(1)
            success_image = self.__wait_element(
                "/html/body/div[4]/div/div[2]/div/img", 120
            )
            time.sleep(1)
            submit_button = self.__wait_element(submit_button_xpath, 30)
            if submit_button.get_attribute("disabled") is None:
                self.click(submit_button)
            modal_disappear = self.__wait_element_disappear("/html/body/div[4]", 30)
            time.sleep(2)

        wooden_level_p = self.__find_element_x(
            '//*[@id="root"]/div/div/div[4]/div/div[2]/div/div/div/p[2]'
        ).text
        wooden_level = int(re.search(r"(\d+)", wooden_level_p).group(1))
        fireplace_level_p = self.__find_element_x(
            '//*[@id="root"]/div/div/div[4]/div/div[3]/div[1]/div/div/p[2]'
        ).text
        fireplace_level = int(re.search(r"(\d+)", fireplace_level_p).group(1))

        if wooden_level == 2 and fireplace_level == 3:
            self.log("Cave actions done!", "info")
            return True

    def boosters(self):
        self.open_page(self.boosters_mission_url)

        time.sleep(2)
        self.driver.refresh()
        time.sleep(10)

        add_near_mission_xpath = '//*[@id="root"]/div/div/div[4]/div[2]/div[2]'
        add_usdt_mission_xpath = '//*[@id="root"]/div/div/div[4]/div[2]/div[3]'

        add_near_mission_button = self.__wait_element(add_near_mission_xpath, 60)
        try:
            add_near_mission_svg = add_near_mission_button.find_element(
                By.TAG_NAME, "svg"
            )
            self.log(add_near_mission_svg)
            if add_near_mission_svg:
                self.click(add_near_mission_button)
            submit_button = self.__wait_element(
                "/html/body/div[4]/div/div[2]/div/div/div[2]/button[2]", 30
            )
            if submit_button.get_attribute("disabled") is None:
                self.click(submit_button)

            wait_success_img = self.__wait_element(
                "/html/body/div[4]/div/div[2]/div/img", 120
            )
            got_it_button = self.__find_element_x(
                "/html/body/div[4]/div/div[2]/div/button"
            )
            self.click(got_it_button)
            time.sleep(5)

        except Exception as e:
            self.log(str(e))

        add_usdt_mission_button = self.__wait_element(add_usdt_mission_xpath, 60)
        try:
            add_usdt_mission_svg = add_usdt_mission_button.find_element(
                By.TAG_NAME, "svg"
            )
            self.log(add_usdt_mission_svg)
            if add_usdt_mission_svg:
                self.click(add_usdt_mission_button)
            submit_button = self.__wait_element(
                "/html/body/div[4]/div/div[2]/div/div/div[2]/button[2]", 30
            )
            if submit_button.get_attribute("disabled") is None:
                self.click(submit_button)

            wait_success_img = self.__wait_element(
                "/html/body/div[4]/div/div[2]/div/img", 120
            )
            got_it_button = self.__find_element_x(
                "/html/body/div[4]/div/div[2]/div/button"
            )
            self.click(got_it_button)
            time.sleep(5)

        except Exception as e:
            self.log(str(e))

        near_mission_status = self.__find_element_x(
            '//*[@id="root"]/div/div/div[4]/div[2]/div[2]/div/div/p'
        ).text
        usdt_mission_status = self.__find_element_x(
            '//*[@id="root"]/div/div/div[4]/div[2]/div[3]/div/div/p'
        ).text
        if (
            near_mission_status == "Выполнено" or near_mission_status == "Completed"
        ) and (
            usdt_mission_status == "Выполнено" or usdt_mission_status == "Completed"
        ):
            return True
        else:
            return False

    def video_missions(self):
        answers_of_missions = {
            "https://tgapp.herewallet.app/missions/submit/explore_youtube_market_codeword": "Popcorn",
            "https://tgapp.herewallet.app/missions/submit/explore_youtube_market_makers": "Profit",
            "https://tgapp.herewallet.app/missions/submit/explore_crypto_airdrops": "Free",
            "https://tgapp.herewallet.app/missions/submit/explore_youtube_memecoins": "Hype",
            "https://tgapp.herewallet.app/missions/submit/crypto_swaps_yt": "Commissions",
            "https://tgapp.herewallet.app/missions/submit/explore_youtube_ton2": "Discover",
            "https://tgapp.herewallet.app/missions/submit/explore_youtube_basics_blockchain": "Community",
            "https://tgapp.herewallet.app/missions/submit/basics_tokens": "Explore And Learn",
            "https://tgapp.herewallet.app/missions/submit/basics_world": "Try island hopping",
            "https://tgapp.herewallet.app/missions/submit/top_wallet": "Seed Phrase",
            "https://tgapp.herewallet.app/missions/submit/basics": "Smart Contracts",
            "https://tgapp.herewallet.app/missions/submit/four_steps": "Hot mining",
            "https://tgapp.herewallet.app/missions/submit/explore_youtube_crazy_crypto": "Imagination",
            "https://tgapp.herewallet.app/missions/submit/explore_youtube_ton": "Fast",
            "https://tgapp.herewallet.app/missions/submit/solana_simply_explained": "MarketPlace",
        }

        submitted_missions_count = 0

        for mission_submit_page in answers_of_missions.keys():
            self.open_page(mission_submit_page)

            answer_input = self.__wait_element(
                '//*[@id="root"]/div/div/div[1]/label/div/input', 60
            )
            answer_input.send_keys(answers_of_missions[mission_submit_page])
            time.sleep(5)

            submit_button = self.__find_element_x(
                '//*[@id="root"]/div/div/div[2]/button'
            )
            if submit_button.get_attribute("disabled") == None:
                self.click(submit_button)

            success_message = self.get_log_message()

            if (
                success_message == "Mission completed!"
                or success_message == "HOT claimed!"
                or success_message == "HOT получен!"
            ):
                self.log(
                    f"Answer of {answers_of_missions[mission_submit_page]} for {mission_submit_page} was successfully submitted [{success_message}]",
                    "info",
                )
                submitted_missions_count += 1
            elif success_message == "Payment have been processed already":
                self.log(
                    f"Payment have been processed already for {mission_submit_page}",
                    "error",
                )
                submitted_missions_count += 1

        self.log(
            f"Successfully submitted answers on {submitted_missions_count} QVs",
            level="info",
        )
        return submitted_missions_count


def claim_hot_action(user_id, loop):
    pool.acquire()
    db = DataBase()
    account = db.get_account_data(user_id)
    automation = WebAutomation(
        account=account, profile_id=account["profile_id"], loop=loop
    )

    logger.info(f"[{account['user_id']}] | Claiming hot {account['claim_hot']+1} time")
    automation.home_page()

    if account["seed_phrase"] != "":
        automation.login(account["seed_phrase"])

    if account["claim_hot"] < account["claim_max"]:
        claim_hot = automation.claim_mining_hot()
        if claim_hot:
            db.update_account_data(
                account["user_id"], {"claim_hot": account["claim_hot"] + 1}
            )
            account = db.get_account_data(account["user_id"])
            logger.info(f'Hot claimed: {account["file_name"]}')
        else:
            logger.info(f'Hot not claimed: {account["file_name"]}')
        del automation
        del db
        pool.release()


def create_transfer_account(
    bnb: bool = False, near: bool = False, trx: bool = False, ton: bool = False
):
    global transfer_eligability
    global transfer_accounts_in_usage
    with lock:
        # adspower = AdsPower()
        if Config.using_anti_detect_browser == "Ads":
            profile_id = "Transfer"
        elif Config.using_anti_detect_browser == "Dolphin":
            dolphin = Dolphin()
            while not profile_id:
                time.sleep(1)
                profile_id = dolphin.get_transfer_profile()

        transfer_automation = WebAutomation(head=True, profile_id=profile_id)
        transfer_automation.home_page()
        balance = transfer_automation.get_balance()

        if (
            (
                (
                    "BNB" in balance.keys()
                    and balance["BNB"]
                    >= Config.transfer_bnb_amount * transfer_accounts_in_usage
                )
                or bnb
            )
            and (
                (
                    "NEAR" in balance.keys()
                    and balance["NEAR"]
                    >= Config.transfer_near_amount * transfer_accounts_in_usage
                )
                or near
            )
            and (
                (
                    "TRX" in balance.keys()
                    and balance["TRX"]
                    >= Config.transfer_tron_amount * transfer_accounts_in_usage
                )
                or trx
            )
            and (
                (
                    "TON" in balance.keys()
                    and balance["TON"]
                    >= Config.transfer_ton_amount * transfer_accounts_in_usage
                )
                or ton
            )
            and transfer_eligability
        ):
            # transfer_automation.configure_transfer_account()
            return transfer_automation

        else:
            transfer_eligability = False
            return False


def automate_here_wallet(account, loop):
    global transfer_eligability
    try:
        if not transfer_eligability:
            accounts.append(account)
            return
        logger.debug(f"New THREAD: {account['file_name']}")

        db = DataBase()
        dolphin = Dolphin(Config.dolphin_api_key)

        # GETTING REFERRER CODE ---------------------------------------------
        if not bool(account["referrer"]):
            referrer = ref_code_action()
            if referrer is None:
                db.update_account_data(
                    account["user_id"], {"referrer": Config.main_referral_code}
                )
            else:
                referrer_data = db.get_account_data(int(referrer))
                referrer_id = referrer_data["ref_code"]
                logger.debug(f"{account['file_name']} | Referrer: {referrer_id}")
                db.update_account_data(
                    account["user_id"], {"referrer": int(referrer_id)}
                )

            account = db.get_account_data(account["user_id"])

        # GETTING PROFILE_ID FROM DOLPHIN -----------------------------------
        if not bool(account["profile_id"]):
            proxy = None
            if account["proxy"] != "":
                proxy = account["proxy"]
            profile_id = None
            adspower = AdsPower()
            while not profile_id:
                if Config.using_anti_detect_browser == "Dolphin":
                    profile_id = dolphin.new_profile(
                        user_id=account["user_id"], proxy=proxy
                    )
                elif Config.using_anti_detect_browser == "Ads":
                    profile_id = adspower.create_profile(
                        proxy=proxy, name=account["user_id"]
                    )
                if not profile_id:
                    time.sleep(20)
            db.update_account_data(account["user_id"], {"profile_id": profile_id})
            account = db.get_account_data(account["user_id"])

        automation = WebAutomation(
            account=account, profile_id=account["profile_id"], loop=loop
        )

        time.sleep(2)
        automation.home_page()

        # CREATING OR LOGGING IN --------------------------------------------
        if account["seed_phrase"] != "":
            login = automation.login(account["seed_phrase"])
            if login:
                db.update_account_data(account["user_id"], {"logged_in": 1})

        else:
            sign_up_data = automation.sign_up()

            db.update_account_data(account["user_id"], sign_up_data)
            account = db.get_account_data(account["user_id"])

        # CLAIMING FIRST BONUS -----------------------------------------------
        if not bool(account["bonus_claimed"]):
            bonus_claimed = automation.claim_bonus_hot()
            if bonus_claimed:
                db.update_account_data(account["user_id"], {"bonus_claimed": 1})
                account = db.get_account_data(account["user_id"])
            else:
                pool.release()
                return

        # GETTING REFERRAL CODE ---------------------------------------------
        if account["ref_code"] == 0 or account["ref_code"] == None:
            ref_code = automation.get_ref_code()
            if ref_code == None:
                pool.release()
                return
            db.update_account_data(account["user_id"], {"ref_code": ref_code})
            ref_code_action("append", account["user_id"])
            account = db.get_account_data(account["user_id"])

        if bool(account["bonus_claimed"]) and (
            not bool(account["eth_mission_id"])
            and not bool(account["bnb_mission_id"])
            and not bool(account["ton_mission_id"])
            and not bool(account["tron_mission_id"])
        ):
            addresses = automation.get_addresses()
            if len(addresses.keys()) == 7:
                db.update_account_data(account["user_id"], addresses)
                account = db.get_account_data(account["user_id"])
            else:
                return

        # FIRST MISSION COMPLETION --------------------------------------------
        if (
            not bool(account["eth_mission_id"])
            and not bool(account["bnb_mission_id"])
            and not bool(account["ton_mission_id"])
            and not bool(account["tron_mission_id"])
        ):
            first_mission_completed = True  # automation.first_mission()
            if first_mission_completed:
                db.update_account_data(
                    account["user_id"],
                    {
                        "eth_mission_id": Config.eth_first_mission_id,
                        "bnb_mission_id": Config.bnb_first_mission_id,
                        "ton_mission_id": Config.ton_first_mission_id,
                        "tron_mission_id": Config.tron_first_mission_id,
                    },
                )
                account = db.get_account_data(account["user_id"])

        balance = automation.get_balance()
        # TRANSFER_ACCOUNT --------------------------------------------------
        if (
            (
                "TON/USD" not in balance.keys()
                and account["ton_mission_id"] == Config.ton_first_mission_id
            )
            or (
                "BNB/USD" not in balance.keys()
                and account["bnb_mission_id"] == Config.bnb_first_mission_id
            )
            or (
                "TRX/USD" not in balance.keys()
                and account["tron_mission_id"] == Config.tron_first_mission_id
            )
            or ("NEAR/USD" not in balance.keys())
        ):
            transfer_automation = create_transfer_account(
                bnb="BNB/USD" in balance.keys(),
                near="NEAR/USD" in balance.keys(),
                trx="TRX/USD" in balance.keys(),
                ton="TON/USD" in balance.keys(),
            )
            if not transfer_automation:
                accounts.append(account)
                return
        else:
            transfer_automation = None

        # TON ----------------------------------------------------------------
        if (
            "TON/USD" not in balance.keys()
            and account["ton_mission_id"] == Config.ton_first_mission_id
        ):
            ton_main_transfer = transfer_automation.transfer(
                Config.ton_chain, account["ton_address"]
            )
            if not ton_main_transfer:
                pool.release()
                return
            time.sleep(180)
        else:
            ton_main_transfer = False
        if (
            "TON/USD" in balance.keys()
            and account["ton_mission_id"] == Config.ton_first_mission_id
        ) or ton_main_transfer:
            claim = automation.claim_mission_reward(
                Config.ton_chain, account["ton_mission_id"]
            )
            if not claim:
                pool.release()
                return
            db.update_account_data(
                account["user_id"], {"ton_mission_id": account["ton_mission_id"] + 1}
            )
            account = db.get_account_data(account["user_id"])

        # TRON ----------------------------------------------------------------
        if (
            "TRX/USD" not in balance.keys()
            and account["tron_mission_id"] == Config.tron_first_mission_id
        ):
            tron_main_transfer = transfer_automation.transfer(
                Config.tron_chain, account["tron_address"]
            )
            if not tron_main_transfer:
                pool.release()
                return
            time.sleep(30)
        else:
            tron_main_transfer = False
        if (
            "TRX/USD" in balance.keys()
            and account["tron_mission_id"] == Config.tron_first_mission_id
        ) or tron_main_transfer:
            claim = automation.claim_mission_reward(
                Config.tron_chain, account["tron_mission_id"]
            )
            if not claim:
                pool.release()
                return
            db.update_account_data(
                account["user_id"], {"tron_mission_id": account["tron_mission_id"] + 1}
            )

        # ETH ----------------------------------------------------------------
        if (
            "ETH/USD" not in balance.keys()
            and account["eth_mission_id"] == Config.eth_first_mission_id
        ):
            eth_main_transfer = transfer_automation.transfer(
                Config.eth_chain, account["eth_address"]
            )
            if not eth_main_transfer:
                pool.release()
                return
            time.sleep(30)
        else:
            eth_main_transfer = False
        if (
            "ETH/USD" in balance.keys()
            and account["eth_mission_id"] == Config.eth_first_mission_id
        ) or eth_main_transfer:
            claim = automation.claim_mission_reward(
                Config.eth_chain, account["eth_mission_id"]
            )
            if not claim:
                pool.release()
                return
            db.update_account_data(
                account["user_id"], {"eth_mission_id": account["eth_mission_id"] + 1}
            )
            account = db.get_account_data(account["user_id"])

        # BNB ----------------------------------------------------------------
        if (
            "BNB/USD" not in balance.keys()
            and account["bnb_mission_id"] == Config.bnb_first_mission_id
        ):
            bnb_main_transfer = transfer_automation.transfer(
                Config.bnb_chain, account["base_address"]
            )
            if not bnb_main_transfer:
                pool.release()
                return
            time.sleep(30)
        else:
            bnb_main_transfer = False
        if (
            "BNB/USD" in balance.keys()
            and account["bnb_mission_id"] == Config.bnb_first_mission_id
        ) or bnb_main_transfer:
            claim = automation.claim_mission_reward(
                Config.bnb_chain, account["bnb_mission_id"]
            )
            if not claim:
                pool.release()
                return
            db.update_account_data(
                account["user_id"], {"bnb_mission_id": account["bnb_mission_id"] + 1}
            )
            account = db.get_account_data(account["user_id"])

        # NEAR ----------------------------------------------------------------
        if "NEAR/USD" not in balance.keys():
            near_main_transfer = transfer_automation.transfer(
                Config.near_chain, account["near_address"]
            )
            if not near_main_transfer:
                pool.release()
                return
            time.sleep(30)

        del transfer_automation

        # VILLAGE JOINING ----------------------------------------------------
        if not bool(account["village_id"]):
            join_village = False
            while join_village == "Private" or join_village != True:
                village_id = choice(automation.village_ids)
                join_village = automation.join_village(village_id)
                if join_village == False:
                    pool.release()
                    return
            db.update_account_data(account["user_id"], {"village_id": village_id})

        if not bool(account["claim_max"]):
            max_count = automation.video_missions()
            if max_count and max_count < 10:
                max_count = 10

            claim_max = randint(7, max_count)
            db.update_account_data(account["user_id"], {"claim_max": claim_max})
            account = db.get_account_data(account["user_id"])

        if account["claim_hot"] < account["claim_max"] // 2:
            pool.release()
            del automation
            while account["claim_hot"] < account["claim_max"] // 2:
                timer_thread = Timer(
                    interval=2250,
                    function=claim_hot_action,
                    args=(account["user_id"], loop),
                )
                timer_thread.start()
                time_start = (
                    datetime.now() + timedelta(seconds=Config.default_claim_inverval)
                ).strftime("%d-%m-%Y %H:%M:%S")
                logger.info(
                    f"[{account['file_name']}] Next HOT claiming at {time_start}"
                )
                timer_thread.join()
                account = db.get_account_data(account["user_id"])
            else:
                pool.acquire()
                automate_here_wallet(account)
                return

        # COMPLETING ETH MISSIONS --------------------------------------------
        if (
            account["eth_mission_id"] < Config.eth_last_mission_id + 1
            and account["eth_mission_id"] > Config.eth_first_mission_id
        ):

            for mission_id in range(
                account["eth_mission_id"], Config.eth_last_mission_id + 1
            ):
                logger.info(mission_id)
                if mission_id == Config.eth_first_mission_id + 1:
                    for i in range(1):
                        bridge_1 = automation.bridge(
                            "ETH", Config.eth_chain, Config.near_chain, 5.5
                        )
                        if bridge_1 == False:
                            break
                        bridge_2 = automation.bridge(
                            "ETH", Config.near_chain, Config.eth_chain, "max"
                        )
                        if bridge_2 == False:
                            break

                # if mission_id == Config.eth_first_mission_id+2:
                #     transfer = automation.transfer(Config.eth_chain, Config.eth_address, 0.00005)
                #     if transfer == False: break

                if mission_id == Config.eth_first_mission_id + 2:
                    swap = automation.swap(
                        Config.eth_chain,
                        Config.eth_contract,
                        Config.eth_usdc_contract,
                        5.5,
                    )
                    if swap == False:
                        break

                if mission_id == Config.eth_first_mission_id + 3:
                    swap_amount = randint(5, 10) * 0.01
                    swap = automation.swap(
                        Config.eth_chain,
                        Config.eth_contract,
                        Config.eth_weth_contract,
                        swap_amount,
                    )

                claim_reward = automation.claim_mission_reward(
                    Config.eth_chain, mission_id
                )
                if claim_reward == False:
                    break
                db.update_account_data(
                    account["user_id"], {"eth_mission_id": mission_id + 1}
                )
            else:
                account = db.get_account_data(account["user_id"])

        # COMPLETING BNB MISSIONS --------------------------------------------
        if (
            account["bnb_mission_id"] < Config.bnb_last_mission_id + 1
            and account["bnb_mission_id"] > Config.bnb_first_mission_id
        ):

            for mission_id in range(
                account["bnb_mission_id"], Config.bnb_last_mission_id + 1
            ):

                if mission_id == Config.bnb_first_mission_id + 1:
                    swap = automation.swap(
                        Config.bnb_chain,
                        Config.bnb_contract,
                        Config.bnb_usdt_contract,
                        5.5,
                    )
                    if swap == False:
                        break

                if mission_id == Config.bnb_first_mission_id + 2:
                    swap_amount = randint(5, 10) * 0.01
                    swap = automation.swap(
                        Config.bnb_chain,
                        Config.bnb_contract,
                        Config.bnb_wbnb_contract,
                        swap_amount,
                    )
                    if swap == False:
                        break

                claim_reward = automation.claim_mission_reward(
                    Config.bnb_chain, mission_id
                )
                if claim_reward == False:
                    break
                db.update_account_data(
                    account["user_id"], {"bnb_mission_id": mission_id + 1}
                )
            else:
                account = db.get_account_data(account["user_id"])

        # COMPLETING BOOSTERS -------------------------------------------------
        if not bool(account["boosters_done"]):
            boosters = automation.boosters()
            if not boosters:
                pool.release()
                return
            db.update_account_data(account["user_id"], {"boosters_done": 1})

        # COMPLETING CAVE MISSIONS --------------------------------------------
        if not bool(account["cave_done"]):
            cave = automation.cave()
            if not cave:
                pool.release()
                return
            db.update_account_data(account["user_id"], {"cave_done": 1})

        # TRANSFERRING ALL FUNDS BACK -------------------------------------------
        main_actions_done = (
            (account["bnb_mission_id"] == Config.bnb_last_mission_id + 1)
            and (account["ton_mission_id"] == Config.ton_last_mission_id + 1)
            and (account["tron_mission_id"] == Config.tron_last_mission_id + 1)
            and bool(account["cave_done"])
            and bool(account["boosters_done"])
        )

        if main_actions_done:
            balance = automation.get_balance()

            if "USDC" in balance.keys():
                eth_swap_back = automation.swap(
                    Config.eth_chain,
                    Config.eth_usdc_contract,
                    Config.eth_contract,
                    "max",
                )
                if eth_swap_back == False:
                    pool.release()
                    return

            if "USDT" in balance.keys():
                bnb_swap_back = automation.swap(
                    Config.bnb_chain,
                    Config.bnb_usdt_contract,
                    Config.bnb_contract,
                    "max",
                )
                if bnb_swap_back == False:
                    pool.release()
                    return

            if "USDC" in balance.keys() or "USDT" in balance.keys():
                balance = automation.get_balance()
            if "ETH" in balance.keys() and balance["ETH/USD"] > 0.1:
                eth_transfer_back = automation.transfer(
                    Config.eth_chain, Config.eth_address, balance["ETH"]
                )
            if "BNB" in balance.keys() and balance["BNB/USD"] > 0.1:
                bnb_transfer_back = automation.transfer(
                    Config.bnb_chain, Config.bnb_address, balance["BNB"]
                )
            if "TON" in balance.keys() and balance["TON/USD"] > 0.1:
                ton_transfer_back = automation.transfer(
                    Config.ton_chain, Config.ton_address, balance["TON"] - 0.007
                )
            if "TRX" in balance.keys() and balance["TRX/USD"] > 0.1:
                tron_transfer_back = automation.transfer(
                    Config.tron_chain, Config.tron_address, balance["TRX"]
                )

            transfer_eligability = True

        # CLAIMING HOT ---------------------------
        if account["claim_hot"] < account["claim_max"]:
            pool.release()
            del automation
            while account["claim_hot"] < account["claim_max"]:
                timer_thread = Timer(
                    interval=Config.default_claim_inverval,
                    function=claim_hot_action,
                    args=(account["user_id"], loop),
                )
                timer_thread.start()
                time_start = (
                    datetime.now() + timedelta(seconds=Config.default_claim_inverval)
                ).strftime("%d-%m-%Y %H:%M:%S")
                logger.info(
                    f"[{account['file_name']}] Next HOT claiming at {time_start}"
                )
                timer_thread.join()
                account = db.get_account_data(account["user_id"])
            else:
                pool.acquire()
                automate_here_wallet(account)
                return

        # MINTING AND COMPLETING HAPI SCORE MISSIONS -------------------------
        if not bool(account["hapi_score_done"]):
            balance = automation.get_balance()
            if "UWON" not in balance.keys() and not bool(account["hapi_score_done"]):
                uwon_swap = automation.swap(
                    Config.near_chain,
                    Config.near_contract,
                    Config.near_uwon_contract,
                    5.5,
                )
                if uwon_swap == False:
                    return

                for i in range(5):
                    mini_transfer_back = automation.transfer(
                        Config.near_chain, Config.near_address, 0.0001
                    )
            hapi_score = automation.hapi_score_missions()
            if hapi_score:
                db.update_account_data(account["user_id"], {"hapi_score_done": 1})
                account = db.get_account_data(account["user_id"])

        if bool(account["hapi_score_done"]):
            balance = automation.get_balance()
            if "UWON" in balance.keys() and balance["UWON/USD"] > 0.1:
                claim_reward = automation.claim_mission_reward(
                    Config.hot_chain, Config.hot_first_mission_id
                )
                uwon_swap_back = automation.swap(
                    Config.near_chain,
                    Config.near_uwon_contract,
                    Config.near_contract,
                    "max",
                )
                if uwon_swap_back == False:
                    pool.release()
                    return
            balance = automation.get_balance()
            if "NEAR" in balance.keys() and balance["NEAR/USD"] > 0.1:
                near_transfer_back = automation.transfer(
                    Config.near_chain, Config.near_address, balance["NEAR"] - 0.005
                )

        if (
            main_actions_done
            and account["claim_hot"] <= account["claim_max"]
            and bool(account["hapi_score_done"])
        ):
            db.update_account_data(
                account["user_id"], {"done": 1, "logged_in": 0, "profile_id": 0}
            )
            dolphin.delete_profiles([account["profile_id"]])
    except Exception as e:
        error_send = asyncio.run_coroutine_threadsafe(
            bot_send_logs(account=account["file_name"], message=str(e), type="error"),
            loop,
        )
        logger.error(f"[{account}] | Error: {e}")
        error_send.result()
        pool.release()


@logger.catch
def automation_threads(threads_count: int = 1):
    loop = asyncio.new_event_loop()
    event_loop_thread = threading.Thread(target=start_event_loop, args=(loop,))
    event_loop_thread.start()
    client_run = asyncio.run_coroutine_threadsafe(bot.start(), loop)
    client_run.result()
    db = DataBase()
    global accounts
    accounts = db.get_all_not_done_accounts()
    global threads
    threads = []
    global pool
    pool = BoundedSemaphore(threads_count)
    for account in accounts:
        while not transfer_eligability:
            time.sleep(20)
        logger.info(
            f'Processing account: {account["user_id"]} [{account['file_name']}]'
        )
        pool.acquire()
        thread = Thread(target=automate_here_wallet, args=(account, loop))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    asyncio.run_coroutine_threadsafe(bot.stop(), loop)
