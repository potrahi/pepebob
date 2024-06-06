from typing import List, Optional, Dict

from sqlalchemy.orm import Session

from core.entities.word_entity import Word as WordEntity
from core.repositories.pair_repository import PairRepository
from core.repositories.reply_repository import ReplyRepository
from core.repositories.word_repository import WordRepository
from config import Config

class LearnService:
    def __init__(self, words: List[str], chat_id: int, session: Session):
        self.end_sentence = Config().end_sentence
        self.words = words
        self.chat_id = chat_id
        self.session = session

    def learn_pair(self) -> None:
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

        pair_ids: List[int] = []

        while new_words:
            trigram_map: Dict[int, int] = {}
            trigram = new_words[:3]
            new_words = new_words[1:]

            for i, w in enumerate(trigram):
                if w is not None and w in preloaded_words:
                    trigram_map[i] = preloaded_words[w].id

            pair = PairRepository().get_pair_or_create_by(self.session, self.chat_id, trigram_map.get(0), trigram_map.get(1))
            pair_ids.append(pair.id)

            reply = ReplyRepository().get_reply_by(self.session, pair.id, trigram_map.get(2))
            if reply:
                ReplyRepository().increment_reply(self.session, reply.id, reply.count)
            else:
                ReplyRepository().create_reply_by(self.session, pair.id, trigram_map.get(2))

        PairRepository().touch(self.session, pair_ids)
