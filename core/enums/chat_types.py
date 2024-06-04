class ChatType:
    @staticmethod
    def from_int(v: int) -> str:
        return {
            0: "chat",
            1: "faction",
            2: "supergroup",
            3: "channel"
        }.get(v, "chat")

    @staticmethod
    def from_str(v: str) -> int:
        return {
            "chat": 0,
            "faction": 1,
            "supergroup": 2,
            "channel": 3
        }.get(v, 0)
