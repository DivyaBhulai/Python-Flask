from flask import Flask, render_template

app = Flask(__name__, static_url_path = "/", static_folder = "static")

@app.route('/')
def index():
    return render_template('webshop-tpl.html')

@app.route('/prijsklasse')
def prijs():
    return render_template('prijsklasse.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

app.run(debug=True)