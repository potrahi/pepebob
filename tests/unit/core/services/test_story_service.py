from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from core.entities.chat_entity import Chat
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.entities.word_entity import Word
from core.services.story_service import StoryService


def test_generate_story(
        story_service: StoryService, dbsession: Session, word1: Word,
        word2: Word, chat: Chat):
    """
    Test the generate method to ensure it produces a story.
    """
    # Setup pairs and replies
    pair1 = Pair(chat_id=chat.id, first_id=word1.id, second_id=word2.id)
    dbsession.add(pair1)
    dbsession.commit()

    reply1 = Reply(pair_id=pair1.id, word_id=word2.id, count=1)
    dbsession.add(reply1)
    dbsession.commit()

    story = story_service.generate()

    assert story is not None
    assert any(word in story for word in [word1.word, word2.word])


def test_generate_story_with_context(
        story_service: StoryService, dbsession: Session, word1: Word,
        word2: Word, chat: Chat):
    """
    Test the generate method with context words to ensure it produces a story.
    """
    # Add context word to database
    context_word = Word(word="contextword")
    dbsession.add(context_word)
    dbsession.commit()

    # Setup pairs and replies
    pair1 = Pair(chat_id=chat.id, first_id=word1.id, second_id=context_word.id)
    dbsession.add(pair1)
    dbsession.commit()

    reply1 = Reply(pair_id=pair1.id, word_id=word2.id, count=1)
    dbsession.add(reply1)
    dbsession.commit()

    assert dbsession.query(Pair).count() == 1
    assert dbsession.query(Reply).count() == 1

    story = story_service.generate()

    assert story is not None
    assert any(word in story for word in [
               word1.word, context_word.word, word2.word])


def test_generate_story_no_pairs(story_service: StoryService):
    """
    Test the generate method when there are no pairs to ensure it returns None.
    """
    story = story_service.generate()
    assert story is None


def test_generate_story_with_sentences(
        story_service: StoryService, dbsession: Session,
        word1: Word, word2: Word, chat: Chat):
    """
    Test the generate method with sentence delimiters.
    """
    # Add context word to database
    context_word = Word(word="contextword")
    dbsession.add(context_word)
    dbsession.commit()

    # Add additional words to the database
    additional_words = ["hello", "world", "goodbye"]
    for word_text in additional_words:
        db_word = Word(word=word_text)
        dbsession.add(db_word)
        dbsession.commit()

    # Retrieve all words from the database
    hello_word = dbsession.query(Word).filter_by(word="hello").first()
    world_word = dbsession.query(Word).filter_by(word="world").first()
    goodbye_word = dbsession.query(Word).filter_by(word="goodbye").first()

    # Setup pairs and replies
    created_time = datetime.now() - timedelta(minutes=15)

    assert hello_word
    assert world_word
    assert goodbye_word

    pair1 = Pair(chat_id=chat.id, first_id=word1.id, second_id=context_word.id,
                 created_at=created_time, updated_at=created_time)
    dbsession.add(pair1)

    pair2 = Pair(chat_id=chat.id, first_id=context_word.id,
                 second_id=word2.id, created_at=created_time, updated_at=created_time)
    dbsession.add(pair2)

    # Add pairs for new words
    pair3 = Pair(chat_id=chat.id, first_id=hello_word.id, second_id=world_word.id,
                 created_at=created_time, updated_at=created_time)
    dbsession.add(pair3)

    pair4 = Pair(chat_id=chat.id, first_id=world_word.id, second_id=goodbye_word.id,
                 created_at=created_time, updated_at=created_time)
    dbsession.add(pair4)

    dbsession.commit()

    reply1 = Reply(pair_id=pair1.id, word_id=word2.id, count=1)
    dbsession.add(reply1)

    reply2 = Reply(pair_id=pair3.id, word_id=goodbye_word.id, count=1)
    dbsession.add(reply2)

    dbsession.commit()

    # Adjust words to include sentence delimiters
    story_service.words = ["hello", "world.", "goodbye", "world"]

    story = story_service.generate()

    print(f"Generated story: {story}")

    assert story is not None
    assert any(word in story for word in ["hello", "world", "goodbye"])
    assert story[-1] in story_service.end_sentence
