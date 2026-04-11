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
- **Деплой:** Render.com

## 🚀 Быстрый старт

```bash
git clone https://github.com/brkotb/guess-game.git
cd guess-game
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py

📍 Локальный запуск: http://127.0.0.1:5000

📁 Структура проекта
guess-game/
├── app.py              # Главный Flask-сервер
├── templates/
│   └── index.html      # Интерфейс игры
├── static/
│   └── sounds.js       # Звуки через Web Audio API
├── requirements.txt    # Зависимости
└── README.md           # Этот файл

👤 Автор
brkotb

⭐ Если понравился проект, поставь звезду на GitHub!
🔗 Сайт в интернете: guess-game-27b5.onrender.com

