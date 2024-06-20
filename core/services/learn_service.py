"""
This module provides the LearnService class for managing the learning process
of word pairs and replies using SQLAlchemy. It interacts with WordRepository,
PairRepository, and ReplyRepository to store and retrieve data.
"""

from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from core.entities.word_entity import Word
from core.repositories.pair_repository import PairRepository
from core.repositories.reply_repository import ReplyRepository
from core.repositories.word_repository import WordRepository


class LearnService:
    """
    Service class for managing the learning process of word pairs and replies.
    """

    def __init__(
            self, words: List[str], end_sentence: List[str],
            chat_id: int, session: Session):
        """
        Initialize the LearnService with words, chat_id, and a SQLAlchemy session.

        Args:
            words (List[str]): List of words to learn.
            end_sentence (List[str]): List of end sentence punctuation
            chat_id (int): Chat ID associated with the learning process.
            session (Session): SQLAlchemy session for database operations.
        """
        self.words = words
        self.end_sentence = end_sentence
        self.chat_id = chat_id
        self.session = session
        self.word_repo = WordRepository()
        self.pair_repo = PairRepository()
        self.reply_repo = ReplyRepository()

    def learn_pair(self) -> None:
        """
        Learn word pairs and manage replies by storing them in the database.
        """
        self._learn_words()
        new_words = self._prepare_new_words()
        pair_ids = self._process_trigrams(new_words)
        self._update_pairs_timestamp(pair_ids)

    def _learn_words(self) -> None:
        """
        Learn words by storing them in the database.
        """
        self.word_repo.learn_words(self.session, self.words)

    def _prepare_new_words(self) -> List[Optional[str]]:
        """
        Prepare a list of new words with None separators based on end sentence characters.

        Returns:
            List[Optional[str]]: The prepared list of new words.
        """
        new_words: List[Optional[str]] = [None]
        for word in self.words:
            new_words.append(word)
            if word[-1] in self.end_sentence:
                new_words.append(None)

        if new_words[-1] is not None:
            new_words.append(None)

        return new_words

    def _process_trigrams(self, new_words: List[Optional[str]]) -> List[int]:
        """
        Process trigrams and manage pairs and replies in the database.

        Args:
            new_words (List[Optional[str]]): The list of new words to process.

        Returns:
            List[int]: List of processed pair IDs.
        """
        preloaded_words = self._preload_words()
        pair_ids = []
        num_words = len(new_words)

        for i in range(num_words - 2):
            trigram_map, _ = self._map_trigram(
                new_words[i:i+3], preloaded_words)

            pair = self.pair_repo.get_pair_or_create_by(
                self.session, self.chat_id, trigram_map.get(0), trigram_map.get(1))
            pair_ids.append(pair.id)

            self._manage_reply(pair.id, trigram_map.get(2))

        return pair_ids

    def _preload_words(self) -> Dict[str, Word]:
        """
        Preload words from the database into a dictionary.

        Returns:
            Dict[str, Word]: Dictionary of preloaded words.
        """
        # Fetch words from the repository
        words = self.word_repo.get_by_words(self.session, self.words)

        # Create a dictionary mapping word strings to Word objects
        preloaded_words = {word.word: word for word in words}
        return preloaded_words

    def _map_trigram(self, new_words: List[Optional[str]],
                     preloaded_words: Dict[str, Word]
                     ) -> Tuple[Dict[int, int], List[Optional[str]]]:
        """
        Map a trigram of words to their IDs.

        Args:
            new_words (List[Optional[str]]): The list of new words.
            preloaded_words (Dict[str, Word]): Dictionary of preloaded words.

        Returns:
            Tuple[Dict[int, int], List[Optional[str]]]: The trigram map and the trigram.
        """
        trigram_map = {}
        trigram = new_words[:3]

        for i, word in enumerate(trigram):
            if word is not None and word in preloaded_words:
                trigram_map[i] = preloaded_words[word].id

        return trigram_map, trigram

    def _manage_reply(self, pair_id: int, word_id: Optional[int]) -> None:
        """
        Manage replies for a given pair and word ID.

        Args:
            pair_id (int): The pair ID.
            word_id (Optional[int]): The word ID.
        """
        reply = self.reply_repo.get_reply_by(self.session, pair_id, word_id)
        if reply:
            self.reply_repo.increment_reply(
                self.session, reply.id, reply.count)
        else:
            self.reply_repo.create_reply_by(self.session, pair_id, word_id)

    def _update_pairs_timestamp(self, pair_ids: List[int]) -> None:
        """
        Update the timestamp of the given pairs.

        Args:
            pair_ids (List[int]): List of pair IDs to update.
        """
        self.pair_repo.touch(self.session, pair_ids)
