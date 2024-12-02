import asyncio
import aiofiles
from datetime import datetime, timezone, time
import os
from bot.config import settings
from bot.utils import logger
from bot.core.base_tapper import BaseTapper

class DailyStatsRecorder:
    def __init__(self, tapper: BaseTapper):
        self.tapper = tapper
        self.stats_dir = "daily_stats"
        if not os.path.exists(self.stats_dir):
            os.makedirs(self.stats_dir)

    async def record_stats(self):
        try:
            if self.tapper.session_name not in settings.stats_sessions:
                return

            init_data = await self.tapper.get_tg_web_data()
            auth_response = await self.tapper.auth(init_data)
            
            if not auth_response:
                return
                
            tickets = auth_response.get('user', {}).get('amountOfTickets', 0)
            points = auth_response.get('user', {}).get('points', 0)
            
            current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            filename = os.path.join(self.stats_dir, f"{self.tapper.session_name}_stats.txt")
            
            async with aiofiles.open(filename, mode='a+') as file:
                await file.write(f"{current_date},{tickets},{points}\n")
                
            logger.info(self.tapper.log_message(
                f"📊 Daily stats recorded | Tickets: <c>{tickets}</c> | Points: <c>{points}</c>"
            ))

        except Exception as e:
            logger.error(self.tapper.log_message(f"Error recording daily stats: {e}"))

    async def run(self):
        while True:
            try:
                now = datetime.now(timezone.utc)
                target = datetime.combine(now.date(), time(23, 59), tzinfo=timezone.utc)
                
                if now >= target:
                    target = datetime.combine(now.date(), time(23, 59), tzinfo=timezone.utc)
                    target = target.replace(day=target.day + 1)
                
                wait_seconds = (target - now).total_seconds()
                await asyncio.sleep(wait_seconds)
                
                await self.record_stats()
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(self.tapper.log_message(f"Error in daily stats recorder: {e}"))
                await asyncio.sleep(60) 