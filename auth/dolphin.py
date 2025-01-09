import random, time
from utils.logger import logger
from config.config import Config
from pyanty import DolphinAPI, STABLE_CHROME_VERSION
import pyanty as dolphin
from pprint import pprint
from threading import Lock

lock = Lock()


class Dolphin(DolphinAPI):
    def new_profile(self, user_id: str, proxy: str = None):
        profiles = self.get_profiles()
        if len(profiles["data"]) == 20:
            deleted = self.delete_done_profile(profiles)
            if not deleted:
                return

        fingerprint = []
        while not fingerprint:
            fingerprint = self.generate_fingerprint(
                platform="windows",
                browser_version=f"{random.randint(114, STABLE_CHROME_VERSION)}",
            )
        # pprint(fingerprint)
        data = self.fingerprint_to_profile(name=str(user_id), fingerprint=fingerprint)
        data.update({"tags": ["NEW"]})
        if proxy:
            proxy_data = proxy.split(":")
            if len(proxy_data) != 4:
                return ValueError("Invalid proxy")
            data.update(
                {
                    "proxy": {
                        "name": f"socks5://{proxy_data[0]}:{proxy_data[1]}",
                        "host": proxy_data[0],
                        "port": proxy_data[1],
                        "type": "socks5",
                        "login": proxy_data[2],
                        "password": proxy_data[3],
                    }
                }
            )
        # host:port:login:pass
        response = self.create_profile(data)
        if not response["success"]:
            logger.error(response["error"]["text"])
            return
        profile_id = response["browserProfileId"]
        return profile_id

    def get_port(self, profile_id):
        logger.debug("GETTING PORT")
        response = ""
        for i in range(10):
            response = dolphin.run_profile(profile_id)
            if "automation" not in response:
                pprint(response)
                time.sleep(10)
            else:
                break
        port = response["automation"]["port"]
        logger.debug(f"PORT is {port}")
        return port

    def delete_done_profile(self, response):
        if response["data"]:
            done_profiles = self.get_all_done_profiles(response["data"])
            profile_id = done_profiles[-1]["id"]
            if profile_id:
                self.delete_profiles([profile_id])

    def get_all_done_profiles(self, profiles):
        done_profiles = []
        for profile in profiles:
            print(profile["tags"])
            if "DONE" in profile["tags"] or "superwhale" in profile["tags"]:
                done_profiles.append(profile)
        return done_profiles

    def get_transfer_profile(self):
        with lock:
            profiles = self.get_profiles()["data"]
            for profile in profiles:
                profile_runned = "running" in profile.keys() and profile["running"]
                if "TRANSFER" in profile["tags"] and not profile_runned:
                    return profile["id"]
            else:
                return None

    def close_profile(self, profile_id):
        dolphin.close_profile(profile_id)


def get_port(): ...


def test():
    dolphin = Dolphin(Config.dolphin_api_key)
    # profiles = dolphin.get_profiles()
    # pprint(profiles['data'][0])
    # print(profiles['data'][0].keys())
    # print('running' in profiles['data'][0].keys())
    # profile_id = dolphin.new_profile('test')
    # port = dolphin.get_port(profile_id)
    # dolphin.get_profiles()
    # dolphin.create_proxy(type='socks5', host='147.45.53.101', port=9043, login='g8LNGR', password='B6Dd5D', name='head')
