"""
import_history_handler.py

This module defines the ImportHistoryHandler class responsible for processing JSON files
containing messages, extracting relevant data, and pushing it to a learn queue.
"""

import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from telegram import Document, File, Update
from telegram.error import TimedOut, NetworkError
from sqlalchemy.orm import Session
from bot.handlers.generic_handler import GenericHandler
from config import Config
from core.repositories.learn_queue_repository import LearnQueueRepository

logger = logging.getLogger(__name__)


class ImportHistoryHandler(GenericHandler):
    """
    ImportHistoryHandler is responsible for handling the /import_history command. It processes
    a JSON file sent by the user, extracts messages, and pushes the words to a
    learning queue.
    """
    EXCLUDED_SENDERS = {"pepeground_bot", "pepepot", "pepepot_test"}

    def __init__(self, update: Update, session: Session,
                 config: Config, document: Document):
        """
        Initializes the ImportHistoryHandler instance.

        Args:
            update (Update): The Telegram update instance.
            session (Session): The SQLAlchemy session instance.
            config (Config): The configuration instance.
            document (Document): The Telegram document instance.
        """
        super().__init__(update, session, config)
        self.document = document
        self.learn_queue = LearnQueueRepository()

    async def call(self, *args, **kwargs) -> Optional[str]:
        """
        Main entry point for handling the /learn command.

        This method performs the following steps:
        1. Calls the `before` method to execute any preliminary actions before handling the update.
        2. Checks if a document is attached. If not, returns a message indicating that a JSON file 
            should be sent with the command.
        3. Processes the attached JSON file to extract messages and push words to 
            the learning queue.
        4. Handles and logs specific errors such as JSON decoding errors, network errors, 
            and timeouts.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Optional[str]: A result message indicating success or failure. Possible return 
                values include:
                    - A message indicating that no document was attached.
                    - A success message indicating the number of processed messages.
                    - An error message indicating a specific failure reason (e.g., 
                        JSON decode error, network error).
        """
        try:
            self.before()
            if not self.document:
                return "No document attached. Please send a JSON file with the /learn command."
            return await self._process_json_file()
        except (json.JSONDecodeError, TimedOut, NetworkError) as e:
            logger.error("Specific error in call method: %s", e)
            return f"An error occurred: {e}"

    async def _process_json_file(self) -> str:
        """
        Processes the JSON file sent by the user, extracts messages, 
        and pushes words to the learning queue.

        Returns:
            str: The result message indicating success or failure.
        """
        if not self._is_valid_document():
            return "Please send a valid JSON file with the /learn command."

        telegram_file = await self._download_file()
        if not telegram_file:
            return "Failed to download the file."

        try:
            byte_array = await telegram_file.download_as_bytearray()
            json_data = json.loads(byte_array.decode('utf-8'))
            extracted_data = self._extract_message_data(json_data)

            for message in extracted_data["messages"]:
                words = self._extract_words(message["text"])
                self.learn_queue.push(words, self.chat.id)

            return f"""
        Successfully processed {len(extracted_data['messages'])} 
        messages from provided JSON file."""

        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", e)
            return "Failed to decode the JSON file."
        except (TimedOut, NetworkError) as e:
            logger.error("Network error while processing JSON file: %s", e)
            return "Network error occurred while processing the JSON file."

    async def _download_file(self, retries: int = 3, delay: int = 5) -> Optional[File]:
        """
        Attempts to download the file with retries on failure.

        Args:
            retries (int): Number of retries.
            delay (int): Delay between retries in seconds.

        Returns:
            Optional[File]: The downloaded file, or None if all retries failed.
        """
        for attempt in range(retries):
            try:
                if self.document:
                    return await self.document.get_file()
            except (TimedOut, NetworkError) as e:
                logger.warning("Attempt %d of %d failed: %s",
                               attempt + 1, retries, e)
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
        return None

    def _is_valid_document(self) -> bool:
        """
        Validates the document.

        Returns:
            bool: True if the document is valid, otherwise False.
        """
        return self.document is not None and self.document.mime_type == 'application/json'

    def _extract_message_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts relevant message data from the JSON.

        Args:
            json_data (Dict[str, Any]): The JSON data.

        Returns:
            Dict[str, Any]: Extracted messages.
        """
        messages = [
            {
                "id": msg.get("id"),
                "date": msg.get("date"),
                "from": msg.get("from"),
                "from_id": msg.get("from_id"),
                "text": msg.get("text")
            }
            for msg in json_data.get("messages", [])
            if msg.get("type") == "message"
            and msg.get("from") not in self.EXCLUDED_SENDERS
            and isinstance(msg.get("text"), str)
            and msg.get("text").strip()
        ]
        return {"messages": messages}

    def _extract_words(self, text: str) -> List[str]:
        """
        Extracts words from the text.

        Args:
            text (str): The message text.

        Returns:
            List[str]: A list of words extracted from the text.
        """
        return self.get_words(text)
