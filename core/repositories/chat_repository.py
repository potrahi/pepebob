import logging
from typing import List, Optional
from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from core.entities.chat_entity import Chat as ChatEntity
from core.enums.chat_types import ChatType

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatRepository:
    def get_list(self, session: Session, limit: int = 20, offset: int = 0) -> List[ChatEntity]:
        logger.debug(f"Fetching chat list with limit={limit} and offset={offset}")
        result = session.execute(select(ChatEntity).limit(limit).offset(offset)).scalars().all()
        return list(result)

    def get_chat_by_id(self, session: Session, id: int) -> Optional[ChatEntity]:
        logger.debug(f"Fetching chat with id={id}")
        result = session.execute(select(ChatEntity).where(ChatEntity.id == id).limit(1)).scalar()
        return result

    def get_or_create_by(self, session: Session, telegram_id: int, name: str, chat_type: str) -> ChatEntity:
        logger.debug(f"Fetching or creating chat with telegram_id={telegram_id}, name={name}, chat_type={chat_type}")
        chat = self.get_by_telegram_id(session, telegram_id)
        if chat:
            logger.debug(f"Chat found with telegram_id={telegram_id}")
            return chat
        else:
            logger.debug(f"Chat not found, creating new chat with telegram_id={telegram_id}")
            return self.create(session, telegram_id, name, chat_type)

    def update_random_chance(self, session: Session, id: int, random_chance: int) -> None:
        logger.debug(f"Updating random_chance for chat id={id} to random_chance={random_chance}")
        session.execute(
            update(ChatEntity)
            .where(ChatEntity.id == id)
            .values(random_chance=random_chance, updated_at=datetime.now())
        )
        session.commit()

    def update_repost_chat(self, session: Session, id: int, repost_chat_username: str) -> None:
        logger.debug(f"Updating repost_chat_username for chat id={id} to repost_chat_username={repost_chat_username}")
        session.execute(
            update(ChatEntity)
            .where(ChatEntity.id == id)
            .values(repost_chat_username=repost_chat_username, updated_at=datetime.now())
        )
        session.commit()

    def update_chat(self, session: Session, id: int, name: Optional[str], telegram_id: int) -> None:
        logger.debug(f"Updating chat id={id} with name={name} and telegram_id={telegram_id}")
        session.execute(
            update(ChatEntity)
            .where(ChatEntity.id == id)
            .values(name=name, telegram_id=telegram_id, updated_at=datetime.now())
        )
        session.commit()

    def create(self, session: Session, telegram_id: int, name: str, chat_type: str) -> ChatEntity:
        logger.debug(f"Creating chat with telegram_id={telegram_id}, name={name}, chat_type={chat_type}")
        session.execute(
            insert(ChatEntity)
            .values(
                telegram_id=telegram_id,
                name=name,
                chat_type=ChatType.from_str(chat_type.lower()),
                updated_at=datetime.now(),
                created_at=datetime.now()
            )
            .on_conflict_do_nothing()
        )
        session.commit()

        chat = self.get_by_telegram_id(session, telegram_id)
        if chat:
            logger.debug(f"Chat created successfully with telegram_id={telegram_id}")
            return chat
        else:
            logger.error(f"Failed to create chat with telegram_id={telegram_id}")
            raise ValueError("No such chat")

    def get_by_telegram_id(self, session: Session, telegram_id: int) -> Optional[ChatEntity]:
        logger.debug(f"Fetching chat with telegram_id={telegram_id}")
        result = session.execute(select(ChatEntity).where(ChatEntity.telegram_id == telegram_id).limit(1)).scalar()
        return result
