import logging
from typing import Type
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.error import TelegramError
from sqlalchemy.orm import Session
from bot.handlers.generic_handler import GenericHandler
from bot.handlers import (
    cool_story_handler, get_gab_handler, get_repost_chat_handler, 
    get_stats_handler, message_handler, ping_handler, repost_handler, set_gab_handler, set_repost_chat_handler)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Router:
    def __init__(self, bot_token, session: Session):
        self.application = Application.builder().token(bot_token).build()
        self.session = session
        self._add_handlers()

    def _add_handlers(self):
        command_handlers = {
            "repost": self.repost,
            "get_stats": self.get_stats,
            "cool_story": self.cool_story,
            "set_gab": self.set_gab,
            "get_gab": self.get_gab,
            "ping": self.ping,
            "set_repost_channel": self.set_repost_channel,
            "get_repost_channel": self.get_repost_channel
        }

        for command, handler in command_handlers.items():
            self.application.add_handler(CommandHandler(command, handler))

        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def _send_response(self, context: CallbackContext, chat_id: int, response: str, reply_to_message_id=None):
        if response:
            await context.bot.send_message(chat_id=chat_id, text=response, reply_to_message_id=reply_to_message_id)

    async def repost(self, update: Update, context: CallbackContext):
        await self._handle_command(update, context, repost_handler.RepostHandler)

    async def get_stats(self, update: Update, context: CallbackContext):
        await self._handle_command(update, context, get_stats_handler.GetStatsHandler)

    async def cool_story(self, update: Update, context: CallbackContext):
        await self._handle_command(update, context, cool_story_handler.CoolStoryHandler)

    async def set_gab(self, update: Update, context: CallbackContext):
        logger.debug("Handling /set_gab command")
        msg = update.message
        args = context.args
        if msg and args:
            try:
                level = int(args[0])
                handler = set_gab_handler.SetGabHandler(update, self.session)
                response = handler.call(level)
                if response:
                    await self._send_response(context, msg.chat_id, response)
            except (IndexError, ValueError):
                logger.error("Invalid arguments for /set_gab command")
                await self._send_response(context, msg.chat_id, "Usage: /set_gab <level>")

    async def get_gab(self, update: Update, context: CallbackContext):
        await self._handle_command(update, context, get_gab_handler.GetGabHandler)

    async def ping(self, update: Update, context: CallbackContext):
        await self._handle_command(update, context, ping_handler.PingHandler)

    async def set_repost_channel(self, update: Update, context: CallbackContext):
        logger.debug("Handling /set_repost_channel command")
        msg = update.message
        if not msg:
            return

        chat_username = next((msg.text[entity.offset:entity.offset + entity.length]
                              for entity in msg.entities if entity.type == "mention" and msg.text), None)
        chat_member_request = await context.bot.get_chat_member(msg.chat.id, msg.from_user.id) if msg.from_user else None

        if chat_username and msg.chat_id:
            handler = set_repost_chat_handler.SetRepostChatHandler(update, chat_member_request, self.session)
            response = handler.call(chat_username)
            if response:
                await self._send_response(context, msg.chat_id, response)
        else:
            logger.error("No chat username found or message chat_id is None")
            await self._send_response(context, msg.chat_id, "No chat username found")

    async def get_repost_channel(self, update: Update, context: CallbackContext):
        await self._handle_command(update, context, get_repost_chat_handler.GetRepostChatHandler)

    async def handle_message(self, update: Update, context: CallbackContext):
        logger.debug("Handling incoming message")
        handler = message_handler.MessageHandler(update, self.session)
        response = handler.call()
        msg = update.message
        if msg:
            try:
                if response and isinstance(response, tuple):
                    left, right = response
                    if left:
                        await self._send_response(context, msg.chat_id, left, reply_to_message_id=msg.message_id)
                    if right:
                        await self._send_response(context, msg.chat_id, right)
                elif response:
                    await self._send_response(context, msg.chat_id, response)
            except TelegramError as e:
                logger.error(f"TelegramError: {e}")
            except Exception as e:
                logger.exception("Unexpected error")

    async def _handle_command(self, update: Update, context: CallbackContext, handler_class: Type[GenericHandler]):
        logger.debug(f"Handling {handler_class.__name__} command")
        handler = handler_class(update, self.session)
        response = handler.call()
        msg = update.message
        if response and msg:
            await self._send_response(context, msg.chat_id, response)

    def run(self):
        logger.info("Bot started. Press Ctrl+C to stop.")
        self.application.run_polling(stop_signals=None)
