from flask import Flask, render_template, session, redirect, url_for, escape, request

app = Flask(__name__, static_url_path = "/", static_folder = "static")

# secret key (fingerprint) nodig voor cookies
app.secret_key = 'hocuspocuspilatuspas'

#@app.route('/')
#def index():
#    return render_template('home.html')

# @app.route('/api')
# def api():
    
@app.route('/prijsklasse')
def prijs():
    titel = "USBWebshop"
    return render_template('prijsklasse.html', titel=titel)

@app.route('/contact')
def contact():
    titel = "USBWebshop"
    return render_template('contact.html', titel=titel)

@app.route('/opslag')
def opslag():
    titel = "USBWebshop"
    return render_template('opslag.html', titel=titel)

@app.route('/eigenschappen')
def eigenschappen():
    titel = "USBWebshop"
    return render_template('eigenschappen.html', titel=titel)

@app.route('/login')
def login():
    titel = "USBWebshop"
    return render_template('login.html', titel=titel)


#database
# maak connectie met DB

import sqlite3 as sql

DATABASE = 'C:/Users/divya/CloudStation/School/metis/Informatica/Python-flask/Webshop/webshop.db'
conn = sql.connect(DATABASE)
print ("Opened database successfully");

@app.route('/check_user', methods=['GET', 'POST'])
def check_user():
    titel = "USBWebshop"
    if request.method == 'POST':
        try:
            # haal variabelen uit het login formulier
            username = request.form['gebruikersnaam']
            password = request.form['wachtwoord']

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()
                cur.execute("SELECT gebruikersnaam, wachtwoord FROM klanten WHERE gebruikersnaam=? and wachtwoord=?", (username,password,))
                #maak array/tuple
                rows = cur.fetchone()
                # haal username uit de tuple
                usr = rows[0]
                # haal password uit de tuple
                pwd = rows[1]

                if (usr == username) and (pwd == password):
                    session['username'] = usr
                    session['loggedin'] = True
                    msg = "Succes"

                conn.commit()

        except:
            conn.rollback()
            msg = "Gebruikersnaam of wachtwoord is niet correct."

            # om te debuggen
            #cur.execute("SELECT gebruikersnaam, wachtwoord FROM klanten WHERE gebruikersnaam='divya' and wachtwoord='divya123'")
            #msg = cur.fetchall()

        finally:
            if msg == "Succes":
                return redirect(url_for('welkom'))
            else:
                return render_template("results.html", msg=msg, titel=titel)

            conn.close()

@app.route('/welkom')
def welkom():
    titel = "USBWebshop"
    username = session['username']
 #   return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>"
    return render_template('welkom.html', username=username, titel=titel)

@app.route('/logout')
def logout():
    titel = "USBWebshop"
    # remove the username from the session if it is there
    session.pop('username', None)
    session.pop('winkelmandje', None)
    session.pop('aantal', None)

#   return redirect(url_for('index'))
    return render_template('logout.html', titel=titel)
  #  return 'Je bent nu uitgelogd.'

# submit klantgegevens
@app.route('/klantgegevens')
def new_klant():
    titel = "USBWebshop"
    return render_template('klant.html', titel=titel)

# sql klant toevoegen
@app.route('/klant_toevoegen', methods=['POST', 'GET'])
def klant_toevoegen():
    titel = "USBWebshop"
    if request.method == 'POST':
        try:
            voornaam = request.form['voornaam']
            achternaam = request.form['achternaam']
            adres = request.form['adres']
            postcode = request.form['postcode']
            plaats = request.form['plaats']
            land = request.form['land']
            email = request.form['email']
            gebruikersnaam = request.form['gebruikersnaam']
            wachtwoord = request.form['pwd']

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()
                #check of username al bestaat
                cur.execute("SELECT gebruikersnaam FROM klanten WHERE gebruikersnaam=?",(gebruikersnaam,))
                rows = cur.fetchone()
                usr = rows[0]

                if (usr == gebruikersnaam):
  #                  cur = conn.cursor()
 #                   cur.execute("INSERT INTO klanten (voornaam,achternaam,adres,postcode,plaats,land,email,gebruikersnaam,wachtwoord) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",(voornaam,achternaam,adres,postcode,plaats,land,email,gebruikersnaam,wachtwoord))
                    msg = "Gebruikersnaam bestaat al. Kies een andere gebruikersnaam."

        except:
            # maak klant aan
  #          conn.rollback()
            cur.execute("INSERT INTO klanten (voornaam,achternaam,adres,postcode,plaats,land,email,gebruikersnaam,wachtwoord) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",(voornaam, achternaam, adres, postcode, plaats, land, email, gebruikersnaam, wachtwoord))
            conn.commit()
            msg = "Je bent succesvol toegevoegd"

        finally:
            return render_template("results.html", msg=msg, titel=titel)

            conn.close()

@app.route('/')
def show_producten():
    titel = "USBWebshop"

    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row

    cur = conn.cursor()
    cur.execute("SELECT * FROM producten")

    rows = cur.fetchall();
    return render_template("home.html", rows=rows, titel = titel)

@app.route('/bestellen', methods=['POST', 'GET'])
def bestellen():
    titel = "USBWebshop"

    if request.method == 'POST':
        try:
            # haal product_ID op
            productID = request.form['product_ID']

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM producten WHERE product_ID=?",(productID,))
                #maak array/tuple
                row=cur.fetchone()
                product = row[0]

                # aantal producten bijhouden
                if 'aantal' in session:
                    teller = session['aantal']
                    teller = teller + 1
                    session['aantal'] = teller

                if 'aantal' not in session:
                    teller = 0
                    session['aantal'] = []
                    # teller ophogen t.b.v. aantal producten in winkelmandje
                    teller = teller + 1
                    session['aantal'] = teller

                # welke producten in winkelmandje
                if 'winkelmandje' not in session:
                    session['winkelmandje'] = []
                    winkelmandje_list = session['winkelmandje']
                    winkelmandje_list.append(product)
                    session['winkelmandje'] = winkelmandje_list

                else:
                    winkelmandje_list = session['winkelmandje']
                    winkelmandje_list.append(product)
                    session['winkelmandje'] = winkelmandje_list

                msg = "Product in winkelmandje"
                conn.commit()

        except:
            conn.rollback()
            msg = "Niet gelukt om product in winkelmandje te zetten."

        finally:
            return render_template("results.html", msg=msg, titel=titel)
            conn.close()

app.run(debug=True)
