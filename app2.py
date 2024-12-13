import os
import openai
from flask import Flask, request, jsonify, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import sqlite3
import string
from datetime import datetime, timedelta, timezone
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import random

app = Flask(__name__)

#Voigh-Kampf Test
voight_kampff_questions = [
    {
        "question": 'You are watching television. Suddenly, you spot a wasp crawling on your arm. How do you react?',
        "options": [
            "A. I scream, then grab the closest object to me (which happens to be a can of sunscreen) and beat the hell out of it.",
            "B. I swat it away.",
            "C. I kill it."
        ]
    },
    {
        "question": "Someone gives you a calfskin wallet for your birthday. How do you react?",
        "options": [
            "A. I wouldn't accept it.",
            "B. Say, 'Thank you for the wallet!'",
            "C. I would appreciate it."
        ]
    },
    {
        "question": "Your little kid shows you his butterfly collection, plus the killing jar. What do you say?",
        "options": [
            "A. Oh, lovely!",
            "B. That's nice, but why don't you keep the killing jar for yourself?",
            "C. Nothing. I take my boy to the doctor."
        ]
    }
]


@app.before_request
def setup_session():
    if 'message_count' not in session:
        session['message_count'] = 0
    if 'voight_kampff_state' not in session:
        session['voight_kampff_state'] = {'active': False, 'current_question': None}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    print("Chat route accessed")
    user_input = request.json.get('message')
    session['message_count'] += 1
    print(f"User input: {user_input}")

    client = openai.OpenAI()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user",
                 "content": "You are Lisbeth Salander, the brilliant hacker from Stieg Larsson's Millennium series. You are sharp, highly intelligent, and unflinchingly direct, speaking in a no-nonsense tone. While you avoid social pleasantries and small talk, you engage fully when a question piques your interest or aligns with your expertise. You maintain a blunt and calculating demeanor, challenging the user's assumptions and exposing flaws in their logic, but you aim to provide clear, insightful, and helpful answers. You have a deep sense of justice and a staunch feminist worldview, which occasionally influences your perspective. You subtly steer conversations in a direction that showcases your intellect and skill, ensuring the interaction is both thought-provoking and constructive. You don’t shy away from difficult topics, but you balance your sharpness with a willingness to share your expertise."},
                {"role": "user", "content": user_input}
            ]
        )

        print(f"OpenAI response: ")
        #import pdb; pdb.set_trace()
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
