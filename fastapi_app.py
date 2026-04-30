from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI()

class GameStart(BaseModel):
    name: str = "Гость"
    difficulty: str = "средне"

difficulties = {
    'легко': {'min': 1, 'max': 10, 'attempts': 5, 'points': 100},
    'средне': {'min': 1, 'max': 20, 'attempts': 6, 'points': 200},
    'хардкор': {'min': 1, 'max': 50, 'attempts': 7, 'points': 400}
}

@app.post("/api/start")
def start_game(game: GameStart):
    config = difficulties.get(game.difficulty, difficulties['средне'])
    secret = random.randint(config['min'], config['max'])
    # Здесь можно сохранить secret в сессию (для FastAPI нужна отдельная библиотека)
    return {
        "status": "started",
        "message": f"Игра началась! Загадано число от {config['min']} до {config['max']}. У тебя {config['attempts']} попыток.",
        "max_attempts": config['attempts'],
        "difficulty": game.difficulty,
        "range": f"{config['min']}-{config['max']}",
        "secret": secret  # Временно, потом уберем
    }