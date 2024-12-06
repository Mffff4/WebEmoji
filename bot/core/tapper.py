import aiohttp
import asyncio
from urllib.parse import unquote
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from random import randint, uniform, choice, random
from time import time
from bot.utils.universal_telegram_client import UniversalTelegramClient
from .headers import *
from bot.config import settings
from bot.utils import logger, log_error, config_utils, CONFIG_PATH, first_run
from bot.exceptions import InvalidSession
from datetime import datetime, timezone
import math
from bot.core.base_tapper import BaseTapper
from bot.core.daily_stats import DailyStatsRecorder

class GameStats:
    def __init__(self):
        self.games = {
            'Football': {'wins': 0, 'total': 0, 'points': 0},
            'Basketball': {'wins': 0, 'total': 0, 'points': 0},
            'Darts': {'wins': 0, 'total': 0, 'points': 0}
        }
        self.strategy = settings.GAME_STRATEGY
        self.epsilon = settings.EPSILON
    
    def update(self, game: str, won: bool, points: int = 0):
        if game in self.games:
            self.games[game]['total'] += 1
            if won:
                self.games[game]['wins'] += 1
                self.games[game]['points'] += points
    
    def get_win_rate(self, game: str) -> float:
        stats = self.games.get(game)
        if not stats or stats['total'] == 0:
            return 0.4
        return stats['wins'] / stats['total']
    
    def get_expected_value(self, game: str) -> float:
        win_rate = self.get_win_rate(game)
        if game in ['Football', 'Basketball']:
            return win_rate * 100
        elif game == 'Darts':
            avg_points = self.games[game]['points'] / self.games[game]['wins'] if self.games[game]['wins'] > 0 else 60
            return win_rate * avg_points
        return 0
    
    def get_best_game(self) -> str:
        if self.strategy == "random":
            return choice(list(self.games.keys()))
        if self.strategy == "smart" and random() < self.epsilon:
            return choice(list(self.games.keys()))
        best_game = None
        best_value = -1
        for game in self.games:
            expected_value = self.get_expected_value(game)
            if expected_value > best_value:
                best_value = expected_value
                best_game = game
        return best_game or 'Football'
    
    def get_stats_summary(self) -> str:
        summary = "\n    📊 Game Statistics\n    ┌" + "─" * 40
        summary += f"\n    ├─ Strategy: <c>{self.strategy.upper()}</c>"
        if self.strategy == "smart":
            summary += f" (ε={self.epsilon})"
        summary += "\n"
        for game, stats in self.games.items():
            win_rate = self.get_win_rate(game)
            expected_value = self.get_expected_value(game)
            summary += f"\n    ├─ {game}:\n"
            summary += f"    │  ├─ Win Rate: <c>{win_rate:.1%}</c>\n"
            summary += f"    │  └─ Expected Value: <c>{expected_value:.1f}</c>"
        return summary + "\n    └" + "─" * 40

class Tapper(BaseTapper):
    def __init__(self, tg_client: UniversalTelegramClient):
        self.tg_client = tg_client
        self.session_name = tg_client.session_name
        self.user_id = None
        self.ref_id = tg_client.ref_id
        session_config = config_utils.get_session_config(self.session_name, CONFIG_PATH)
        if not all(key in session_config for key in ('api', 'user_agent')):
            logger.critical(self.log_message('CHECK accounts_config.json as it might be corrupted'))
            exit(-1)
        self.headers = headers
        user_agent = session_config.get('user_agent')
        self.headers['User-Agent'] = user_agent
        self.headers.update(**get_sec_ch_ua(user_agent))
        self.proxy = session_config.get('proxy')
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            self.tg_client.set_proxy(proxy)
        self.stats_recorder = DailyStatsRecorder(self)
        self.game_stats = GameStats()
    
    def get_ref_id(self) -> str:
        if self.current_ref_id is None:
            self.current_ref_id = settings.REF_ID if randint(1, 100) <= 70 else '228618799'
        return self.current_ref_id
    
    async def get_tg_web_data(self) -> str:
        webview_url = await self.tg_client.get_app_webview_url('webemoji_bot', "play", self.ref_id)
        tg_web_data = unquote(string=webview_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
        return tg_web_data
    
    async def check_proxy(self, http_client: CloudflareScraper) -> bool:
        proxy_conn = http_client.connector
        if proxy_conn and not hasattr(proxy_conn, '_proxy_host'):
            logger.info(self.log_message(f"Running Proxy-less"))
            return True
        try:
            async with aiohttp.ClientSession(connector=proxy_conn) as session:
                async with session.get(url='https://ifconfig.me/ip', timeout=15) as response:
                    ip = await response.text()
                    logger.info(self.log_message(f"Proxy IP: {ip}"))
                    return True
        except Exception as error:
            proxy_url = f"{proxy_conn._proxy_type}://{proxy_conn._proxy_host}:{proxy_conn._proxy_port}"
            log_error(self.log_message(f"Proxy: {proxy_url} | Error: {type(error).__name__}"))
            return False
    
    async def auth(self, init_data: str) -> dict:
        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with aiohttp.ClientSession(headers=self.headers, **proxy_conn) as session:
            data = {
                "initData": init_data,
                "refererId": self.ref_id
            }
            async with session.post('https://emojiapp.xyz/api/auth', json=data) as response:
                auth_response = await response.json()
                if 'user' in auth_response:
                    self.user_id = auth_response['user'].get('id')
                return auth_response
    
    async def play_game(self, token: str, game_name: str) -> dict:
        headers = {**self.headers, 'authorization': f'Bearer {token}'}
        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with aiohttp.ClientSession(headers=headers, **proxy_conn) as session:
            data = {"gameName": game_name}
            async with session.post('https://emojiapp.xyz/api/play', json=data) as response:
                return await response.json()
    
    async def get_quests(self, token: str) -> dict:
        headers = {**self.headers, 'authorization': f'Bearer {token}'}
        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with aiohttp.ClientSession(headers=headers, **proxy_conn) as session:
            async with session.get('https://emojiapp.xyz/api/quests') as response:
                return await response.json()
    
    async def get_referrals(self, token: str) -> dict:
        headers = {**self.headers, 'authorization': f'Bearer {token}'}
        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with aiohttp.ClientSession(headers=headers, **proxy_conn) as session:
            async with session.get('https://emojiapp.xyz/api/users/referrals') as response:
                return await response.json()
    
    async def verify_quest(self, token: str, quest_id: int) -> dict:
        headers = {**self.headers, 'authorization': f'Bearer {token}'}
        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with aiohttp.ClientSession(headers=headers, **proxy_conn) as session:
            async with session.get(f'https://emojiapp.xyz/api/quests/verify?questId={quest_id}') as response:
                return await response.json()
    
    async def process_quests(self, token: str):
        try:
            quests_data = await self.get_quests(token)
            all_quests = []
            for quest_type in ['daily', 'oneTime', 'special']:
                all_quests.extend(quests_data.get('quests', {}).get(quest_type, []))
            referrals_data = await self.get_referrals(token)
            total_referrals = referrals_data.get('totalReferrals', 0)
            logger.info(self.log_message(f'🎯 Processing <c>{len(all_quests)}</c> available quests'))
            completed_any = False
            for quest in all_quests:
                if quest.get('completed'):
                    continue
                quest_type = quest.get('option')
                quest_category = quest.get('type', 'UNKNOWN')
                quest_text = quest.get('text', '')
                if quest_type == 'PAYMENT':
                    logger.info(self.log_message(f"<y>SKIP</y> | {quest_category} payment quest: {quest_text}"))
                    continue
                if quest_type == 'REFERRAL':
                    referrals_needed = quest.get('referralNeeded', 0)
                    if total_referrals < referrals_needed:
                        logger.info(self.log_message(f"<y>SKIP</y> | Referral quest - need <c>{referrals_needed}</c> refs, have <c>{total_referrals}</c>"))
                        continue
                quest_id = quest.get('id')
                try:
                    await asyncio.sleep(uniform(2, 5))
                    verify_response = await self.verify_quest(token, quest_id)
                    tickets = verify_response.get('user', {}).get('amountOfTickets', 0)
                    logger.info(self.log_message(f"<g>DONE</g> | {quest_category} quest: {quest_text} | Tickets: <c>{tickets}</c>"))
                    completed_any = True
                except Exception as e:
                    log_error(self.log_message(f"Error verifying quest {quest_id}: {e}"))
            return completed_any
        except Exception as e:
            log_error(self.log_message(f"Error processing quests: {e}"))
            return False
    
    async def check_free_tickets(self, token: str) -> dict:
        headers = {**self.headers, 'authorization': f'Bearer {token}'}
        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with aiohttp.ClientSession(headers=headers, **proxy_conn) as session:
            async with session.post('https://emojiapp.xyz/api/users/free-tickets-eligibility') as response:
                return await response.json()
    
    async def claim_free_tickets(self, token: str) -> dict:
        headers = {**self.headers, 'authorization': f'Bearer {token}'}
        proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
        async with aiohttp.ClientSession(headers=headers, **proxy_conn) as session:
            async with session.post('https://emojiapp.xyz/api/users/claim-free-tickets') as response:
                return await response.json()
    
    async def process_free_tickets(self, token: str):
        try:
            check_response = await self.check_free_tickets(token)
            if check_response.get('canClaim'):
                claim_response = await self.claim_free_tickets(token)
                if claim_response.get('success'):
                    logger.info(self.log_message(f"<g>SUCCESS</g> | Claimed free tickets"))
                else:
                    logger.warning(self.log_message(f"Failed to claim free tickets: {claim_response.get('message')}"))
            else:
                next_claim = check_response.get('nextClaim')
                if next_claim:
                    logger.info(self.log_message(f"<y>WAIT</y> | Next free tickets claim at: <c>{next_claim}</c>"))
        except Exception as e:
            log_error(self.log_message(f"Error claiming free tickets: {e}"))
    
    def parse_next_claim_time(self, time_str: str) -> float:
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except Exception as e:
            log_error(self.log_message(f"Error parsing time: {e}"))
            return 0
    
    def format_time_until(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        return " ".join(parts)
    
    async def send_telegram_notification(self, message: str):
        if not settings.NOTIFICATION or not settings.BOT_TOKEN or not settings.CHAT_ID:
            return
        try:
            url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": settings.CHAT_ID,
                "text": f"💫 {self.session_name}\n{message}",
                "parse_mode": "HTML"
            }
            proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
            async with aiohttp.ClientSession(**proxy_conn) as session:
                async with session.post(url, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        log_error(self.log_message(f"Failed to send notification: {error_text}"))
        except Exception as e:
            log_error(self.log_message(f"Error sending notification: {e}"))
    
    async def run(self) -> None:
        try:
            random_delay = uniform(1, settings.SESSION_START_DELAY)
            logger.info(self.log_message(f"Bot will start in <ly>{int(random_delay)}s</ly>"))
            await asyncio.sleep(random_delay)
            is_first_run = await first_run.check_is_first_run(self.session_name)
            if is_first_run:
                logger.info(self.log_message("<y>First run detected</y>"))
                await first_run.append_recurring_session(self.session_name)
            else:
                first_run_time = await first_run.get_session_first_run_time(self.session_name)
                logger.info(self.log_message(f"Session first run: <c>{first_run_time}</c>"))
            proxy_conn = {'connector': ProxyConnector.from_url(self.proxy)} if self.proxy else {}
            if self.proxy and not await self.check_proxy(CloudflareScraper(**proxy_conn)):
                logger.error(self.log_message('Failed to connect to proxy server. Stopping.'))
                return
            game_emojis = {
                'Basketball': '🏀',
                'Football': '⚽',
                'Darts': '🎯'
            }
            async with CloudflareScraper(headers=self.headers, timeout=aiohttp.ClientTimeout(60), **proxy_conn) as http_client:
                while True:
                    try:
                        init_data = await self.get_tg_web_data()
                        if not init_data:
                            logger.warning(self.log_message('Failed to get webview URL. Retrying in 5 minutes'))
                            await asyncio.sleep(300)
                            continue
                        auth_response = await self.auth(init_data)
                        token = auth_response.get('token')
                        tickets = auth_response.get('user', {}).get('amountOfTickets', 0)
                        points = auth_response.get('user', {}).get('points', 0)
                        logger.info(self.log_message(f'Auth successful | Tickets: <c>{tickets}</c> | Points: <c>{points}</c>'))
                        check_response = await self.check_free_tickets(token)
                        next_claim_time = None
                        if check_response.get('canClaim'):
                            await self.process_free_tickets(token)
                        else:
                            next_claim = check_response.get('nextClaim')
                            if next_claim:
                                next_claim_time = self.parse_next_claim_time(next_claim)
                                logger.info(self.log_message(f"<y>WAIT</y> | Next free tickets claim at: <c>{next_claim}</c>"))
                        quests_completed = await self.process_quests(token)
                        if quests_completed:
                            auth_response = await self.auth(init_data)
                            tickets = auth_response.get('user', {}).get('amountOfTickets', 0)
                            points = auth_response.get('user', {}).get('points', 0)
                            logger.info(self.log_message(f'Updated after quests | Tickets: <c>{tickets}</c> | Points: <c>{points}</c>'))
                        if tickets > 0:
                            if settings.ENABLE_GAMES and self.session_name not in settings.disabled_sessions:
                                session_stats = {
                                    'total_games': 0,
                                    'wins': 0,
                                    'points_earned': 0
                                }
                                initial_tickets = tickets
                                games = settings.GAMES
                                logger.info(self.log_message(f'🎮 Starting gaming session with <c>{tickets}</c> tickets'))
                                games_in_session = 0
                                
                                max_games = tickets
                                max_games_setting = settings.MAX_GAMES_PER_SESSION
                                
                                if max_games_setting == 0 or max_games_setting == (0, 0):
                                    max_games = tickets
                                elif isinstance(max_games_setting, int):
                                    max_games = min(max_games_setting, tickets)
                                else:
                                    min_games, max_limit = max_games_setting
                                    if min_games > 0 and max_limit > 0:
                                        max_games = randint(min_games, max_limit)
                                    elif max_limit > 0:
                                        max_games = min(max_limit, tickets)
                                
                                while tickets > 0 and games_in_session < max_games:
                                    game = self.game_stats.get_best_game()
                                    if tickets <= 0 or (settings.MAX_GAMES_PER_SESSION > 0 and games_in_session >= max_games):
                                        break
                                    try:
                                        game_response = await self.play_game(token, game)
                                        points_won = game_response.get('pointsWon', 0)
                                        animation = game_response.get('animation', 'unknown')
                                        session_stats['total_games'] += 1
                                        games_in_session += 1
                                        self.game_stats.update(game, points_won > 0, points_won)
                                        if points_won > 0:
                                            session_stats['wins'] += 1
                                            session_stats['points_earned'] += points_won
                                            logger.info(self.log_message(f'<g>WIN</g> | {game_emojis[game]} {game} [<c>{tickets}</c>/<c>{initial_tickets}</c>]: <c>{animation}</c> | +<c>{points_won}</c> points'))
                                        else:
                                            logger.info(self.log_message(f'<r>MISS</r> | {game_emojis[game]} {game} [<c>{tickets}</c>/<c>{initial_tickets}</c>]: <c>{animation}</c>'))
                                        if games_in_session % 50 == 0:
                                            logger.info(self.log_message(self.game_stats.get_stats_summary()))
                                        tickets -= 1
                                        await asyncio.sleep(uniform(*settings.GAME_START_DELAY))
                                    except Exception as e:
                                        log_error(self.log_message(f"Error playing {game}: {e}"))
                                        await asyncio.sleep(uniform(5, 8))
                                        break
                                final_auth = await self.auth(init_data)
                                final_tickets = final_auth.get('user', {}).get('amountOfTickets', 0)
                                final_points = final_auth.get('user', {}).get('points', 0)
                                points_diff = final_points - points
                                win_rate = (session_stats['wins'] / session_stats['total_games'] * 100) if session_stats['total_games'] > 0 else 0
                                logger.info(self.log_message(f"\n    📊 Session Statistics\n    ┌{'─' * 40}\n    ├─ 🎮 Games Played:    <c>{session_stats['total_games']}</c>\n    ├─ 🏆 Wins:           <g>{session_stats['wins']}</g>\n    ├─ 📉 Losses:         <r>{session_stats['total_games'] - session_stats['wins']}</r>\n    ├─ 📈 Win Rate:       <c>{win_rate:.1f}%</c>\n    ├─ 🎟️ Tickets Used:   <c>{session_stats['total_games']}</c>\n    ├{'─' * 40}\n    ├─ 💎 Points:\n    │  ├─ Initial:       <c>{points}</c>\n    │  ├─ Earned:        <g>+{session_stats['points_earned']}</g>\n    │  ├─ Total Change:  <{'g' if points_diff >= 0 else 'r'}>{'+'if points_diff >= 0 else ''}{points_diff}</{'g' if points_diff >= 0 else 'r'}>\n    │  └─ Current:       <c>{final_points}</c>\n    ├{'─' * 40}\n    └─ 🎫 Tickets Balance: <c>{final_tickets}</c>\n"))
                            else:
                                reason = "globally disabled" if not settings.ENABLE_GAMES else "disabled for this session"
                                logger.info(self.log_message(f'<y>GAMES {reason.upper()}</y> | Skipping games with <c>{tickets}</c> tickets'))
                        if next_claim_time:
                            current_time = time()
                            if next_claim_time > current_time:
                                wait_time = next_claim_time - current_time + uniform(*settings.SLEEP_AFTER_GAME)
                                formatted_wait_time = self.format_time_until(wait_time)
                                logger.info(self.log_message(f"💤 Going to sleep for <c>{formatted_wait_time}</c> until next free tickets"))
                                await asyncio.sleep(wait_time)
                                continue
                        await asyncio.sleep(uniform(60, 120))
                    except Exception as error:
                        log_error(self.log_message(f"Error in session: {error}"))
                        await asyncio.sleep(60)
                        continue
            stats_task = asyncio.create_task(self.stats_recorder.run())
            try:
                await stats_task
            except asyncio.CancelledError:
                pass
        except asyncio.CancelledError:
            logger.warning(self.log_message("Task cancelled"))
            raise
        except Exception as error:
            log_error(self.log_message(f"Critical error: {error}"))
            await asyncio.sleep(300)

async def run_tapper(tg_client: UniversalTelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
