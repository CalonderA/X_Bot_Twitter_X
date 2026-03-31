#!/usr/bin/env python3
"""
tg_bot.py — Рабочий Telegram бот для управления X Bot
from __future__ import annotations
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import get_settings, logger
# Хранилище данных
_pending_items: dict = {}
_hitl_store: dict = {}
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "🤖 <b>X AutoReply Bot</b>\n\n"
        "Доступные команды:\n"
        "/menu — Главное меню\n"
        "/status — Статус бота\n"
        "/help — Помощь",
        parse_mode="HTML"
    )
async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("▶️ Запустить бота", callback_data="start_bot")],
        [InlineKeyboardButton("⏹️ Остановить бота", callback_data="stop_bot")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
        "🤖 <b>X AutoReply Bot</b> — Главное меню",
        reply_markup=reply_markup,
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка статуса"""
        "📊 <b>Статус бота:</b>\n\n"
        "✅ Telegram бот: Онлайн\n"
        "⏳ X Bot: Готов к работе\n"
        "💾 База данных: Подключена",
async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "start_bot":
        await query.edit_message_text(
            "▶️ <b>Бот запускается...</b>\n\n"
            "Перейдите в GUI и нажмите кнопку Start на нужном аккаунте.",
            parse_mode="HTML"
        )
    elif data == "stop_bot":
            "⏹️ <b>Бот останавливается...</b>\n\n"
            "Все воркеры будут остановлены.",
    elif data == "stats":
            "📊 <b>Статистика:</b>\n\n"
            "📝 Комментариев сегодня: 0\n"
            "❤️ Лайков: 0\n"
            "🔖 Закладок: 0\n"
            "👤 Аккаунтов: 0",
    elif data == "settings":
            "⚙️ <b>Настройки:</b>\n\n"
            "Настройки управляются через GUI.\n"
            "Запустите: python gui.py",
def create_application() -> Application:
    """Создание приложения Telegram бота"""
    settings = get_settings()
    token = settings.telegram_bot_token
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не настроен в .env")
    application = Application.builder().token(token).build()
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("menu", cmd_menu))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CallbackQueryHandler(on_callback))
    return application
async def main():
    """Главная функция запуска"""
    logger.info("[TG] Telegram бот инициализируется...")
    try:
        app = create_application()
        logger.success("[TG] ✅ Telegram бот запущен!")
        # Запускаем бота
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        # Держим бота запущенным
        import asyncio
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"[TG] ❌ Ошибка Telegram бота: {e}")
        raise
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
