#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Авто режим без зависимостей шифрования
"""
import asyncio
import time
import random
import json
import os
import sqlite3
from datetime import datetime

def log(msg):
    timestamp = datetime.now().strftime("[%H:%M]")
    print(f"{timestamp} {msg}")

class SimpleDB:
    """Простая база данных без зависимостей"""
    def __init__(self):
        self.db_path = "simple_bot.db"
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                username TEXT,
                auth_token TEXT,
                ct0 TEXT,
                proxy_id INTEGER
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                account_id INTEGER,
                key TEXT,
                value TEXT,
                PRIMARY KEY (account_id, key)
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_accounts(self):
        conn = sqlite3.connect(self.db_path)
        accounts = conn.execute("SELECT * FROM accounts").fetchall()
        conn.close()
        return [{"id": row[0], "username": row[1], "auth_token": row[2], "ct0": row[3], "proxy_id": row[4]} for row in accounts]
    
    def get_account(self, account_id):
        conn = sqlite3.connect(self.db_path)
        account = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
        conn.close()
        if account:
            return {"id": account[0], "username": account[1], "auth_token": account[2], "ct0": account[3], "proxy_id": account[4]}
        return None
    
    def get_settings(self, account_id):
        conn = sqlite3.connect(self.db_path)
        settings = conn.execute("SELECT key, value FROM settings WHERE account_id = ?", (account_id,)).fetchall()
        conn.close()
        return {row[0]: row[1] for row in settings}
    
    def set_setting(self, account_id, key, value):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT OR REPLACE INTO settings (account_id, key, value) VALUES (?, ?, ?)
        ''', (account_id, key, value))
        conn.commit()
        conn.close()

class MockTwitterClient:
    """Имитация Twitter клиента для демонстрации"""
    def __init__(self, account_id, auth_token, ct0, proxy=None):
        self.account_id = account_id
        self.auth_token = auth_token
        self.ct0 = ct0
        self.proxy = proxy
    
    async def verify_session(self):
        """Проверка сессии"""
        await asyncio.sleep(0.5)
        return f"mock_user_{self.account_id}"
    
    async def search_tweets(self, query, min_likes=0, min_retweets=0, max_age_minutes=0, lang="en", limit=20):
        """Поиск твитов"""
        await asyncio.sleep(1)
        
        # Имитация найденных твитов
        tweets = []
        users = ["@crypto_trader", "@bitcoin_whale", "@defi_master", "@nft_collector", "@token_analyst"]
        texts = [
            f"Bitcoin is looking strong today! {query}",
            f"Ethereum update coming soon {query}",
            f"DeFi protocols showing growth {query}",
            f"NFT market is heating up {query}",
            f"Trading opportunities in crypto {query}"
        ]
        
        for i in range(random.randint(3, 8)):
            tweet = {
                'id': f"mock_{random.randint(1000000, 9999999)}",
                'author_username': random.choice(users),
                'author_followers': random.randint(100, 10000),
                'text': random.choice(texts),
                'likes': random.randint(10, 1000),
                'retweets': random.randint(5, 500)
            }
            tweets.append(tweet)
        
        return tweets
    
    async def post_reply(self, reply_text, tweet_id, post_url):
        """Отправка ответа"""
        await asyncio.sleep(2)
        return f"mock_reply_{random.randint(100000, 999999)}"
    
    async def like_tweet(self, tweet_id):
        """Лайк твита"""
        await asyncio.sleep(0.5)
        return random.random() > 0.1  # 90% успеха
    
    async def bookmark_tweet(self, tweet_id):
        """Добавление в закладки"""
        await asyncio.sleep(0.5)
        return random.random() > 0.15  # 85% успеха
    
    async def visit_profile(self, username):
        """Посещение профиля"""
        await asyncio.sleep(0.5)
        return random.random() > 0.2  # 80% успеха

class AutoModeBot:
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.running = False
        self.session_comments = 0
        self.db = SimpleDB()
        
    async def get_settings(self):
        """Получение настроек"""
        try:
            settings = self.db.get_settings(self.account_id)
            return {
                'comments_per_session': int(settings.get('comments_per_session', 0)),
                'custom_delay': int(settings.get('custom_delay', 300)),
                'like_after_comment': settings.get('like_after_comment', 'False') == 'True',
                'bookmark_after_comment': settings.get('bookmark_after_comment', 'False') == 'True',
                'visit_profile_after_comment': settings.get('visit_profile_after_comment', 'False') == 'True',
                'lang_filter': settings.get('lang_filter', 'en'),
                'min_followers': int(settings.get('min_followers', 0))
            }
        except:
            return {
                'comments_per_session': 0,
                'custom_delay': 300,
                'like_after_comment': True,
                'bookmark_after_comment': True,
                'visit_profile_after_comment': False,
                'lang_filter': 'en',
                'min_followers': 0
            }
    
    async def get_keywords(self):
        """Получение ключевых слов"""
        # Для демонстрации используем стандартные слова
        return ['крипта', 'bitcoin', 'ethereum', 'defi', 'nft', 'trading']
    
    async def run_auto_cycle(self):
        """Один полный цикл работы"""
        try:
            # Получаем настройки
            settings = await self.get_settings()
            
            # Получаем аккаунт
            account = self.db.get_account(self.account_id)
            if not account:
                log(f"Аккаунт {self.account_id} не найден")
                return False
            
            # Создаем клиент
            client = MockTwitterClient(
                account_id=self.account_id,
                auth_token=account['auth_token'],
                ct0=account['ct0']
            )
            
            # Проверяем сессию
            username = await client.verify_session()
            if not username:
                log("Сессия недействительна")
                return False
            
            log(f"Сессия подтверждена: @{username}")
            
            # Ищем посты
            keywords = await self.get_keywords()
            keyword = random.choice(keywords)
            log(f"Поиск постов по ключевому слову \"{keyword}\"")
            
            tweets = await client.search_tweets(
                query=keyword,
                min_likes=0,
                min_retweets=0,
                max_age_minutes=0,
                lang=settings['lang_filter'],
                limit=20
            )
            
            if not tweets:
                log("Посты не найдены")
                return True
            
            # Выбираем лучший пост
            best_tweet = max(tweets, key=lambda t: t['likes'])
            
            # Проверяем фильтр подписчиков
            if settings['min_followers'] > 0 and best_tweet['author_followers'] < settings['min_followers']:
                log(f"Пост от @{best_tweet['author_username']} пропущен (мало подписчиков: {best_tweet['author_followers']})")
                return True
            
            # Генерируем комментарий
            log(f"Найден пост от @{best_tweet['author_username']} ({best_tweet['author_followers']} подписчиков)")
            
            # Имитация генерации ответа
            await asyncio.sleep(1)
            reply_text = f"Interesting point about {keyword}! Thanks for sharing."
            
            # Отправляем комментарий
            post_url = f"https://x.com/{best_tweet['author_username']}/status/{best_tweet['id']}"
            new_id = await client.post_reply(reply_text, best_tweet['id'], post_url)
            
            if new_id:
                self.session_comments += 1
                log(f"Комментарий отправлен → ID: {new_id}")
                
                # Выполняем дополнительные действия
                actions = []
                
                if settings['like_after_comment']:
                    await asyncio.sleep(random.uniform(0.5, 1))
                    success = await client.like_tweet(best_tweet['id'])
                    actions.append("❤️ лайк поставлен" if success else "❌ лайк не поставлен")
                
                if settings['bookmark_after_comment']:
                    await asyncio.sleep(random.uniform(0.5, 1))
                    success = await client.bookmark_tweet(best_tweet['id'])
                    actions.append("🔖 закладка добавлена" if success else "❌ закладка не добавлена")
                
                if settings['visit_profile_after_comment']:
                    await asyncio.sleep(random.uniform(0.5, 1))
                    success = await client.visit_profile(best_tweet['author_username'])
                    actions.append("👤 переход в профиль" if success else "❌ профиль не посещен")
                
                if actions:
                    log(f"🎯 Доп. действия: {' → '.join(actions)}")
                
                return True
            else:
                log("Не удалось отправить комментарий")
                return False
        
        except Exception as e:
            log(f"Ошибка цикла: {e}")
            return False
    
    async def run_auto_mode(self):
        """Основной цикл авто режима"""
        self.running = True
        self.session_comments = 0
        
        log("🚀 Бот запущен. Авто режим активирован")
        
        try:
            while self.running:
                # Проверяем лимит комментариев
                settings = await self.get_settings()
                if settings and settings['comments_per_session'] > 0:
                    if self.session_comments >= settings['comments_per_session']:
                        log(f"🏁 Достигнут лимит комментариев ({self.session_comments}/{settings['comments_per_session']})")
                        break
                
                # Выполняем цикл
                success = await self.run_auto_cycle()
                
                if not self.running:
                    break
                
                # Задержка между циклами
                if settings:
                    delay = min(30, settings['custom_delay'])  # Для теста максимум 30 секунд
                    log(f"⏳ Ожидание {delay} секунд...")
                    
                    for i in range(delay, 0, -1):
                        if not self.running:
                            break
                        await asyncio.sleep(1)
                else:
                    await asyncio.sleep(10)
        
        except KeyboardInterrupt:
            log("\n⏹️ Остановлено пользователем")
        except Exception as e:
            log(f"❌ Критическая ошибка: {e}")
        finally:
            self.running = False
            log(f"🛑 Авто режим завершен. Комментарий отправлено: {self.session_comments}")

async def main():
    print("🤖 Twitter Bot - Автоматический режим (Без зависимостей)")
    print("="*60)
    
    # Создаем тестовый аккаунт если его нет
    db = SimpleDB()
    accounts = db.get_accounts()
    
    if not accounts:
        log("Создаем тестовый аккаунт...")
        conn = sqlite3.connect("simple_bot.db")
        conn.execute('''
            INSERT INTO accounts (id, username, auth_token, ct0) VALUES (?, ?, ?, ?)
        ''', (1, "test_user", "mock_token", "mock_ct0"))
        conn.commit()
        conn.close()
        accounts = db.get_accounts()
    
    print("📋 Доступные аккаунты:")
    for i, acc in enumerate(accounts, 1):
        print(f"   {i}. ID: {acc['id']} - @{acc.get('username', 'Unknown')}")
    
    try:
        choice = input("\n🔢 Выберите аккаунт (номер): ").strip()
        if not choice.isdigit():
            print("❌ Неверный выбор")
            return
        
        account_id = accounts[int(choice) - 1]['id']
        
        # Устанавливаем настройки по умолчанию
        db.set_setting(account_id, 'comments_per_session', '0')
        db.set_setting(account_id, 'custom_delay', '300')
        db.set_setting(account_id, 'like_after_comment', 'True')
        db.set_setting(account_id, 'bookmark_after_comment', 'True')
        db.set_setting(account_id, 'visit_profile_after_comment', 'False')
        db.set_setting(account_id, 'lang_filter', 'en')
        db.set_setting(account_id, 'min_followers', '0')
        
        # Создаем и запускаем бота
        bot = AutoModeBot(account_id)
        
        print("\n🚀 Запуск авто режима...")
        print("💡 Нажмите Ctrl+C для остановки")
        print("="*60)
        
        await bot.run_auto_mode()
    
    except KeyboardInterrupt:
        print("\n⏹️ Остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Программа завершена")
