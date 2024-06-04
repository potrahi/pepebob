from typing import List
from core.core_config import CoreConfig

class Config:
    def __init__(self):
        self.core_config = CoreConfig()

    class Bot:
        def __init__(self, config: CoreConfig):
            self.bot_config = config.get_config("bot")

        @property
        def twitter(self) -> bool:
            return self.bot_config.getboolean("twitter")

        @property
        def async_learn(self) -> bool:
            return self.bot_config.getboolean("async_learn")

        @property
        def cleanup_limit(self) -> int:
            return self.bot_config.getint("cleanup_limit")

        @property
        def repost_chat_ids(self) -> List[int]:
            return list(map(int, self.bot_config.get("repost_chat_ids").strip('[]').split(',')))

        @property
        def repost_chat_id(self) -> int:
            return self.bot_config.getint("repost_chat_id")

        @property
        def telegram_token(self) -> str:
            return self.bot_config.get("telegram_token")

        @property
        def anchors(self) -> List[str]:
            return self.bot_config.get("anchors").strip('[]').split(', ')

        @property
        def name(self) -> str:
            return self.bot_config.get("name")

    @property
    def bot(self) -> Bot:
        return Config.Bot(self.core_config)
