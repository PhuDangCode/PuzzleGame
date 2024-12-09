from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os
from solve import load_word_list, refine_word_list  # Import functions from solve.py



app = Flask(__name__)

Base_URL = "https://wordle.votee.dev:8000"

# API functions
def wordseg_api(text):
    url = f"{Base_URL}/wordseg"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'text': text}  # form-encoded data
    response = requests.post(url, data=payload, headers=headers)  # Use data instead of json
    return response.json()


def daily_api(guess, size=5):
    url = f"{Base_URL}/daily"
    params = {'guess': guess, 'size': size}  # Query parameters
    response = requests.get(url, params=params)  # Use GET method with query parameters
    return response.json()


def random_guess_api(guess, size=5, seed=None):
    url = f"{Base_URL}/random"
    params = {'guess': guess, 'size': size}  # Required query parameters
    if seed:
        params['seed'] = seed  # Include seed only if provided
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API error: {response.text}")


def guess_word_api(word, guess):
    url = f"{Base_URL}/word/{word}"
    params = {'guess': guess}
    response = requests.get(url, params=params)
    return response.json()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/wordseg', methods=['GET', 'POST'])
def wordseg():
    result = None
    if request.method == 'POST':
        text = request.form['text']
        result = wordseg_api(text)
    return render_template('wordseg.html', result=result)

@app.route('/daily', methods=['GET', 'POST'])
def daily():
    feedback = None
    if request.method == 'POST':
        guess = request.form.get('guess')  # Safely retrieve the guess from the form
        if not guess:
            return render_template('daily.html', feedback=None, error="Please enter a valid guess.")
        feedback = daily_api(guess)
    return render_template('daily.html', feedback=feedback)


@app.route('/auto_solve', methods=['POST'])
def auto_solve():
    try:
        # Load word list
        word_list = load_word_list()

        data = request.get_json()
        size = data.get('size', 5)
        current_guess = word_list[0]
        solved = False

        while not solved:
            # Query the /daily API with the current guess
            feedback = daily_api(current_guess, size)
            if all(letter['result'] == 'correct' for letter in feedback):
                solved = True
                break

            # Refine word list based on feedback
            word_list = refine_word_list(word_list, feedback)
            if not word_list:
                return jsonify({'error': 'No possible words left.'}), 400

            current_guess = word_list[0]

        return jsonify({'guess': current_guess, 'feedback': feedback, 'solved': solved})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/random', methods=['GET', 'POST'])
def random_guess():
    feedback = None
    seed = request.form.get('seed', '')  # Retrieve seed if provided
    guess = request.form.get('guess', '')  # Retrieve guess

    if request.method == 'POST' and guess:  # Ensure guess is submitted
        try:
            feedback = random_guess_api(guess, size=5, seed=seed)  # Call the API
        except Exception as e:
            return render_template('random.html', feedback=None, error=str(e), seed=seed, last_guess=guess)

    # Render the template with feedback, seed, and the last guess
    return render_template('random.html', feedback=feedback, seed=seed, last_guess=guess)


@app.route('/auto_solve_random', methods=['POST'])
def auto_solve_random():
    try:
        # Load word list
        word_list = load_word_list()

        data = request.get_json()
        size = data.get('size', 5)
        seed = data.get('seed', None)
        current_guess = word_list[0]
        solved = False

        while not solved:
            # Query the /random API with the current guess and seed
            feedback = random_guess_api(current_guess, size=size, seed=seed)
            if all(letter['result'] == 'correct' for letter in feedback):
                solved = True
                break

            # Refine word list based on feedback
            word_list = refine_word_list(word_list, feedback)
            if not word_list:
                return jsonify({'error': 'No possible words left.'}), 400

            current_guess = word_list[0]

        return jsonify({'guess': current_guess, 'feedback': feedback, 'solved': solved})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/guess_word', methods=['GET', 'POST'])      
def guess_word():
    feedback = None
    if request.method == 'POST':
        word = request.form['word']
        guess = request.form['guess']
        feedback = guess_word_api(word, guess)
    return render_template('guess_word.html', feedback=feedback)

@app.route('/auto_solve_guess_word', methods=['POST'])
def auto_solve_guess_word():
    try:
        # Load word list
        word_list = load_word_list()

        data = request.get_json()
        word = data.get('word')
        size = data.get('size', 5)
        current_guess = word_list[0]
        solved = False

        while not solved:
            # Query the /word/<word> API with the current guess
            feedback = guess_word_api(word, current_guess)
            if all(letter['result'] == 'correct' for letter in feedback):
                solved = True
                break

            # Refine word list based on feedback
            word_list = refine_word_list(word_list, feedback)
            if not word_list:
                return jsonify({'error': 'No possible words left.'}), 400

            current_guess = word_list[0]

        return jsonify({'guess': current_guess, 'feedback': feedback, 'solved': solved})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
