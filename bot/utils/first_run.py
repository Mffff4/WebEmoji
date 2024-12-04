import aiofiles
import os
from datetime import datetime, timezone

async def check_is_first_run(session_name: str) -> bool:
    try:
        if not os.path.exists('first_run.txt'):
            return True
            
        async with aiofiles.open('first_run.txt', mode='r') as file:
            content = await file.read()
            sessions = [line.strip().split(',')[0] for line in content.splitlines() if line.strip()]
            return session_name.lower() not in sessions
    except Exception:
        return True

async def append_recurring_session(session_name: str):
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    async with aiofiles.open('first_run.txt', mode='a+') as file:
        await file.write(f"{session_name.lower()},{current_time}\n")

async def get_session_first_run_time(session_name: str) -> str:
    try:
        async with aiofiles.open('first_run.txt', mode='r') as file:
            content = await file.read()
            for line in content.splitlines():
                if line.strip():
                    session, timestamp = line.split(',')
                    if session.lower() == session_name.lower():
                        return timestamp
    except Exception:
        pass
    return "Unknown"
