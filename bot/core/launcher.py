import glob
import asyncio
import argparse
import os
import subprocess
import signal
from copy import deepcopy
from random import uniform
from colorama import init, Fore, Style

from bot.utils.universal_telegram_client import UniversalTelegramClient
from bot.utils.web import run_web_and_tunnel, stop_web_and_tunnel
from bot.config import settings
from bot.core.agents import generate_random_user_agent
from bot.utils import logger, config_utils, proxy_utils, CONFIG_PATH, SESSIONS_PATH, PROXIES_PATH
from bot.core.tapper import run_tapper
from bot.core.registrator import register_sessions

init()  # Инициализация colorama

# Добавляем глобальные переменные для управления веб-сервером
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    shutdown_event.set()

START_TEXT = f"""
{Fore.RED}ВНИМАНИЕ: Эта ферма не предназначена для продажи!{Style.RESET_ALL}
{Fore.RED}WARNING: This farm is not for sale!{Style.RESET_ALL}
{Fore.RED}¡ADVERTENCIA: ¡Esta granja no está a la venta!{Style.RESET_ALL}
{Fore.RED}ATTENTION: Cette ferme n'est pas à vendre!{Style.RESET_ALL}
{Fore.RED}ACHTUNG: Diese Farm ist nicht zum Verkauf bestimmt!{Style.RESET_ALL}
{Fore.RED}ATTENZIONE: Questa fattoria non è in vendita!{Style.RESET_ALL}
{Fore.RED}注意：この農場は販売用ではありません！{Style.RESET_ALL}
{Fore.RED}주의: 이 농장은 판매용이 아닙니다!{Style.RESET_ALL}
{Fore.RED}注意：此农场不用于销售！{Style.RESET_ALL}
{Fore.RED}ATENÇÃO: Esta fazenda não se destina à venda!{Style.RESET_ALL}


{Fore.LIGHTMAGENTA_EX} 

██╗    ██╗███████╗██████╗ ███████╗███╗   ███╗ ██████╗      ██╗██╗
██║    ██║██╔════╝██╔══██╗██╔════╝████╗ ████║██╔═══██╗     ██║██║
██║ █╗ ██║█████╗  ██████╔╝█████╗  ██╔████╔██║██║   ██║     ██║██║
██║███╗██║██╔══╝  ██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║██   ██║██║
╚███╔███╔╝███████╗██████╔╝███████╗██║ ╚═╝ ██║╚██████╔╝╚█████╔╝██║
 ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═════╝  ╚════╝ ╚═╝
                                                                 

{Style.RESET_ALL}
{Fore.CYAN}Select action:{Style.RESET_ALL}

    {Fore.GREEN}1. Launch clicker{Style.RESET_ALL}
    {Fore.GREEN}2. Create session{Style.RESET_ALL}
    {Fore.GREEN}3. Create session via QR{Style.RESET_ALL}
    {Fore.GREEN}4. Upload sessions via web (BETA){Style.RESET_ALL}

{Fore.CYAN}Developed by: @Mffff4{Style.RESET_ALL}
{Fore.CYAN}Our Telegram channel: {Fore.BLUE}https://t.me/+x8gutImPtaQyN2Ey{Style.RESET_ALL}

"""

API_ID = settings.API_ID
API_HASH = settings.API_HASH


def prompt_user_action() -> int:
    logger.info(START_TEXT)
    while True:
        action = input("> ").strip()
        if action.isdigit() and action in ("1", "2", "3", "4"):
            return int(action)
        logger.warning("Invalid action. Please enter a number between 1 and 4.")


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")
    args = parser.parse_args()

    if not settings.USE_PROXY:
        logger.info(f"Detected {len(get_sessions(SESSIONS_PATH))} sessions | USE_PROXY=False")
    else:
        logger.info(f"Detected {len(get_sessions(SESSIONS_PATH))} sessions | "
                    f"{len(proxy_utils.get_proxies(PROXIES_PATH))} proxies")

    action = args.action or prompt_user_action()

    if action == 1:
        if not API_ID or not API_HASH:
            raise ValueError("API_ID and API_HASH not found in the .env file.")
        await run_tasks()
    elif action == 2:
        await register_sessions()
    elif action == 3:
        session_name = input("Enter the session name for QR code authentication: ")
        print("Initializing QR code authentication...")
        subprocess.run(["python", "-m", "bot.utils.loginQR", "-s", session_name])
        print("QR code authentication was successful!")
    elif action == 4:
        logger.info("Starting web interface for uploading sessions...")
        signal.signal(signal.SIGINT, signal_handler)
        try:
            web_task = asyncio.create_task(run_web_and_tunnel())
            await shutdown_event.wait()
        finally:
            web_task.cancel()
            await stop_web_and_tunnel()
            print("Program terminated.")


def get_sessions(sessions_folder: str) -> list[str]:
    session_names = glob.glob(f"{sessions_folder}/*.session")
    session_names += glob.glob(f"{sessions_folder}/telethon/*.session")
    session_names += glob.glob(f"{sessions_folder}/pyrogram/*.session")
    return [file.replace('.session', '') for file in sorted(session_names)]


async def get_tg_clients() -> list[UniversalTelegramClient]:
    session_paths = get_sessions(SESSIONS_PATH)

    if not session_paths:
        raise FileNotFoundError("Session files not found")
    tg_clients = []
    for session in session_paths:
        session_name = os.path.basename(session)
        
        if session_name in settings.blacklisted_sessions:
            logger.warning(f"{session_name} | Session is blacklisted | Skipping")
            continue
            
        accounts_config = config_utils.read_config_file(CONFIG_PATH)
        session_config: dict = deepcopy(accounts_config.get(session_name, {}))
        if 'api' not in session_config:
            session_config['api'] = {}
        api_config = session_config.get('api', {})
        api = None
        if api_config.get('api_id') in [4, 6, 2040, 10840, 21724]:
            api = config_utils.get_api(api_config)

        if api:
            client_params = {
                "session": session,
                "api": api
            }
        else:
            client_params = {
                "api_id": api_config.get("api_id", API_ID),
                "api_hash": api_config.get("api_hash", API_HASH),
                "session": session,
                "lang_code": api_config.get("lang_code", "en"),
                "system_lang_code": api_config.get("system_lang_code", "en-US")
            }

            for key in ("device_model", "system_version", "app_version"):
                if api_config.get(key):
                    client_params[key] = api_config[key]

        session_config['user_agent'] = session_config.get('user_agent', generate_random_user_agent())
        api_config.update(api_id=client_params.get('api_id') or client_params.get('api').api_id,
                          api_hash=client_params.get('api_hash') or client_params.get('api').api_hash)

        session_proxy = session_config.get('proxy')
        if not session_proxy and 'proxy' in session_config.keys():
            tg_clients.append(UniversalTelegramClient(**client_params))
            if accounts_config.get(session_name) != session_config:
                await config_utils.update_session_config_in_file(session_name, session_config, CONFIG_PATH)
            continue

        else:
            if settings.DISABLE_PROXY_REPLACE:
                proxy = session_proxy or next(iter(proxy_utils.get_unused_proxies(accounts_config, PROXIES_PATH)), None)
            else:
                proxy = await proxy_utils.get_working_proxy(accounts_config, session_proxy) \
                    if session_proxy or settings.USE_PROXY else None

            if not proxy and (settings.USE_PROXY or session_proxy):
                logger.warning(f"{session_name} | Didn't find a working unused proxy for session | Skipping")
                continue
            else:
                tg_clients.append(UniversalTelegramClient(**client_params))
                session_config['proxy'] = proxy
                if accounts_config.get(session_name) != session_config:
                    await config_utils.update_session_config_in_file(session_name, session_config, CONFIG_PATH)

    return tg_clients


async def init_config_file():
    session_paths = get_sessions(SESSIONS_PATH)

    if not session_paths:
        raise FileNotFoundError("Session files not found")
    for session in session_paths:
        session_name = os.path.basename(session)
        parsed_json = config_utils.import_session_json(session)
        if parsed_json:
            accounts_config = config_utils.read_config_file(CONFIG_PATH)
            session_config: dict = deepcopy(accounts_config.get(session_name, {}))
            session_config['user_agent'] = session_config.get('user_agent', generate_random_user_agent())
            session_config['api'] = parsed_json
            if accounts_config.get(session_name) != session_config:
                await config_utils.update_session_config_in_file(session_name, session_config, CONFIG_PATH)


async def run_tasks():
    await config_utils.restructure_config(CONFIG_PATH)
    await init_config_file()
    tg_clients = await get_tg_clients()
    tasks = [asyncio.create_task(run_tapper(tg_client=tg_client)) for tg_client in tg_clients]
    await asyncio.gather(*tasks)
