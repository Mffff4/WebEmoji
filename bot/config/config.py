from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = None
    API_HASH: str = None
    GLOBAL_CONFIG_PATH: str = "TG_FARM"

    FIX_CERT: bool = False

    SESSION_START_DELAY: int = 360

    REF_ID: str = '228618799'

    SESSIONS_PER_PROXY: int = 1
    USE_PROXY: bool = False
    DISABLE_PROXY_REPLACE: bool = False

    NOTIFICATION: bool = False
    BOT_TOKEN: Optional[str] = None
    CHAT_ID: Optional[int] = None

    DEVICE_PARAMS: bool = False

    DEBUG_LOGGING: bool = False

    ENABLE_GAMES: bool = True
    MAX_GAMES_PER_SESSION: int = 0
    DISABLED_GAMES_SESSIONS: str = ""

    DAILY_STATS_SESSIONS: str = ""
    BLACKLISTED_SESSIONS: str = ""

    @property
    def disabled_sessions(self) -> List[str]:
        if not self.DISABLED_GAMES_SESSIONS:
            return []
        return [x.strip() for x in self.DISABLED_GAMES_SESSIONS.split(',')]

    @property
    def blacklisted_sessions(self) -> List[str]:
        if not self.BLACKLISTED_SESSIONS:
            return []
        return [x.strip() for x in self.BLACKLISTED_SESSIONS.split(',')]

    @property
    def stats_sessions(self) -> List[str]:
        if not self.DAILY_STATS_SESSIONS:
            return []
        return [x.strip() for x in self.DAILY_STATS_SESSIONS.split(',')]

    GAMES: List[str] = ['Basketball', 'Football', 'Darts']

    PRIZE_LIST: dict[str, int] = {
        "1-3": 500,
        "4-6": 100,
        "7-15": 50,
        "16-30": 25,
        "31-100": 15,
    }

settings = Settings()
