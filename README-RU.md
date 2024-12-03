# WebEmoji Bot

[🇷🇺 Русский](README-RU.md) | [🇬🇧 English](README.md)

[![Bot Link](https://img.shields.io/badge/Telegram_Бот-Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/webemoji_bot/play?startapp=228618799)
[![Channel Link](https://img.shields.io/badge/Telegram_Канал-Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+x8gutImPtaQyN2Ey)

---

## 📑 Оглавление
1. [Описание](#описание)
2. [Ключевые особенности](#ключевые-особенности)
3. [Установка](#установка)
   - [Быстрый старт](#быстрый-старт)
   - [Ручная установка](#ручная-установка)
4. [Настройки](#настройки)
5. [Поддержка и донаты](#поддержка-и-донаты)
6. [Контакты](#контакты)

---

## 📜 Описание
**WebEmoji Bot** - автоматизированный бот для игры WebEmoji. Поддерживает многопоточность, работу через прокси и автоматическое управление игрой.

---

## 🌟 Ключевые особенности
- 🔄 **Многопоточность** — возможность работы с несколькими аккаунтами параллельно
- 🔐 **Поддержка прокси** — безопасная работа через прокси-серверы
- 🎮 **Умная игра** — автоматическая игра с оптимальной стратегией
- 🎯 **Управление квестами** — автоматическое выполнение квестов
- 🎟️ **Бесплатные билеты** — автоматическое получение бесплатных билетов
- 📊 **Статистика** — отслеживание подробной статистики сессий

---

## 🛠️ Установка

### Быстрый старт
1. **Скачайте проект:**
   ```bash
   git clone https://github.com/Mffff4/WebEmoji.git
   cd WebEmoji
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте параметры в файле `.env`:**
   ```bash
   API_ID=ваш_api_id
   API_HASH=ваш_api_hash
   ```

### Ручная установка
1. **Linux:**
   ```bash
   sudo sh install.sh
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   cp .env-example .env
   nano .env  # Укажите свои API_ID и API_HASH
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

## ⚙️ Настройки

| Параметр                   | Значение по умолчанию | Описание                                                    |
|---------------------------|----------------------|-------------------------------------------------------------|
| **API_ID**                |                      | ID приложения Telegram API                                   |
| **API_HASH**              |                      | Хеш приложения Telegram API                                  |
|   **GLOBAL_CONFIG_PATH**    | Определяет глобальный путь для accounts_config, proxies, sessions. <br/>Укажите абсолютный путь или используйте переменную окружения (по умолчанию - переменная окружения: **TG_FARM**)<br/> Если переменной окружения не существует, использует директорию скрипта |
|        **FIX_CERT**         |                                                                                              Попытаться исправить ошибку SSLCertVerificationError ( True / **False** )                                                                                              |

| **REF_ID**                |                      | Реферальный ID для новых аккаунтов                          |
| **USE_PROXY**             | False                | Включить использование прокси                                |
| **SESSIONS_PER_PROXY**    | 1                    | Количество сессий на один прокси                            |
| **DISABLE_PROXY_REPLACE** | False                | Отключить замену прокси при ошибке                          |
| **SESSION_START_DELAY**   | 360                  | Задержка перед стартом сессии (сек)                         |
| **ENABLE_GAMES**          | True                 | Включить игру                                               |
| **DISABLED_GAMES_SESSIONS** | "session1,session2"   | Отключить игры в сессиях (через запятую)                    |
| **MAX_GAMES_PER_SESSION** | 0                    | Максимум игр за сессию (0 = без ограничений)               |
| **BLACKLISTED_SESSIONS** | ""                   | Сессии, которые не будут использоваться (через запятую)     |
| **DEBUG_LOGGING**         | False                | Включить отладочное логирование                             |
| **DEVICE_PARAMS**         | False                | Включить пользовательские параметры устройства              |

---

## 💰 Поддержка и донаты

Поддержите разработку с помощью криптовалют или платформ:

| Валюта               | Адрес кошелька                                                                       |
|----------------------|-------------------------------------------------------------------------------------|
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

## 📞 Контакты

Если у вас возникли вопросы или предложения:
- **Telegram**: [Присоединяйтесь к нашему каналу](https://t.me/+x8gutImPtaQyN2Ey)

---
## ⚠️ Дисклеймер

Данное программное обеспечение предоставляется "как есть", без каких-либо гарантий. Используя этот бот, вы принимаете на себя полную ответственность за его использование и любые последствия, которые могут возникнуть.

Автор не несет ответственности за:
- Любой прямой или косвенный ущерб, связанный с использованием бота
- Возможные нарушения условий использования сторонних сервисов
- Блокировку или ограничение доступа к аккаунтам

Используйте бота на свой страх и риск и в соответствии с применимым законодательством и условиями использования сторонних сервисов.


