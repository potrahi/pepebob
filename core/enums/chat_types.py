"""
This module defines the ChatType class, which provides a method to convert
chat type strings to their corresponding integer values.
"""

class ChatType:
    """
    A utility class for converting chat type strings to integer values.

    Methods:
        from_str(v: str) -> int:
            Converts a chat type string to its corresponding integer value.
    """

    @staticmethod
    def from_str(v: str) -> int:
        """
        Converts a chat type string to its corresponding integer value.

        Parameters:
            v (str): The chat type as a string. Valid values are "chat", "faction",
                     "supergroup", and "channel".

        Returns:
            int: The corresponding integer value for the chat type. Defaults to 0
                 if the input string does not match any known chat type.
        """
        return {
            "chat": 0,
            "faction": 1,
            "supergroup": 2,
            "channel": 3
        }.get(v, 0)
