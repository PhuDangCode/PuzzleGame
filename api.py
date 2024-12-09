import requests

Base_URL = "https://wordle.votee.dev:8000"

def wordseg(text):
    url = f"{Base_URL}/wordseg"
    headers = {'Content-Type': 'application/json'}
    payload = {'text': text}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def daily(guess, size=5):
    url = f"{Base_URL}/daily"
    payload = {
        'guess': guess,
        'size': size
    }
    response = requests.post(url, json=payload)
    return response.json()

def random_guess(guess, size=5, seed=None):
    url = f"{Base_URL}/random"
    params = {
        'guess': guess,
        'size': size,
        'seed': seed
    }
    response = requests.get(url, params=params)
    return response.json()

def guess_word(word, guess):
    url = f"{Base_URL}/word/{word}"
    params = {
        'guess': guess
    }
    response = requests.get(url, params=params)
    return response.json()