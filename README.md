# WebEmoji Bot

[🇷🇺 Русский](README-RU.md) | [🇬🇧 English](README.md)

[![Bot Link](https://img.shields.io/badge/Telegram_Bot-Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/webemoji_bot/play?startapp=228618799)
[![Channel Link](https://img.shields.io/badge/Telegram_Channel-Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+x8gutImPtaQyN2Ey)

---

## 📑 Table of Contents
1. [Description](#description)
2. [Key Features](#key-features)
3. [Installation](#installation)
   - [Quick Start](#quick-start)
   - [Manual Installation](#manual-installation)
4. [Settings](#settings)
5. [Support and Donations](#support-and-donations)
6. [Contact](#contact)

---

## 📜 Description
**WebEmoji Bot** is an automated bot for the WebEmoji game. Supports multithreading, proxy integration, and automatic game management.

---

## 🌟 Key Features
- 🔄 **Multithreading** — ability to work with multiple accounts in parallel
- 🔐 **Proxy Support** — secure operation through proxy servers
- 🎯 **Smart Gaming** — automatic game playing with optimal strategy
- 🎯 **Quest Management** — automatic quest completion
- 🎟️ **Free Tickets** — automatic free tickets claiming
- 📊 **Statistics** — detailed session statistics tracking

---

## 🛠️ Installation

### Quick Start
1. **Download the project:**
   ```bash
   git clone https://github.com/Mffff4/WebEmoji.git
   cd WebEmoji
   ```

2. **Install dependencies:**
   - **Windows**:
     ```bash
     run.bat
     ```
   - **Linux**:
     ```bash
     run.sh
     ```

3. **Get API keys:**
   - Go to [my.telegram.org](https://my.telegram.org) and get your `API_ID` and `API_HASH`
   - Add this information to the `.env` file

4. **Run the bot:**
   ```bash
   python3 main.py --action 3  # Run the bot
   ```

### Manual Installation
1. **Linux:**
   ```bash
   sudo sh install.sh
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   cp .env-example .env
   nano .env  # Add your API_ID and API_HASH
   python3 main.py
   ```

2. **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env-example .env
   python main.py
   ```

---

## ⚙️ Settings


| Parameter                  | Default Value         | Description                                                 |
|---------------------------|----------------------|---------------------------------------------------------------|
| **API_ID**                |                      | Telegram API application ID                                   |
| **API_HASH**              |                      | Telegram API application hash                                 |
|   **GLOBAL_CONFIG_PATH**    |                      | Defines the global path for accounts_config, proxies, sessions. <br/>Specify the absolute path or use the environment variable (default - environment variable: **TG_FARM**)<br/> If the environment variable does not exist, it uses the script directory |
|        **FIX_CERT**         | False                | Try to fix SSLCertVerificationError ( True / **False** ) |
| **REF_ID**                |             | Referral ID for new accounts                                 |
| **USE_PROXY**             | False                 | Enable proxy usage                                           |
| **SESSIONS_PER_PROXY**    | 1                    | Number of sessions per proxy                                 |
| **DISABLE_PROXY_REPLACE** | False                | Disable proxy replacement on failure                         |
| **SESSION_START_DELAY**   | 360                  | Delay before session start (sec)                             |
| **ENABLE_GAMES**          | True                 | Enable game playing                                          |
| **DISABLED_GAMES_SESSIONS** | "session1,session2"   | Disable games in sessions (comma separated)                    |
| **MAX_GAMES_PER_SESSION** | 0                    | Maximum games per session (0 = unlimited)                    |
| **BLACKLISTED_SESSIONS** | ""                   | Sessions that will not be used (comma separated)             |
| **DEBUG_LOGGING**         | False                | Enable debug logging                                         |
| **DEVICE_PARAMS**         | False                | Enable custom device parameters                              |


---

## 💰 Support and Donations

Support development using cryptocurrencies:

| Currency              | Wallet Address                                                                     |
|----------------------|------------------------------------------------------------------------------------|
| Bitcoin (BTC)        |bc1qt84nyhuzcnkh2qpva93jdqa20hp49edcl94nf6| 
| Ethereum (ETH)       |0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| TON                  |UQBlvCgM84ijBQn0-PVP3On0fFVWds5SOHilxbe33EDQgryz|
| Binance Coin         |0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Solana (SOL)         |3vVxkGKasJWCgoamdJiRPy6is4di72xR98CDj2UdS1BE| 
| Ripple (XRP)         |rPJzfBcU6B8SYU5M8h36zuPcLCgRcpKNB4| 
| Dogecoin (DOGE)      |DST5W1c4FFzHVhruVsa2zE6jh5dznLDkmW| 
| Polkadot (DOT)       |1US84xhUghAhrMtw2bcZh9CXN3i7T1VJB2Gdjy9hNjR3K71| 
| Litecoin (LTC)       |ltc1qcg8qesg8j4wvk9m7e74pm7aanl34y7q9rutvwu| 
| Matic                |0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Tron (TRX)           |TQkDWCjchCLhNsGwr4YocUHEeezsB4jVo5| 

---

## 📞 Contact

If you have questions or suggestions:
- **Telegram**: [Join our channel](https://t.me/+x8gutImPtaQyN2Ey)

---

## ⚠️ Disclaimer

This software is provided "as is" without any warranties. By using this bot, you accept full responsibility for its use and any consequences that may arise.

The author is not responsible for:
- Any direct or indirect damages related to the use of the bot
- Possible violations of third-party service terms of use
- Account blocking or access restrictions

Use the bot at your own risk and in compliance with applicable laws and third-party service terms of use.

