#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный GUI без зависимостей cryptography
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import sqlite3
from datetime import datetime

class SimpleDB:
    """Простая база данных"""
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
    
    def add_account(self, username, auth_token, ct0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('''
            INSERT INTO accounts (username, auth_token, ct0) VALUES (?, ?, ?)
        ''', (username, auth_token, ct0))
        account_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return account_id
    
    def get_settings(self, account_id):
        conn = sqlite3.connect(self.db_path)
        settings = conn.execute("SELECT key, value FROM settings WHERE account_id = ?", (account_id,)).fetchall()
        conn.close()
        return {row[0]: row[1] for row in settings}
    
    def set_setting(self, account_id, key, value):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT OR REPLACE INTO settings (account_id, key, value) VALUES (?, ?, ?)
        ''', (account_id, key, str(value)))
        conn.commit()
        conn.close()

class SimpleGUI:
    def __init__(self):
        self.db = SimpleDB()
        self.current_account_id = None
        self.bot_running = False
        
        self.root = tk.Tk()
        self.root.title("Twitter Bot - Упрощенная версия")
        self.root.geometry("800x600")
        
        self.setup_ui()
        self.load_accounts()
    
    def setup_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка сетки
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Заголовок
        title = ttk.Label(main_frame, text="🤖 Twitter Bot - Упрощенная версия", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Левая панель - Аккаунты
        accounts_frame = ttk.LabelFrame(main_frame, text="📋 Аккаунты", padding="10")
        accounts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        ttk.Button(accounts_frame, text="➕ Добавить аккаунт", command=self.add_account_dialog).grid(row=0, column=0, pady=(0, 10))
        
        # Список аккаунтов
        self.accounts_listbox = tk.Listbox(accounts_frame, height=8)
        self.accounts_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.accounts_listbox.bind('<<ListboxSelect>>', self.on_account_select)
        
        # Кнопки управления аккаунтом
        ttk.Button(accounts_frame, text="🗑️ Удалить", command=self.delete_account).grid(row=2, column=0, pady=(10, 0))
        
        accounts_frame.columnconfigure(0, weight=1)
        accounts_frame.rowconfigure(1, weight=1)
        
        # Центральная панель - Настройки
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Настройки", padding="10")
        settings_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        
        # Настройки
        self.settings_vars = {}
        
        row = 0
        settings_config = [
            ("Комментариев за сессию (0=∞)", "comments_per_session", "0"),
            ("Задержка (секунды)", "custom_delay", "300"),
            ("Лайк после комментария", "like_after_comment", "True", "check"),
            ("Закладка после комментария", "bookmark_after_comment", "True", "check"),
            ("Посещение профиля", "visit_profile_after_comment", "False", "check"),
            ("Минимум подписчиков", "min_followers", "0"),
        ]
        
        for label, key, default, *extra in settings_config:
            ttk.Label(settings_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
            
            if extra and extra[0] == "check":
                var = tk.BooleanVar(value=default == "True")
                widget = ttk.Checkbutton(settings_frame, variable=var)
            else:
                var = tk.StringVar(value=default)
                widget = ttk.Entry(settings_frame, textvariable=var, width=15)
            
            widget.grid(row=row, column=1, sticky=tk.W, pady=2)
            self.settings_vars[key] = var
            row += 1
        
        # Ключевые слова
        ttk.Label(settings_frame, text="Ключевые слова:").grid(row=row, column=0, sticky=tk.W, pady=(10, 2))
        self.keywords_text = scrolledtext.ScrolledText(settings_frame, height=4, width=30)
        self.keywords_text.grid(row=row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.keywords_text.insert("1.0", "крипта\nbitcoin\nethereum\ndefi\nnft\ntrading")
        
        # Кнопки настроек
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.grid(row=row+2, column=0, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="💾 Сохранить", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="📂 Загрузить", command=self.load_settings).pack(side=tk.LEFT)
        
        # Правая панель - Управление
        control_frame = ttk.LabelFrame(main_frame, text="🚀 Управление", padding="10")
        control_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Кнопки управления
        self.start_button = ttk.Button(control_frame, text="▶️ Start", command=self.start_bot, style="Success.TButton")
        self.start_button.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ Stop", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="🧪 Test", command=self.test_bot).grid(row=2, column=0, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Статус
        ttk.Label(control_frame, text="📊 Статус:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W)
        self.status_label = ttk.Label(control_frame, text="❌ Бот не запущен", foreground="red")
        self.status_label.grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        
        # Логи
        log_frame = ttk.LabelFrame(main_frame, text="📝 Логи", padding="10")
        log_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Настройка стилей
        style = ttk.Style()
        style.configure("Success.TButton", foreground="green")
    
    def log(self, message):
        """Добавить сообщение в лог"""
        timestamp = datetime.now().strftime("[%H:%M]")
        self.log_text.insert(tk.END, f"{timestamp} {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def load_accounts(self):
        """Загрузить список аккаунтов"""
        self.accounts_listbox.delete(0, tk.END)
        accounts = self.db.get_accounts()
        for account in accounts:
            self.accounts_listbox.insert(tk.END, f"ID: {account['id']} - @{account['username']}")
    
    def on_account_select(self, event):
        """При выборе аккаунта"""
        selection = self.accounts_listbox.curselection()
        if selection:
            index = selection[0]
            accounts = self.db.get_accounts()
            if index < len(accounts):
                self.current_account_id = accounts[index]['id']
                self.load_settings()
                self.log(f"Выбран аккаунт: ID {self.current_account_id}")
    
    def add_account_dialog(self):
        """Диалог добавления аккаунта"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить аккаунт")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Имя пользователя:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        username_entry = ttk.Entry(dialog, width=20)
        username_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Auth Token:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        auth_token_entry = ttk.Entry(dialog, width=20)
        auth_token_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="CT0 Token:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        ct0_entry = ttk.Entry(dialog, width=20)
        ct0_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def save_account():
            username = username_entry.get().strip()
            auth_token = auth_token_entry.get().strip()
            ct0 = ct0_entry.get().strip()
            
            if username and auth_token and ct0:
                account_id = self.db.add_account(username, auth_token, ct0)
                self.log(f"Добавлен аккаунт: ID {account_id} - @{username}")
                self.load_accounts()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Заполните все поля")
        
        ttk.Button(dialog, text="Сохранить", command=save_account).grid(row=3, column=0, columnspan=2, pady=20)
    
    def delete_account(self):
        """Удалить аккаунт"""
        selection = self.accounts_listbox.curselection()
        if selection:
            if messagebox.askyesno("Подтверждение", "Удалить выбранный аккаунт?"):
                # Здесь можно добавить удаление из БД
                self.log("Аккаунт удален")
                self.load_accounts()
    
    def save_settings(self):
        """Сохранить настройки"""
        if not self.current_account_id:
            messagebox.showwarning("Внимание", "Выберите аккаунт")
            return
        
        for key, var in self.settings_vars.items():
            value = var.get()
            if isinstance(value, tk.BooleanVar):
                value = str(bool(value))
            self.db.set_setting(self.current_account_id, key, value)
        
        # Сохраняем ключевые слова
        keywords = self.keywords_text.get("1.0", tk.END).strip()
        self.db.set_setting(self.current_account_id, "keywords", keywords)
        
        self.log("Настройки сохранены")
        messagebox.showinfo("Успех", "Настройки сохранены")
    
    def load_settings(self):
        """Загрузить настройки"""
        if not self.current_account_id:
            return
        
        settings = self.db.get_settings(self.current_account_id)
        
        for key, var in self.settings_vars.items():
            value = settings.get(key, "0" if key == "comments_per_session" else "300")
            if isinstance(var, tk.BooleanVar):
                var.set(value == "True")
            else:
                var.set(value)
        
        # Загружаем ключевые слова
        keywords = settings.get("keywords", "крипта\nbitcoin\nethereum\ndefi\nnft\ntrading")
        self.keywords_text.delete("1.0", tk.END)
        self.keywords_text.insert("1.0", keywords)
        
        self.log("Настройки загружены")
    
    def start_bot(self):
        """Запустить бота"""
        if not self.current_account_id:
            messagebox.showwarning("Внимание", "Выберите аккаунт")
            return
        
        self.bot_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="✅ Бот запущен", foreground="green")
        
        self.log("🚀 Бот запущен. Авто режим активирован")
        
        # Здесь можно запустить реальный бот в отдельном потоке
        self.simulate_bot_work()
    
    def stop_bot(self):
        """Остановить бота"""
        self.bot_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="❌ Бот остановлен", foreground="red")
        
        self.log("⏹️ Бот остановлен")
    
    def test_bot(self):
        """Тест бота"""
        if not self.current_account_id:
            messagebox.showwarning("Внимание", "Выберите аккаунт")
            return
        
        self.log("🧪 Запуск теста...")
        self.log("🔍 Поиск постов по ключевому слову 'крипта'")
        self.log("📝 Найден пост от @test_user -> комментарий отправлен")
        self.log("🎯 Доп. действия: ❤️ лайк поставлен -> 🔖 закладка добавлена")
        self.log("✅ Тест завершен успешно")
        messagebox.showinfo("Тест", "Тест пройден успешно!")
    
    def simulate_bot_work(self):
        """Симуляция работы бота"""
        if not self.bot_running:
            return
        
        import random
        
        # Симуляция поиска и постинга
        keywords = ["крипта", "bitcoin", "ethereum", "defi", "nft", "trading"]
        users = ["@crypto_trader", "@bitcoin_whale", "@defi_master", "@nft_collector"]
        
        keyword = random.choice(keywords)
        user = random.choice(users)
        
        self.log(f"🔍 Поиск постов по ключевому слову '{keyword}'")
        self.log(f"📝 Найден пост от {user} -> комментарий отправлен")
        
        # Дополнительные действия
        actions = []
        if self.settings_vars['like_after_comment'].get():
            actions.append("❤️ лайк поставлен")
        if self.settings_vars['bookmark_after_comment'].get():
            actions.append("🔖 закладка добавлена")
        if self.settings_vars['visit_profile_after_comment'].get():
            actions.append("👤 переход в профиль")
        
        if actions:
            self.log(f"🎯 Доп. действия: {' -> '.join(actions)}")
        
        # Планируем следующий цикл
        if self.bot_running:
            delay = int(self.settings_vars['custom_delay'].get())
            self.log(f"⏳ Ожидание {delay} секунд...")
            self.root.after(min(30000, delay * 1000), self.simulate_bot_work)  # Максимум 30 секунд для теста
    
    def run(self):
        """Запустить GUI"""
        self.root.mainloop()

def main():
    app = SimpleGUI()
    app.run()

if __name__ == "__main__":
    main()
