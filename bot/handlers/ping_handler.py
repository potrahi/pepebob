"""
This module defines the PingHandler class, which handles the ping command
and responds with a pong message.
"""

from typing import Optional
from bot.handlers.generic_handler import GenericHandler

class PingHandler(GenericHandler):
    """
    Handler class responsible for responding to ping commands.

    Methods:
        call: Asynchronously returns a pong message.
    """

    async def call(self, *args, **kwargs) -> Optional[str]:
        """
        Asynchronously returns a pong message in response to a ping command.

        This method performs the following steps:
        1. Calls the `before` method to execute any preliminary actions before 
            handling the update.
        2. Returns a simple string "Pong." indicating a successful ping response.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Optional[str]: A string "Pong." indicating a successful ping response.
        """
        self.before()
        return "Pong."
