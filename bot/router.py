"""
Router module for handling Telegram bot commands and messages.

This module initializes the Telegram bot application, sets up command and message handlers,
and defines the Router class responsible for processing incoming updates and routing them
to the appropriate handlers.
"""

import logging
from typing import Optional, Type
from telegram import Document, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.error import TelegramError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from bot.handlers.generic_handler import GenericHandler
from bot.handlers import (
    cool_story_handler, get_gab_handler,
    get_stats_handler, message_handler, ping_handler,
    set_gab_handler, learn_handler)
from config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Router:
    """Router class for handling Telegram bot commands and messages."""

    def __init__(self, config: Config, session: Session):
        self.application = Application.builder().token(config.bot.token).build()
        self.session = session
        self.config = config
        self._add_handlers()

    def _add_handlers(self):
        """Add command and message handlers to the bot application."""
        command_handlers = {
            "get_stats": get_stats_handler.GetStatsHandler,
            "cool_story": cool_story_handler.CoolStoryHandler,
            "set_gab": self.set_gab,
            "get_gab": get_gab_handler.GetGabHandler,
            "ping": ping_handler.PingHandler,
            "learn": self.learn
        }

        for command, handler in command_handlers.items():
            self.application.add_handler(CommandHandler(
                command, self._create_command_handler(handler)))

        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(
            filters.Document.ALL & filters.CaptionRegex(r'/learn'), self.learn))

    def _create_command_handler(self, handler_class: Type[GenericHandler]):
        """Create a command handler for a given handler class."""
        async def command_handler(update: Update, context: CallbackContext):
            await self._handle_command(update, context, handler_class)
        return command_handler

    async def _send_response(self, context: CallbackContext, chat_id: int,
                             response: str, reply_to_message_id=None):
        """Send a response message to the user."""
        if response:
            await context.bot.send_message(
                chat_id=chat_id, text=response, reply_to_message_id=reply_to_message_id)

    async def _handle_command(self, update: Update, context: CallbackContext,
                              handler_class: Type[GenericHandler],
                              document: Optional[Document] = None):
        """Handle commands using the specified handler class."""
        logger.debug("Handling %s command", handler_class.__name__)
        handler = (
            handler_class(update, self.session, self.config,
                          document)  # type: ignore
            if handler_class == learn_handler.LearnHandler
            else handler_class(update, self.session, self.config)
        )
        response = await handler.call()
        msg = update.message
        if response and msg:
            await self._send_response(
                context, msg.chat_id, response, reply_to_message_id=msg.message_id)

    async def learn(self, update: Update, context: CallbackContext):
        """Handle the /learn command."""
        document = update.message.document if update.message else None
        await self._handle_command(update, context, learn_handler.LearnHandler, document=document)

    async def set_gab(self, update: Update, context: CallbackContext):
        """Handle the /set_gab command."""
        logger.debug("Handling /set_gab command")
        msg = update.message
        args = context.args
        if msg and args:
            try:
                level = int(args[0])
                handler = set_gab_handler.SetGabHandler(
                    update, self.session, self.config)
                response = await handler.call(level)
                if response:
                    await self._send_response(context, msg.chat_id, response)
            except (IndexError, ValueError):
                logger.error("Invalid arguments for /set_gab command")
                await self._send_response(context, msg.chat_id, "Usage: /set_gab <level>")

    async def handle_message(self, update: Update, context: CallbackContext):
        """Handle incoming messages."""
        logger.debug("Handling incoming message")
        handler = message_handler.MessageHandler(
            update, self.session, self.config)
        response = await handler.call()
        msg = update.message
        if msg:
            try:
                if response:
                    if isinstance(response, tuple):
                        left, right = response
                        if left:
                            await self._send_response(context, msg.chat_id, left, msg.message_id)
                        if right:
                            await self._send_response(context, msg.chat_id, right)
                    else:
                        await self._send_response(context, msg.chat_id, response)
            except TelegramError as e:
                logger.error("TelegramError: %s", e)
            except (ValueError, KeyError, AttributeError, TypeError, OperationalError) as e:
                logger.exception("Unexpected specific Exception: %s", e)

    def run(self):
        """Start the bot and run it."""
        logger.info("Bot started. Press Ctrl+C to stop.")
        self.application.run_polling(stop_signals=None)
