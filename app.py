from flask import Flask, jsonify, render_template, request, session
from datetime import datetime
import random
import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:пароль@localhost:5432/guess_game')

app = Flask(__name__)
app.secret_key = 'super-secret-key-2024'

# ========== НАСТРОЙКА БАЗЫ ДАННЫХ ==========

DATABASE_URL = "postgresql://postgres:ТВОЙ_ПАРОЛЬ@localhost:5432/guess_game"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    score INTEGER NOT NULL,
                    difficulty VARCHAR(50),
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()

def save_record(player_name, score, difficulty):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO records (name, score, difficulty) VALUES (%s, %s, %s)",
                (player_name, score, difficulty)
            )
        conn.commit()

def load_records():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT name, score, difficulty, date FROM records ORDER BY score DESC LIMIT 10"
            )
            return cur.fetchall()

# ========== ИНИЦИАЛИЗАЦИЯ БД ==========
init_db()

# ========== ГЛАВНАЯ СТРАНИЦА ==========
@app.route('/')
def index():
    return render_template('index.html')

# ========== ЗВУКИ ==========
@app.route('/api/sounds/<sound_type>')
def get_sound_preset(sound_type):
    presets = {
        'win': {'frequencies': [523.25, 659.25, 783.99], 'duration': 0.3},
        'lose': {'frequencies': [392.00, 349.23, 293.66, 261.63], 'duration': 0.25},
        'achievement': {'frequencies': [784.00, 987.77, 1174.66, 987.77, 784.00], 'duration': 0.15}
    }
    return jsonify({
        'type': sound_type,
        'data': presets.get(sound_type, presets['win']),
        'timestamp': datetime.now().isoformat()
    })

# ========== ИГРОВЫЕ API ==========

@app.route('/api/start', methods=['POST'])
def start_game():
    data = request.get_json()
    player_name = data.get('name', 'Гость')
    difficulty = data.get('difficulty', 'средне')

    # НОВЫЕ НАСТРОЙКИ СЛОЖНОСТИ (исправленный баланс)
    difficulties = {
        'легко': {'min': 1, 'max': 10, 'attempts': 5, 'points': 100},
        'средне': {'min': 1, 'max': 20, 'attempts': 6, 'points': 200},
        'хардкор': {'min': 1, 'max': 50, 'attempts': 7, 'points': 400}
    }

    config = difficulties.get(difficulty, difficulties['средне'])

    session['player_name'] = player_name
    session['secret_number'] = random.randint(config['min'], config['max'])
    session['attempts_left'] = config['attempts']
    session['total_attempts'] = config['attempts']
    session['score'] = 0
    session['game_over'] = False
    session['difficulty'] = difficulty
    session['min_range'] = config['min']
    session['max_range'] = config['max']
    session['points_per_win'] = config['points']

    return jsonify({
        'status': 'started',
        'message': f'Игра началась! Загадано число от {config["min"]} до {config["max"]}. У тебя {config["attempts"]} попыток.',
        'max_attempts': config['attempts'],
        'difficulty': difficulty,
        'range': f'{config["min"]}-{config["max"]}'
    })

@app.route('/api/guess', methods=['POST'])
def make_guess():
    if session.get('game_over'):
        return jsonify({'error': 'Игра окончена. Начни новую!'}), 400

    data = request.get_json()
    guess = data.get('guess')

    if guess is None:
        return jsonify({'error': 'Введи число!'}), 400

    secret = session['secret_number']
    session['attempts_left'] -= 1
    attempts_used = session['total_attempts'] - session['attempts_left']

    if guess == secret:
        points = session['points_per_win']
        bonus = max(0, (session['total_attempts'] - attempts_used) * 10)
        total_score = points + bonus
        session['score'] = total_score
        session['game_over'] = True

        save_record(session['player_name'], total_score, session['difficulty'])

        return jsonify({
            'result': 'win',
            'message': f'Поздравляю! Ты угадал число {secret} за {attempts_used} попыток!',
            'score': total_score,
            'attempts_used': attempts_used,
            'attempts_left': 0,
            'sound': 'win'
        })

    if session['attempts_left'] <= 0:
        session['game_over'] = True
        return jsonify({
            'result': 'lose',
            'message': f'Попытки кончились! Загаданное число было {secret}.',
            'score': 0,
            'attempts_used': attempts_used,
            'attempts_left': 0,
            'sound': 'lose'
        })

    hint = 'больше' if guess < secret else 'меньше'
    return jsonify({
        'result': 'continue',
        'message': f'Не угадал! Загаданное число {hint} чем {guess}. Осталось попыток: {session["attempts_left"]}',
        'attempts_used': attempts_used,
        'attempts_left': session['attempts_left'],
        'sound': 'hint' if attempts_used % 3 == 0 else None
    })

@app.route('/api/status', methods=['GET'])
def game_status():
    if session.get('game_over'):
        return jsonify({'status': 'finished', 'game_over': True})
    if 'secret_number' not in session:
        return jsonify({'status': 'not_started'})

    return jsonify({
        'status': 'active',
        'attempts_left': session.get('attempts_left', 0),
        'total_attempts': session.get('total_attempts', 0),
        'difficulty': session.get('difficulty'),
        'range': f"{session.get('min_range', 1)}-{session.get('max_range', 100)}"
    })

@app.route('/api/top_scores', methods=['GET'])
def top_scores():
    records = load_records()
    return jsonify({'records': records})

@app.route('/api/reset', methods=['POST'])
def reset_game():
    session.clear()
    return jsonify({'status': 'reset'})

# ========== РЕЖИМ "ИИ УГАДЫВАЕТ" ==========

@app.route('/api/ai/start', methods=['POST'])
def ai_start():
    data = request.get_json()
    player_name = data.get('name', 'Гость')
    difficulty = data.get('difficulty', 'средне')
    
    difficulties = {
        'легко': {'min': 1, 'max': 10, 'max_attempts': 5},
        'средне': {'min': 1, 'max': 20, 'max_attempts': 6},
        'хардкор': {'min': 1, 'max': 50, 'max_attempts': 7}
    }
    
    config = difficulties.get(difficulty, difficulties['средне'])
    
    session['ai_mode'] = 'guessing'
    session['ai_player_name'] = player_name
    session['ai_min'] = config['min']
    session['ai_max'] = config['max']
    session['ai_attempts_left'] = config['max_attempts']
    session['ai_guesses'] = []
    session['ai_finished'] = False
    session['ai_difficulty'] = difficulty
    
    first_guess = (config['min'] + config['max']) // 2
    session['ai_current_guess'] = first_guess
    
    return jsonify({
        'status': 'started',
        'message': f'🤖 ИИ готов угадывать! Загадай число от {config["min"]} до {config["max"]}.',
        'guess': first_guess,
        'attempts_left': config['max_attempts'],
        'min': config['min'],
        'max': config['max']
    })

@app.route('/api/ai/guess', methods=['POST'])
def ai_make_guess():
    if session.get('ai_finished'):
        return jsonify({'error': 'Игра окончена. Начни новую!'}), 400
    
    data = request.get_json()
    answer = data.get('answer')
    
    if answer not in ['больше', 'меньше', 'равно']:
        return jsonify({'error': 'Ответь "больше", "меньше" или "равно"'}), 400
    
    session['ai_attempts_left'] -= 1
    session['ai_guesses'].append({
        'guess': session['ai_current_guess'],
        'answer': answer
    })
    
    if answer == 'равно':
        session['ai_finished'] = True
        return jsonify({
            'result': 'win',
            'message': f'🤖 ИИ угадал твоё число {session["ai_current_guess"]} за {len(session["ai_guesses"])} попыток!',
            'attempts_used': len(session['ai_guesses']),
            'sound': 'lose'
        })
    
    if session['ai_attempts_left'] <= 0:
        session['ai_finished'] = True
        return jsonify({
            'result': 'lose',
            'message': f'🎉 ИИ не смог угадать! Ты победил!',
            'sound': 'win'
        })
    
    if answer == 'больше':
        session['ai_min'] = session['ai_current_guess'] + 1
    else:
        session['ai_max'] = session['ai_current_guess'] - 1
    
    new_guess = (session['ai_min'] + session['ai_max']) // 2
    session['ai_current_guess'] = new_guess
    
    return jsonify({
        'result': 'continue',
        'message': '🤔 ИИ думает...',
        'guess': new_guess,
        'attempts_left': session['ai_attempts_left']
    })

@app.route('/api/ai/reset', methods=['POST'])
def ai_reset():
    session.pop('ai_mode', None)
    session.pop('ai_finished', None)
    return jsonify({'status': 'reset'})

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("Сервер запущен!")
    print("Открой в браузере: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
