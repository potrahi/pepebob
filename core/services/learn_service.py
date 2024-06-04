import logging
from typing import List, Optional, Dict

from sqlalchemy.orm import Session

from core.entities.word_entity import Word as WordEntity
from core.repositories.pair_repository import PairRepository
from core.repositories.reply_repository import ReplyRepository
from core.repositories.word_repository import WordRepository
from init_config import config

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LearnService:
    def __init__(self, words: List[str], chat_id: int, session: Session):
        logger.debug(f"Initializing LearnService with words={words}, chat_id={chat_id}")
        self.end_sentence = config.core_config.punctuation['end_sentence']
        self.words = words
        self.chat_id = chat_id
        self.session = session

    def learn_pair(self) -> None:
        logger.debug(f"Starting to learn pairs for chat_id={self.chat_id}")
        WordRepository().learn_words(self.session, self.words)
        new_words: List[Optional[str]] = [None]
        preloaded_words: Dict[str, WordEntity] = {we.word: we for we in WordRepository().get_by_words(self.session, self.words)}

        for w in self.words:
            new_words.append(w)
            end_sentence = self.end_sentence
            if w[-1] in end_sentence:
                new_words.append(None)

        if new_words[-1] is not None:
            new_words.append(None)

        logger.debug(f"Processed words into new_words={new_words}")
        pair_ids: List[int] = []

        while new_words:
            trigram_map: Dict[int, int] = {}
            trigram = new_words[:3]
            new_words = new_words[1:]

            for i, w in enumerate(trigram):
                if w is not None and w in preloaded_words:
                    trigram_map[i] = preloaded_words[w].id

            logger.debug(f"Trigram: {trigram}, Trigram map: {trigram_map}")
            pair = PairRepository().get_pair_or_create_by(self.session, self.chat_id, trigram_map.get(0), trigram_map.get(1))
            pair_ids.append(pair.id)

            reply = ReplyRepository().get_reply_by(self.session, pair.id, trigram_map.get(2))
            if reply:
                logger.debug(f"Incrementing reply for pair.id={pair.id}, reply.id={reply.id}")
                ReplyRepository().increment_reply(self.session, reply.id, reply.count)
            else:
                logger.debug(f"Creating new reply for pair.id={pair.id}, word_id={trigram_map.get(2)}")
                ReplyRepository().create_reply_by(self.session, pair.id, trigram_map.get(2))

        PairRepository().touch(self.session, pair_ids)
        logger.debug(f"Pairs touched: {pair_ids}")
