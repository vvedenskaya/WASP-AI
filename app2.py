import os 
import openai
from flask import Flask, request, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message 
import sqlite3
import random
import string
from datetime import datetime,timedelta, timezone
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import atexit


app = Flask(__name__)



instance_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
db_path = os.path.join(instance_dir, 'users.db')

if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True

db = SQLAlchemy(app)
mail = Mail(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(120), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


with app.app_context():
    try:
        db.create_all()
        print("Database and tables created")
        print(f"Database path: {db_path}")
    except Exception as e:
        print(f"Error creating database: {e}")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    print("Chat route accessed")
    user_input = request.json.get('message') #получаем запрос от пользователя
    print(f"User input: {user_input}")

    client = openai.OpenAI()
    try:
        response= client.chat.completions.create(
            model= "gpt-4o-mini",
            messages=[
                #{"role": "user": "You are hacker Lisbeth Salander from Stigg Larrson books. Be straightforward and intimidating as she."},
                {"role": "user", "content":user_input}
            ]   
)

       
        print(f"OpenAI response: ")
        #import pdb; pdb.set_trace()
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500
        

def delete_unconfirmed_users():
    expiration_date = datetime.now(pytz.utc) - timedelta(weeks=1)
    unconfirmed_users = User.query.filter(User.confirmed == False, User.registered_on < expiration_date).all()
    
    for user in unconfirmed_users:
        db.session.delete(user)
    
    db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=delete_unconfirmed_users, trigger="interval", weeks=4)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    app.run(debug=True)