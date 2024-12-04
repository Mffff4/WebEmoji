import os
import sys
import asyncio
import aiohttp
import subprocess
from typing import Optional
from bot.utils import logger
from bot.config import settings

class UpdateManager:
    def __init__(self):
        self.repo_url = f"https://api.github.com/repos/{settings.GITHUB_REPO}"
        self.branch = "main"
        self.current_commit = self._get_current_commit()
        self.check_interval = settings.CHECK_UPDATE_INTERVAL
        self.is_update_restart = "--update-restart" in sys.argv
        self._configure_git_safe_directory()

    def _configure_git_safe_directory(self) -> None:
        try:
            current_dir = os.getcwd()
            subprocess.run(
                ["git", "config", "--global", "--add", "safe.directory", current_dir],
                check=True,
                capture_output=True
            )
            logger.info("Git safe.directory configured successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to configure git safe.directory: {e}")

    def _get_current_commit(self) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""

    async def _get_latest_commit(self) -> Optional[str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.repo_url}/commits/{self.branch}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["sha"]
        except Exception as e:
            logger.error(f"Error getting latest commit: {e}")
        return None

    async def check_for_updates(self) -> bool:
        latest_commit = await self._get_latest_commit()
        if not latest_commit:
            return False
        return latest_commit != self.current_commit

    def _pull_updates(self) -> bool:
        try:
            self._configure_git_safe_directory()
            subprocess.run(["git", "pull"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error updating: {e}")
            if e.stderr:
                logger.error(f"Git error details: {e.stderr.decode()}")
            return False

    def _install_requirements(self) -> bool:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing dependencies: {e}")
            return False

    async def update_and_restart(self) -> None:
        logger.info("🔄 Update detected! Starting update process...")
        
        if not self._pull_updates():
            logger.error("❌ Failed to pull updates")
            return

        if not self._install_requirements():
            logger.error("❌ Failed to update dependencies")
            return

        logger.info("✅ Update successfully installed! Restarting application...")
        
        new_args = [sys.executable, sys.argv[0], "-a", "1", "--update-restart"]
        os.execv(sys.executable, new_args)

    async def run(self) -> None:
        if not self.is_update_restart:
            await asyncio.sleep(10)
        
        while True:
            try:
                if await self.check_for_updates():
                    await self.update_and_restart()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error during update check: {e}")
                await asyncio.sleep(60)