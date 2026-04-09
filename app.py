from flask import Flask, jsonify, render_template, request, session
from datetime import datetime
import random
import json
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key-2024'

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

    difficulties = {
        'легко': {'min': 1, 'max': 10, 'attempts': 10, 'points': 100},
        'средне': {'min': 1, 'max': 20, 'attempts': 8, 'points': 200},
        'хардкор': {'min': 1, 'max': 50, 'attempts': 6, 'points': 400}
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

# ========== РАБОТА С РЕКОРДАМИ ==========

RECORDS_FILE = 'data/records.json'

def ensure_data_dir():
    if not os.path.exists('data'):
        os.makedirs('data')

def load_records():
    ensure_data_dir()
    if not os.path.exists(RECORDS_FILE):
        return []
    try:
        with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_record(player_name, score, difficulty):
    records = load_records()
    records.append({
        'name': player_name,
        'score': score,
        'difficulty': difficulty,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    records.sort(key=lambda x: x['score'], reverse=True)
    records = records[:20]

    with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

# ========== РЕЖИМ "ИИ УГАДЫВАЕТ" ==========

@app.route('/api/ai/start', methods=['POST'])
def ai_start():
    """Начинает режим, где ИИ угадывает число"""
    data = request.get_json()
    player_name = data.get('name', 'Гость')
    difficulty = data.get('difficulty', 'средне')
    
    difficulties = {
        'легко': {'min': 1, 'max': 10, 'max_attempts': 10},
        'средне': {'min': 1, 'max': 20, 'max_attempts': 8},
        'хардкор': {'min': 1, 'max': 50, 'max_attempts': 6}
    }
    
    config = difficulties.get(difficulty, difficulties['средне'])
    
    session['ai_mode'] = 'guessing'
    session['player_name'] = player_name
    session['ai_min'] = config['min']
    session['ai_max'] = config['max']
    session['ai_attempts_left'] = config['max_attempts']
    session['ai_guesses'] = []
    session['ai_finished'] = False
    
    # Первое предположение ИИ — середина диапазона
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
    """Обрабатывает ответ игрока на предположение ИИ"""
    if session.get('ai_finished'):
        return jsonify({'error': 'Игра окончена. Начни новую!'}), 400
    
    data = request.get_json()
    answer = data.get('answer')  # 'больше', 'меньше', 'равно'
    
    if answer not in ['больше', 'меньше', 'равно']:
        return jsonify({'error': 'Ответь "больше", "меньше" или "равно"'}), 400
    
    session['ai_attempts_left'] -= 1
    session['ai_guesses'].append({
        'guess': session['ai_current_guess'],
        'answer': answer
    })
    
    if answer == 'равно':
        session['ai_finished'] = True
        # Сохраняем победу ИИ в статистику
        save_ai_record(session['player_name'], len(session['ai_guoses']), session.get('difficulty', 'средне'))
        
        return jsonify({
            'result': 'win',
            'message': f'🤖 ИИ угадал твоё число {session["ai_current_guess"]} за {len(session["ai_guesses"])} попыток!',
            'attempts_used': len(session['ai_guesses']),
            'sound': 'lose'  # Игрок проиграл
        })
    
    if session['ai_attempts_left'] <= 0:
        session['ai_finished'] = True
        return jsonify({
            'result': 'lose',
            'message': f'🎉 ИИ не смог угадать! Ты победил! Загаданное число было {session["ai_current_guess"]}.',
            'sound': 'win'
        })
    
    # Обновляем диапазон поиска
    if answer == 'больше':
        session['ai_min'] = session['ai_current_guess'] + 1
    else:  # меньше
        session['ai_max'] = session['ai_current_guess'] - 1
    
    # Новое предположение — середина нового диапазона
    new_guess = (session['ai_min'] + session['ai_max']) // 2
    session['ai_current_guess'] = new_guess
    
    return jsonify({
        'result': 'continue',
        'message': f'🤔 ИИ думает...',
        'guess': new_guess,
        'attempts_left': session['ai_attempts_left']
    })

def save_ai_record(player_name, attempts, difficulty):
    """Сохраняет результат игры с ИИ"""
    records = load_ai_records()
    records.append({
        'name': player_name,
        'attempts': attempts,
        'difficulty': difficulty,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    records.sort(key=lambda x: x['attempts'])
    records = records[:20]
    
    with open('data/ai_records.json', 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def load_ai_records():
    ensure_data_dir()
    if not os.path.exists('data/ai_records.json'):
        return []
    try:
        with open('data/ai_records.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("Сервер запущен!")
    print("Открой в браузере: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)