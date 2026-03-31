"""

tg_bot.py — Управление ботом через Telegram (минимальная версия)

"""



from __future__ import annotations



import random

import warnings

from datetime import datetime, timezone

from typing import Optional



from telegram.warnings import PTBUserWarning



warnings.filterwarnings("ignore", category=PTBUserWarning)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from telegram.ext import (

    Application,

    CallbackQueryHandler,

    CommandHandler,

    ContextTypes,

    ConversationHandler,

    MessageHandler,

    filters,

)



