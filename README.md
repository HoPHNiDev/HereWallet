<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://tgapp.herewallet.app/images/Dragon_intro.png" alt="Project logo"></a>
</p>

<h3 align="center">Here Wallet Automation</h3>

<p align="center"> Here Wallet automation Script using Selenium
    <br> 
</p>

> [!CAUTION]
> Not relevant now, because Here Wallet's missions have been closed/ended and automation protection system has been updated.

## 📝 Table of Contents

- [Features](#features)
- [Settings](#settings)
- [Getting Started](#getting_started)
- [Built Using](#built_using)
- [Authors](#authors)

## ✨ Features <a name = "features"></a> 
|Feature|Supported|
|:-----:|:-------:|
|Multithreading|✅|
|Proxy binding to session|✅|
|Funds Auto Transfer|✅|
|Automatic joining to squad|✅|
|Automatic joining via your ref_code|✅|
|Automatic creating wallets|✅|
|AutoTasks|✅|
|Automated HOT Claiming|✅|
|Boosters Autobuy|✅|
|Auto Bridge|✅|
|Auto Swap|✅|
|Posibility to use ADBs|✅|
|Saving all data on sqlite3 db file|✅|
|Support for pyrogram .session|✅|

## ⚙️ [Settings](https://github.com/HoPHNiDev/HereWallet/blob/main/.env-example/) <a name = "settings"></a>
|Settings|Description|
|:------:|:---------:|
|**API_ID**|Platform data from which to run the Telegram session (default - android)|
|**API_HASH**|Platform data from which to run the Telegram session (default - android)|
|**BOT_TOKEN**|Bot Token from @BotFather for error notifications|
|**RECEIVER_ID**|Error notifications receiver ID|
|**MAIN_URL**|URL for herewallet's website for transfer account with external data which provides telegram when we open the app|
|**MAIN_SEED_PHRASE**|Seed phrase of transfer account|
|**MAIN_USERNAME**|Username of Transfer account for logging|
|**MAIN_REF_CODE**|Ref code of main account|
|**MAIN_PROXY**|Proxy for transfer account|
|**HOT_ADDRESS**|Hot address for moneyback|
|**SOLANA_ADDRESS**|Solana address for moneyback|
|**TON_ADDRESS**|TON address for moneyback|
|**ETH_ADDRESS**|ETH address for moneyback|
|**BNB_ADDRESS**|BNB address for moneyback|
|**NEAR_ADDRESS**|NEAR address for moneyback|
|**TRON_ADDRESS**|TRON address for moneyback|
|**DOLPHIN_API_KEY**|DOLPHIN's API KEY|
|**ADS_API_KEY**|AdsPower's API KEY|


## 🏁 Getting Started <a name = "getting_started"></a>

To quickly install the required libraries and run the bot:

1. Open `run.bat` on Windows or `run.sh` on Linux.

### Prerequisites

Make sure you have Python **3.11** installed.  
Download Python [here](https://www.python.org/downloads/).

### Obtaining API Keys

1. Visit [my.telegram.org](https://my.telegram.org) and log in with your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Note down your **API_ID** and **API_HASH** from the site and add them to the `.env` file.

---

### Installing

You can download the [**repository**](https://github.com/HoPHNiDev/HereWallet) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/HoPHNiDev/HereWallet.git
cd HereWallet
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# <img src="https://upload.wikimedia.org/wikipedia/commons/3/35/Tux.svg" alt="Tux" width="21" /> Linux manual installation
```shell
sudo sh install.sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default

python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/HereWallet >>> python3 main.py --action (1/2)
# Or
~/HereWallet >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Add/create a session files
# 3 - Add/create a session files from json
```

# <img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Windows_logo_-_2012.svg" alt="Windows Logo" width="25" /> Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default

python main.py
```

You can also use arguments for quick start, for example:
```shell
~/HereWallet >>> python main.py --action (1/2)
# Or
~/HereWallet >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Add/create a session files
# 3 - Add/create a session files from json
```

## ⛏️ Built Using <a name = "built_using"></a>

- [Python](https://www.python.com/) - Programming language
- [Selenium](https://selenium.dev/) - Web Automation Tool
- [Pyrogram](https://pyrogram.org/) - Asynchronous MTProto Telegram API framework
- [Dolphin](https://dolphin-anty.com/en/) - Anti Detect Browser
- [AdsPower](https://www.adspower.com/) - Anti Detect Browser

## ✍️ Authors <a name = "authors"></a>

- [@HoPHNiDev](https://github.com/HoPHNiDev) - Idea & Initial work
