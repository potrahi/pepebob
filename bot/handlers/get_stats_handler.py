"""
This module defines the GetStatsHandler class, which handles the retrieval
of statistics about known pairs in a chat.
"""

from typing import Optional
from core.repositories.pair_repository import PairRepository
from bot.handlers.generic_handler import GenericHandler

class GetStatsHandler(GenericHandler):
    """
    Handler class responsible for retrieving statistics about known pairs in a chat.

    Methods:
        call: Asynchronously retrieves and returns the count of known pairs in the chat.
    """

    async def call(self, *args, **kwargs) -> Optional[str]:
        """
        Asynchronously retrieves the count of known pairs in the current chat.

        This method performs the following steps:
        1. Calls the `before` method to execute any preliminary actions before handling the update.
        2. Uses the `PairRepository` to retrieve the count of known pairs for the current chat 
            from the database.
        3. Returns a formatted string containing the count of known pairs in the chat.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Optional[str]: A string containing the count of known pairs in the chat, or None if 
                not available.
        """
        self.before()
        count = PairRepository().get_pairs_count(self.session, self.chat.id)
        return f"Known pairs in this chat: {count}."
