import asyncio
import csv
from typing import Optional, List, Dict, Union
from telegram import Update
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import (
    PeerUser, User, Message as TelethonMessage,
    TypeInputPeer, MessageEmpty, MessageService)
from telethon.tl.types.messages import Messages, ChannelMessages
from sqlalchemy.orm import Session
from bot.handlers.generic_handler import GenericHandler
from config import Config


class LearnHandler(GenericHandler):
    def __init__(self, update: Update, session: Session, config: Config, client: TelegramClient):
        super().__init__(update, session, config)
        self.client = client
        self.chat_id = self.telegram_id
        
    async def get_messages(self, history):
        messages = []
        user_dict: Dict[int, str] = {}
        for message in history.messages:
            if isinstance(message, TelethonMessage):
                if message.from_id and isinstance(message.from_id, PeerUser):
                    user_id = message.from_id.user_id
                    if user_id not in user_dict:
                        user = await self.client.get_entity(user_id)
                        if user and isinstance(user, User):
                            user_dict[user_id] = user.username if user.username else f"{user.first_name} {user.last_name}"
                    sender_username = user_dict[user_id]
                else:
                    sender_username = None

                if isinstance(message, (MessageEmpty, MessageService)):
                    continue

                date_str = message.date.isoformat() if message.date else "Unknown"

                messages.append({
                    'id': message.id,
                    'date': date_str,
                    'sender_username': sender_username,
                    'message': message.message
                })
        return messages

    async def get_chat_history(
        self, chat_id: int, limit: int = 100) -> List[Dict[str, Union[int, str, Optional[str]]]]:
        messages = []

        chat_entity = await self.client.get_entity(chat_id)

        if isinstance(chat_entity, list):
            raise ValueError("Expected a single entity, but got a list")

        chat: TypeInputPeer = await self.client.get_input_entity(chat_entity)

        last_id = 0
        total_messages = 0

        while True:
            try:
                history = await self.client(GetHistoryRequest(
                    peer=chat,
                    offset_id=last_id,
                    offset_date=None,
                    add_offset=0,
                    limit=limit,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))

                if not isinstance(history, (Messages, ChannelMessages)):
                    raise ValueError("Unexpected return type from GetHistoryRequest")

                if not history.messages:
                    break

                messages = await self.get_messages(history)

                last_id = history.messages[-1].id
                total_messages += len(history.messages)
                print(f"Retrieved {total_messages} messages so far.")

            except errors.FloodWaitError as e:
                print(f"Flood wait for {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
                continue

            except errors.RPCError as e:
                print(f"An error occurred: {e}")
                break

        return messages

    async def save_messages(self):
        messages = await self.get_chat_history(self.chat_id)

        with open('chat_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'date', 'sender_username', 'message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for message in messages:
                writer.writerow(message)
        return f"Messages downloaded: {len(messages)}"
    
    def call(self) -> Optional[str]:
        self.before()
        return "learn handler called"
