# 🎮 Угадай число — веб-игра на Flask

Веб-версия классической игры "Угадай число" с тремя режимами, искусственным интеллектом, звуками и **базой данных PostgreSQL**.

## ✨ Особенности

- 🎯 **Классический режим** — угадай число компьютера
- 🤖 **ИИ угадывает** — загадай число, а компьютер отгадает
- 📊 **Рекорды в PostgreSQL** — сохраняются навсегда, не сбрасываются при деплое
- 🔐 **Регистрация и логин** — каждый игрок со своей статистикой
- 🔊 **Звуковые эффекты** — через Web Audio API
- 🎚️ **Регулировка громкости**
- 📱 **Адаптивный дизайн** — работает на телефонах

## 🛠 Технологии

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Звуки:** Web Audio API
- **База данных:** PostgreSQL
- **Контейнеризация:** Docker
- **Деплой:** Render.com

## 🚀 Быстрый старт

### 📍 Локальный запуск

```bash
git clone https://github.com/brkotb/guess-game.git
cd guess-game
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## 🐳 Запуск через Docker
```bash
docker run -d -p 10000:10000 -e DATABASE_URL="postgresql://user:pass@host/db" guess-game
Открой в браузере: http://localhost:10000
```
Важно: Замени DATABASE_URL="postgresql://user:pass@host/db" на реальную строку подключения к твоей базе данных PostgreSQL. Её можно найти в настройках твоего сервиса на Render.

## 📁 Структура проекта

```
guess-game/
├── app.py              # Главный Flask-сервер
├── fastapi_app.py      # Экспериментальная версия на FastAPI
├── requirements.txt    # Зависимости
├── Dockerfile          # Инструкция для сборки Docker-образа
├── .dockerignore       # Файлы, которые не попадают в образ
├── templates/
│   └── index.html
├── static/
│   └── sounds.js
└── README.md           # Этот файл
```

## 👤 Автор
**brkotb**

## ⭐ Поддержка проекта
Если понравился проект, поставь звезду на GitHub — это помогает другим найти игру.

## 🔗 Ссылки
GitHub репозиторий: github.com/brkotb/guess-game

Сайт в интернете: guess-game-27b5.onrender.com
