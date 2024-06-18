import json
import asyncio
import logging
from typing import Optional, Dict, Any
from telegram import Document, File, Update
from telegram.error import TimedOut, NetworkError
from sqlalchemy.orm import Session
from bot.handlers.generic_handler import GenericHandler
from config import Config
from core.repositories.learn_queue_repository import LearnQueueRepository

logger = logging.getLogger(__name__)

class LearnHandler(GenericHandler):
    def __init__(self, update: Update, session: Session,
                 config: Config, document: Optional[Document] = None):
        super().__init__(update, session, config)
        self.document = document
        self.learn_queue = LearnQueueRepository()

    async def process_json_file(self) -> str:
        if not self.document or self.document.mime_type != 'application/json':
            return "Please send a JSON file with the /learn command."

        try:
            telegram_file = await self.get_file_with_retry()
            if not telegram_file:
                return "Failed to download the file."

            byte_array = await telegram_file.download_as_bytearray()
            json_data = json.loads(byte_array.decode('utf-8'))

            extracted_data = self.extract_message_data(json_data)
            output_file_path = 'extracted_messages.json'
            self.save_extracted_data(extracted_data, output_file_path)
            
            for message in extracted_data["messages"]:
                words = self.get_words(message["text"])
                self.learn_queue.push(words, self.chat.id)
                
            return f"Processed JSON data and saved to {output_file_path}"

        except Exception as e:
            logger.error("Error processing JSON file: %s", e)
            return "An error occurred while processing the JSON file."

    async def get_file_with_retry(self, retries: int = 3, delay: int = 5) -> Optional[File]:
        for attempt in range(retries):
            try:
                if self.document:
                    return await self.document.get_file()
            except (TimedOut, NetworkError) as e:
                logger.warning(f"Attempt {attempt + 1} of {retries} failed: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                else:
                    return None

    def extract_message_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        messages = []
        excluded_senders = {"pepeground_bot", "pepepot", "pepepot_test"}
        for message in json_data.get("messages", []):
            if message.get("type") == "message":
                sender = message.get("from")
                if sender not in excluded_senders:
                    text = message.get("text")
                    if isinstance(text, str) and text.strip():
                        messages.append({
                            "id": message.get("id"),
                            "date": message.get("date"),
                            "from": sender,
                            "from_id": message.get("from_id"),
                            "text": text
                        })
        return {"messages": messages}

    def save_extracted_data(self, extracted_data: Dict[str, Any], file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)

    async def call(self) -> Optional[str]:
        try:
            self.before()
            if not self.document:
                return "No document attached. Please send a JSON file with the /learn command."
            return await self.process_json_file()
        except Exception as e:
            logger.error("Error in call method: %s", e)
            return "An unexpected error occurred."
