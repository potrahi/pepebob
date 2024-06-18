"""
This module provides the StoryService class for generating stories based on word pairs
and replies using SQLAlchemy. It interacts with PairRepository, ReplyRepository, and WordRepository
to store and retrieve data.
"""

from typing import List, Optional, Dict
from random import shuffle, randint
from sqlalchemy.orm import Session

from core.entities.word_entity import Word
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.repositories.pair_repository import PairRepository
from core.repositories.reply_repository import ReplyRepository
from core.repositories.word_repository import WordRepository


class StoryService:
    """
    Service class for generating stories based on word pairs and replies.
    """

    def __init__(self, words: List[str], context: List[str], chat_id: int,
                 session: Session, end_sentence: List[str], sentences: Optional[int] = None):
        """
        Initialize the StoryService with words, context, chat_id, session, end_sentence, 
            and sentences.

        Args:
            words (List[str]): List of words to be used in the story.
            context (List[str]): List of context words.
            chat_id (int): Chat ID associated with the story generation.
            session (Session): SQLAlchemy session for database operations.
            end_sentence (List[str]): List of characters that indicate sentence endings.
            sentences (Optional[int], optional): Number of sentences to generate. Defaults to None.
        """
        self.words = words
        self.context = context
        self.chat_id = chat_id
        self.session = session
        self.end_sentence = end_sentence
        self.sentences = sentences
        self.current_sentences = []
        self.current_word_ids = []

    def _generate_sentence(self) -> None:
        """
        Generate a single sentence for the story and add it to the current sentences.
        """
        sentence = []
        safety_counter = 50

        first_word_id: Optional[int] = None
        second_word_ids: List[Optional[int]] = list(self.current_word_ids)

        pairs = self._get_shuffled_pairs(first_word_id, second_word_ids)

        while safety_counter > 0 and pairs:
            safety_counter -= 1
            pair = pairs.pop(0)
            replies = self._get_shuffled_replies(pair.id)

            first_word_id = pair.second_id
            word_entity = self._get_word_entity(pair.second_id)

            if word_entity:
                if not sentence:
                    sentence.append(word_entity.word.lower())
                    if pair.second_id in self.current_word_ids:
                        self.current_word_ids.remove(pair.second_id)

                if replies:
                    reply = replies[0]
                    second_word_ids = [reply.word_id]
                    word_entity = self._get_word_entity(reply.word_id)

                    if word_entity:
                        sentence.append(word_entity.word)
                    else:
                        break
                else:
                    break
            pairs = self._get_shuffled_pairs(first_word_id, second_word_ids)

        if sentence:
            final_sentence = self._set_sentence_end(" ".join(sentence).strip())
            self.current_sentences.append(final_sentence)

    def _get_shuffled_pairs(self, first_word_id: Optional[int],
                            second_word_ids: List[Optional[int]]) -> List[Pair]:
        """
        Retrieve and shuffle pairs based on first and second word IDs.

        Args:
            first_word_id (Optional[int]): The first word ID.
            second_word_ids (List[Optional[int]]): The list of second word IDs.

        Returns:
            List[Pair]: The shuffled list of pairs.
        """
        pairs = PairRepository().get_pair_with_replies(
            session=self.session, chat_id=self.chat_id,
            first_ids=first_word_id, second_ids=second_word_ids
        )
        shuffle(pairs)
        return pairs

    def _get_shuffled_replies(self, pair_id: int) -> List[Reply]:
        """
        Retrieve and shuffle replies for a given pair ID.

        Args:
            pair_id (int): The pair ID.

        Returns:
            List[Reply]: The shuffled list of replies.
        """
        replies = ReplyRepository().replies_for_pair(
            session=self.session, pair_id=pair_id)
        shuffle(replies)
        return replies

    def _get_word_entity(self, word_id: Optional[int]) -> Optional[Word]:
        """
        Retrieve a Word by its ID.

        Args:
            word_id (Optional[int]): The word ID.

        Returns:
            Optional[Word]: The Word if found, otherwise None.
        """
        return WordRepository().get_word_by_id(session=self.session, word_id=word_id or 0)

    def _set_sentence_end(self, sentence: str) -> str:
        """
        Ensure the sentence ends with a valid end sentence character.

        Args:
            sentence (str): The sentence to check.

        Returns:
            str: The sentence with a valid end character.
        """
        if sentence[-1] in self.end_sentence:
            return sentence
        else:
            end_punctuation = self.end_sentence[randint(
                0, self._end_sentence_length - 1)]
            return f"{sentence}{end_punctuation}"

    @property
    def _end_sentence_length(self) -> int:
        """
        Get the length of the end_sentence list.

        Returns:
            int: The length of the end_sentence list.
        """
        return len(self.end_sentence)

    def generate(self) -> Optional[str]:
        """
        Generate a story based on the provided words and context.

        Returns:
            Optional[str]: The generated story, or None if no sentences were generated.
        """
        current_words: Dict[str, int] = {w.word: w.id for w in WordRepository().get_by_words(
            session=self.session, words=self.words + self.context)}
        self.current_word_ids = [current_words[w]
                                 for w in self.words if w in current_words]

        num_sentences = self.sentences if self.sentences is not None else randint(
            1, 3)
        for _ in range(num_sentences):
            self._generate_sentence()

        if self.current_sentences:
            return " ".join(self.current_sentences)
        else:
            return None
