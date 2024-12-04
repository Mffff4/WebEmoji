import asyncio
from contextlib import suppress
from bot.core.launcher import process
from os import system, name as os_name
import os


def is_docker():
    """Check if we're running in a Docker container"""
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))


def set_window_title(title):
    """ Set console window title cross-platform
    Args:
        title (str): New window title
    """
    if is_docker():
        return
    if os_name == 'nt':
        system(f'title {title}')
    else:
        print(f'\033]0;{title}\007', end='', flush=True)


async def main():
    await process()


if __name__ == '__main__':
    set_window_title('WebEmoji')
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
