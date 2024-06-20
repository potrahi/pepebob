from datetime import datetime
from core.entities.chat_entity import Chat
from core.entities.pair_entity import Pair
from core.entities.reply_entity import Reply
from core.entities.word_entity import Word


def test_create_chat(dbsession):
    creation_time = datetime(2023, 1, 1, 0, 0, 0)
    update_time = datetime(2023, 1, 1, 0, 0, 0)

    chat = Chat(
        telegram_id=123456789,
        chat_type=1,
        random_chance=10,
        created_at=creation_time,
        updated_at=update_time,
        name='Test Chat'
    )
    dbsession.add(chat)
    dbsession.commit()

    retrieved_chat = dbsession.query(
        Chat).filter_by(telegram_id=123456789).one()

    assert chat.id is not None
    assert retrieved_chat.telegram_id == 123456789
    assert retrieved_chat.chat_type == 1
    assert retrieved_chat.random_chance == 10
    assert retrieved_chat.created_at == creation_time
    assert retrieved_chat.updated_at == update_time
    assert retrieved_chat.name == 'Test Chat'


def test_create_word(dbsession):
    word = Word(word='hello')
    dbsession.add(word)
    dbsession.commit()

    retrieved_word = dbsession.query(Word).filter_by(word='hello').one()

    assert word.id is not None
    assert retrieved_word.word == 'hello'


def test_create_pair(dbsession):
    creation_time = datetime(2023, 2, 1, 0, 0, 0)
    update_time = datetime(2023, 2, 1, 0, 0, 0)

    chat = Chat(
        telegram_id=987654321,
        chat_type=1,
        random_chance=10,
        created_at=creation_time,
        updated_at=update_time,
        name='Another Chat'
    )
    word1 = Word(word='first')
    word2 = Word(word='second')
    dbsession.add_all([chat, word1, word2])
    dbsession.commit()

    pair = Pair(
        chat_id=chat.id,
        first_id=word1.id,
        second_id=word2.id
    )
    dbsession.add(pair)
    dbsession.commit()

    retrieved_chat = dbsession.query(
        Chat).filter_by(telegram_id=987654321).one()
    retrieved_word_1 = dbsession.query(
        Word).filter_by(word='first').one()
    retrieved_word_2 = dbsession.query(
        Word).filter_by(word='second').one()
    retrieved_pair = dbsession.query(
        Pair).filter_by(
            chat_id=retrieved_chat.id, first_id=retrieved_word_1.id,
            second_id=retrieved_word_2.id
    ).one()

    assert pair.id is not None
    assert retrieved_pair.chat_id == retrieved_chat.id
    assert retrieved_pair.first_id == retrieved_word_1.id
    assert retrieved_pair.second_id == retrieved_word_2.id


def test_create_reply(dbsession):
    creation_time = datetime(2023, 3, 1, 0, 0, 0)
    update_time = datetime(2023, 3, 1, 0, 0, 0)

    chat = Chat(
        telegram_id=123123123,
        chat_type=1,
        random_chance=10,
        created_at=creation_time,
        updated_at=update_time,
        name='Reply Chat'
    )
    word1 = Word(word='hello')
    word2 = Word(word='world')
    dbsession.add_all([chat, word1, word2])
    dbsession.commit()

    pair = Pair(
        chat_id=chat.id,
        first_id=word1.id,
        second_id=word2.id
    )
    dbsession.add(pair)
    dbsession.commit()

    reply = Reply(
        pair_id=pair.id,
        word_id=word1.id,
        count=1
    )
    dbsession.add(reply)
    dbsession.commit()

    retrieved_reply = dbsession.query(
        Reply).filter_by(pair_id=pair.id, word_id=word1.id).one()

    assert reply.id is not None
    assert retrieved_reply.pair_id == pair.id
    assert retrieved_reply.word_id == word1.id
    assert retrieved_reply.word_id != word2.id
    assert retrieved_reply.count == 1


def test_relationships(dbsession):
    chat = Chat(
        telegram_id=321321321,
        chat_type=1,
        random_chance=10,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        name='Relationship Chat'
    )
    word1 = Word(word='alpha')
    word2 = Word(word='beta')
    dbsession.add_all([chat, word1, word2])
    dbsession.commit()

    pair = Pair(
        chat_id=chat.id,
        first_id=word1.id,
        second_id=word2.id
    )
    dbsession.add(pair)
    dbsession.commit()

    reply1 = Reply(
        pair_id=pair.id,
        word_id=word1.id,
        count=1
    )
    reply2 = Reply(
        pair_id=pair.id,
        word_id=word2.id,
        count=2
    )
    dbsession.add_all([reply1, reply2])
    dbsession.commit()

    dbsession.refresh(chat)
    dbsession.refresh(pair)

    assert len(chat.pairs) == 1
    assert pair.first_word.word == 'alpha'
    assert pair.second_word.word == 'beta'
    assert len(pair.replies) == 2
