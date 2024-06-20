"""
This module contains the SetGabHandler class which is responsible for setting the gab level
in a chat for a Telegram bot.
"""

from typing import Optional

from core.repositories.chat_repository import ChatRepository
from bot.handlers.generic_handler import GenericHandler


class SetGabHandler(GenericHandler):
    """
    Handler for setting the gab level in a chat.
    """

    async def call(self, *args, **kwargs) -> Optional[str]:
        """
        Sets the gab level for the chat if it is within the allowed range (0-50).

        This method performs the following steps:
        1. Calls the `before` method to execute any preliminary actions before handling the update.
        2. Retrieves the 'level' from the keyword arguments.
        3. Validates that the 'level' is provided and is within the allowed range (0-50).
        4. Updates the gab level (random chance) for the chat using the `ChatRepository`.
        5. Returns a message indicating the result of the action.

        Args:
            *args: Additional arguments, should include 'level'.
            **kwargs: Additional keyword arguments

        Returns:
            Optional[str]: A message indicating the result of the action. Possible return 
                values include:
                    - A message indicating that the level is required if not provided.
                    - A message indicating that the level must be within the allowed range 
                        if invalid.
                    - A success message indicating that the gab level has been set if valid.
        """
        self.before()

        level = int(args[0])
        if level is None:
            return "Level is required."

        if level > 50 or level < 0:
            return "0-50 allowed, Dude!"

        ChatRepository().update_random_chance(self.session, self.chat.id, level)
        return f"Ya wohl, Lord Helmet! Setting gab to {level}"
