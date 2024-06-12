"""
This module contains the GetGabHandler class, which handles the 'get gab' requests
from the bot, providing information about the 'pizdlivost' level.
"""

from typing import Optional
from bot.handlers.generic_handler import GenericHandler


class GetGabHandler(GenericHandler):
    """
    GetGabHandler processes the 'get gab' request and responds with the pizdlivost level.
    """

    async def call(self, *args, **kwargs) -> Optional[str]:
        """
        Execute the main logic of the handler.

        This method performs the following steps:
        1. Calls the `before` method to execute any preliminary actions before handling the update.
        2. Retrieves the 'pizdlivost' level, represented by the `random_chance` attribute, 
            from the chat object.
        3. Returns a formatted response string indicating the 'pizdlivost' level.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Optional[str]: A formatted string indicating the 'pizdlivost' level, or None if 
                not available.
        """
        self.before()
        pizdlivost_level = self.chat.random_chance
        return f"Pizdlivost level is on {pizdlivost_level}"
