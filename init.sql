CREATE TABLE IF NOT EXISTS chats(
    id SERIAL PRIMARY KEY NOT NULL,
    telegram_id bigint NOT NULL,
    chat_type smallint NOT NULL,
    random_chance smallint DEFAULT 5 NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying
);

CREATE INDEX IF NOT EXISTS index_chats_on_telegram_id ON chats USING btree (telegram_id);

CREATE TABLE IF NOT EXISTS pairs (
    id SERIAL PRIMARY KEY NOT NULL,
    chat_id integer NOT NULL,
    first_id integer,
    second_id integer,
    created_at timestamp without time zone NOT NULL
);

CREATE INDEX IF NOT EXISTS index_pairs_on_chat_id ON pairs USING btree (chat_id);
CREATE INDEX IF NOT EXISTS index_pairs_on_first_id ON pairs USING btree (first_id);
CREATE INDEX IF NOT EXISTS index_pairs_on_second_id ON pairs USING btree (second_id);
CREATE UNIQUE INDEX IF NOT EXISTS unique_pair_chat_id_first_id ON pairs USING btree (chat_id, first_id) WHERE (second_id IS NULL);
CREATE UNIQUE INDEX IF NOT EXISTS unique_pair_chat_id_first_id_second_id ON pairs USING btree (chat_id, first_id, second_id);
CREATE UNIQUE INDEX IF NOT EXISTS unique_pair_chat_id_second_id ON pairs USING btree (chat_id, second_id) WHERE (first_id IS NULL);

CREATE TABLE IF NOT EXISTS replies (
    id SERIAL PRIMARY KEY NOT NULL,
    pair_id integer NOT NULL,
    word_id integer,
    count bigint DEFAULT 1 NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS unique_reply_pair_id ON replies USING btree (pair_id) WHERE (word_id IS NULL);
CREATE UNIQUE INDEX IF NOT EXISTS unique_reply_pair_id_word_id ON replies USING btree (pair_id, word_id);

CREATE TABLE IF NOT EXISTS words (
    id SERIAL PRIMARY KEY NOT NULL,
    word character varying NOT NULL
);

CREATE INDEX IF NOT EXISTS index_words_on_word ON words USING btree (word);

ALTER TABLE pairs DROP CONSTRAINT IF EXISTS first_id_fk;
ALTER TABLE pairs ADD CONSTRAINT first_id_fk FOREIGN KEY (first_id) REFERENCES words ON DELETE CASCADE;
ALTER TABLE pairs DROP CONSTRAINT IF EXISTS second_id_fk;
ALTER TABLE pairs ADD CONSTRAINT second_id_fk FOREIGN KEY (second_id) REFERENCES words ON DELETE CASCADE;
ALTER TABLE replies DROP CONSTRAINT IF EXISTS word_id_fk;
ALTER TABLE replies ADD CONSTRAINT word_id_fk FOREIGN KEY (word_id) REFERENCES words ON DELETE CASCADE;

CREATE UNIQUE INDEX IF NOT EXISTS unique_word_word ON words USING btree(word);

ALTER TABLE replies DROP CONSTRAINT IF EXISTS pair_id_fk;
ALTER TABLE replies ADD CONSTRAINT pair_id_fk FOREIGN KEY (pair_id) REFERENCES pairs ON DELETE CASCADE;

ALTER TABLE pairs DROP CONSTRAINT IF EXISTS chat_id_fk;
ALTER TABLE pairs ADD CONSTRAINT chat_id_fk FOREIGN KEY (chat_id) REFERENCES chats ON DELETE CASCADE;

ALTER TABLE pairs ADD COLUMN IF NOT EXISTS updated_at timestamp without time zone;
UPDATE pairs SET updated_at = now() WHERE updated_at IS NULL;
ALTER TABLE pairs ALTER COLUMN updated_at SET NOT NULL;

CREATE TABLE IF NOT EXISTS subscriptions(
    id SERIAL PRIMARY KEY NOT NULL,
    chat_id bigint NOT NULL,
    name character varying NOT NULL,
    since_id bigint
);

ALTER TABLE chats ADD COLUMN IF NOT EXISTS repost_chat_username character varying;
