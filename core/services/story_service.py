import logging
from typing import List, Optional, Dict
from random import shuffle, randint
from sqlalchemy.orm import Session

from core.entities.pair_entity import Pair as PairEntity
from core.repositories.pair_repository import PairRepository
from core.repositories.reply_repository import ReplyRepository
from core.repositories.word_repository import WordRepository
from config import Config

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class StoryService:
    def __init__(self, words: List[str], context: List[str], chat_id: int, session: Session, sentences: Optional[int] = None):
        logger.debug(f"Initializing StoryService with words={words}, context={context}, chat_id={chat_id}, sentences={sentences}")
        self.end_sentence = Config().end_sentence
        self.words = words
        self.context = context
        self.chat_id = chat_id
        self.session = session
        self.sentences = sentences
        self.current_sentences = []
        self.current_word_ids = []

    def generate(self) -> Optional[str]:
        logger.debug("Generating story")
        current_words: Dict[str, int] = {w.word: w.id for w in WordRepository().get_by_words(
            session=self.session, words=self.words + self.context)}
        self.current_word_ids = [current_words[w] for w in self.words if w in current_words]

        for _ in range(self.sentences if self.sentences is not None else randint(1, 3)):
            self.generate_sentence()

        if self.current_sentences:
            story = " ".join(self.current_sentences)
            logger.debug(f"Generated story: {story}")
            return story
        else:
            logger.debug("No sentences generated")
            return None

    def generate_sentence(self) -> None:
        logger.debug("Generating sentence")
        sentence = []
        safety_counter = 50

        first_word_id: Optional[int] = None
        second_word_id: List[Optional[int]] = [id_ for id_ in self.current_word_ids]

        pair: Optional[PairEntity] = None

        pairs = PairRepository().get_pair_with_replies(
            session=self.session, chat_id=self.chat_id, first_ids=first_word_id, second_ids=second_word_id) 
        shuffle(pairs)
        pair = pairs[0] if pairs else None

        while safety_counter > 0:
            if pair is None:
                break

            safety_counter -= 1

            if pair is not None:
                replies = ReplyRepository().replies_for_pair(session=self.session, pair_id=pair.id)
                shuffle(replies)
                reply = replies[0] if replies else None

                first_word_id = pair.second_id

                word_entity = WordRepository().get_word_by_id(session=self.session, id=pair.second_id or 0)
                if word_entity:
                    if not sentence:
                        sentence.append(word_entity.word.lower())
                        if pair.second_id in self.current_word_ids:
                            self.current_word_ids.remove(pair.second_id)

                if reply and reply.word_id:
                    second_word_id = [reply.word_id]

                    word_entity = WordRepository().get_word_by_id(session=self.session, id=reply.word_id)
                    if word_entity:
                        sentence.append(word_entity.word)
                    else:
                        break
            pairs = PairRepository().get_pair_with_replies(
                session=self.session, chat_id=self.chat_id, first_ids=first_word_id, second_ids=second_word_id)
            shuffle(pairs)
            pair = pairs[0] if pairs else None

        if sentence:
            final_sentence = self.set_sentence_end(" ".join(sentence).strip())
            logger.debug(f"Generated sentence: {final_sentence}")
            self.current_sentences.append(final_sentence)

    def set_sentence_end(self, s: str) -> str:
        if s[-1] in self.end_sentence:
            return s
        else:
            end_punctuation = self.end_sentence[randint(0, self.end_sentence_length - 1)]
            logger.debug(f"Setting sentence end: {s}{end_punctuation}")
            return f"{s}{end_punctuation}"

    @property
    def end_sentence_length(self) -> int:
        length = len(self.end_sentence)
        logger.debug(f"End sentence length: {length}")
        return length
