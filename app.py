from flask import Flask, render_template, session, redirect, url_for, escape, request
app = Flask(__name__, static_url_path = "/", static_folder = "static")

app.secret_key = 'hocuspocuspilatuspas'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/prijsklasse')
def prijs():
    return render_template('prijsklasse.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/opslag')
def opslag():
    return render_template('opslag.html')

@app.route('/eigenschappen')
def eigenschappen():
    return render_template('eigenschappen.html')

@app.route('/bestellen-en-versturen')
def bestellen_en_versturen():
    return render_template('bestellen-en-versturen.html')

@app.route('/logo')
def logo():
    return render_template('home.html')

'''@app.route('/login')
def login():
    return render_template('login.html')
'''

@app.route('/login', methods=['GET', 'POST'])

def login():
    if 'username' in session:
        username = session['username']
        return redirect(url_for('welkom'))
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('welkom'))
    return render_template('login.html')

@app.route('/welkom')
def welkom():
    username = session['username']
 #   return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>"
    return render_template('welkom.html', username=username)

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
 #   return redirect(url_for('index'))
    return render_template('logout.html')
  #  return 'Je bent nu uitgelogd.'

#database
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

app.run(debug=True)
