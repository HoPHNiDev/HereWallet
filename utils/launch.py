from utils.logger import logger
import argparse
from auto.auto import automation_threads
from auth.auth import new_account, new_account_from_json

start_text = """
██╗  ██╗███████╗██████╗ ███████╗    ██╗    ██╗ █████╗ ██╗     ██╗     ███████╗████████╗
██║  ██║██╔════╝██╔══██╗██╔════╝    ██║    ██║██╔══██╗██║     ██║     ██╔════╝╚══██╔══╝
███████║█████╗  ██████╔╝█████╗      ██║ █╗ ██║███████║██║     ██║     █████╗     ██║   
██╔══██║██╔══╝  ██╔══██╗██╔══╝      ██║███╗██║██╔══██║██║     ██║     ██╔══╝     ██║   
██║  ██║███████╗██║  ██║███████╗    ╚███╔███╔╝██║  ██║███████╗███████╗███████╗   ██║   
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝     ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝   ╚═╝   

Select an action:

    1. Run automation script
    2. Create/Add a new sessions
    3. Create/Add a new sessions from JSON data file
"""


async def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    action = parser.parse_args().action

    if not action:
        print(start_text)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ["1", "2"]:
                logger.warning("Action must be 1 or 2")
            else:
                action = int(action)
                break

    if action == 1:
        threads_count = int(input("Enter the number of threads:  >... "))
        automation_threads(threads_count)

    elif action == 2:
        file_path = input(
            "Enter the path to the accounts file, leave blank to write data directly: "
        )
        await new_account(file_path)

    elif action == 3:
        await new_account_from_json()
