import requests as r
import time
from utils.logger import logger

from config.config import Config

class AdsPower:
    def __init__(self, profile_id: str = None):
        self.host_port = '50325'
        self.profile_id = profile_id

        if profile_id != None:
            profile_data = self.start_profile()
            self.webdriver = profile_data['webdriver']
            self.port = profile_data['port']
            logger.info(f'Webdriver is {self.webdriver} | Port is {self.port}')

    def start_profile(self):
        logger.info(f'Starting profile {self.profile_id}')
        open_url = f"http://local.adspower.com:{self.host_port}/api/v1/browser/start?user_id={self.profile_id}"
        
        response = r.get(open_url).json()

        if response["code"] != 0:
            logger.error(f'While openning profile error occured: {response["msg"]}')
            return

        return {'webdriver': response['data']['webdriver'], 'port': response['data']['ws']['selenium']}
    
    def __del__(self):
        logger.info(f'Closing profile {self.profile_id}')
        if self.profile_id:
            close_url = f"http://local.adspower.com:{self.host_port}/api/v1/browser/stop?user_id={self.profile_id}"
            response = r.get(close_url).json()
            if response['code'] != 0:
                logger.error(f'While openning profile error occured: {response["msg"]}')
                return

    def create_profile(self, proxy: str = None, name: str = 'Profile') -> str:
        create_profile_url = f"http://local.adspower.com:{self.host_port}/api/v1/user/create"

        if proxy:
            s_proxy = proxy.split(':')
            ads_proxy = {
                "proxy_type":"socks5",
                "proxy_host":s_proxy[0],
                "proxy_port":s_proxy[1],
                "proxy_user":s_proxy[2],
                "proxy_password":s_proxy[3],
                "proxy_soft":"other"
            }
        else: ads_proxy = {
            'proxy_soft': 'no_proxy'
        }

        payload = {
        "name": name,
        "group_id": "0",
        "domain_name": "https://tgapp.herewallet.app/home",
        "repeat_config": [
            "0"
        ],
        "fingerprint_config": {
            "flash": "block",
            "fonts": [
                "all"
            ],
            "location": "allow",
            "webrtc": "proxy",
            "do_not_track": "true",
        },
        "user_proxy_config": ads_proxy
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = r.post(create_profile_url, headers=headers, json=payload).json()
        print(response)
        if response['code'] != 0:
            logger.error(f'While openning profile error occured: {response["msg"]}')
            return

        return response['data']['id']
    

def ads_func():
    ads_power = AdsPower(profile_id='knq165t')
    time.sleep(15)
