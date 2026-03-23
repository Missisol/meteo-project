import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class TelegramConfig:
    """Конфигурация Telegram бота."""
    bot_token: str = ''
    chat_id: str = ''


class TelegramSender:
    """Отправщик уведомлений в Telegram."""
    
    def __init__(self, config: TelegramConfig):
        self._config = config

    @property
    def is_configured(self) -> bool:
        """Проверка, настроен ли Telegram."""
        return bool(self._config.bot_token and self._config.chat_id)

    def send_notification(self, temperature: float, humidity: float, pressure: int) -> bool:
        """Отправка уведомления с данными датчиков."""
        if not self.is_configured:
            logger.debug("Telegram not configured, skipping notification")
            return False
            
        text = (f"Данные на: {datetime.now().strftime('%d.%m.%Y, %H:%M')}\n"
                f"Температура: {temperature}°C\n"
                f"Влажность: {humidity}%\n"
                f"Давление: {pressure} гПа")
        
        return self._send_message(text)

    def _send_message(self, text: str, max_retries: int = 3, retry_delay: int = 10) -> bool:
        """Отправка сообщения в Telegram с повторными попытками."""
        url = f"https://api.telegram.org/bot{self._config.bot_token}/sendMessage"
        payload = {'chat_id': self._config.chat_id, 'text': text}

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                return True
            except requests.RequestException as e:
                logger.warning(f"Telegram attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        logger.error(f"Failed to send Telegram message after {max_retries} attempts")
        return False


# Глобальный экземпляр
_telegram_sender: Optional[TelegramSender] = None


def init_telegram(flask_app) -> TelegramSender:
    """Инициализация Telegram отправщика."""
    global _telegram_sender
    config = TelegramConfig(
        bot_token=flask_app.config.get('BOT_TOKEN', ''),
        chat_id=flask_app.config.get('CHAT_ID', ''),
    )
    _telegram_sender = TelegramSender(config)
    return _telegram_sender


def get_telegram_sender() -> TelegramSender:
    """Получение экземпляра TelegramSender."""
    if _telegram_sender is None:
        raise RuntimeError("Telegram sender not initialized")
    return _telegram_sender
