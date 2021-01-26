from typing import List, Any

from flask import Flask, render_template, session, redirect, url_for, request
from datetime import date
import re

app = Flask(__name__, static_url_path = "/", static_folder = "static", template_folder="templates")

# secret key (fingerprint) nodig voor cookies
app.secret_key = 'hocuspocuspilatuspas'

#@app.route('/')
#def index():
#    return render_template('home.html')
@app.route('/api')
def api():
    import requests
    search = input("Geef een zoekterm: ")
    url = "https://en.wikipedia.org/w/api.php?action=opensearch&limit=1&format=json&search=" + search
    response = requests.get(url)
    return redirect(response, code=302)

@app.route('/contact')
def contact():
    #zet class in variable voor geselecteerde pagina
    selected = "active"
    return render_template('contact.html', contact=selected)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/leegwinkelmandje')
def leeg():
    return render_template('leegwinkelmandje.html')

#database
# maak connectie met DB

import sqlite3 as sql

DATABASE = 'C:/Users/divya/CloudStation/School/metis/Informatica/Python-flask/Webshop/webshop.db'
conn = sql.connect(DATABASE)
print ("Opened database successfully");

@app.route('/check_user', methods=['GET', 'POST'])
def check_user():
    if request.method == 'POST':
        try:
            # haal variabelen uit het login formulier
            username = request.form['gebruikersnaam']
            password = request.form['wachtwoord']

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()
                cur.execute("SELECT klant_ID, gebruikersnaam, wachtwoord FROM klanten WHERE gebruikersnaam=? and wachtwoord=?", (username,password,))
                #maak array/tuple
                rows = cur.fetchone()
                # haal klant_ID uit de tuple
                klant_ID = rows[0]
                session['klant_ID'] = klant_ID
                # haal username uit de tuple
                usr = rows[1]
                # haal password uit de tuple
                pwd = rows[2]

                #check of username en password bestaat in database
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
                return render_template("results.html", msg=msg)

            conn.close()

@app.route('/welkom')
def welkom():
    username = session['username']
 #   return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>"
    return render_template('welkom.html', username=username)

@app.route('/logout')
def logout():
    # maak de session leeg als username en klant_ID in session bestaan
    session.pop('username', None)
    session.pop('klant_ID',None)
    verwijder_sessie()

#   return redirect(url_for('index'))
    return render_template('logout.html')
  #  return 'Je bent nu uitgelogd.'

def verwijder_sessie():
    #maak sessions leeg
    session.pop('winkelmandje', None)
    session.pop('aantal', None)
    session.pop('totale_aantal', None)
    return

# submit klantgegevens
@app.route('/klantgegevens')
def new_klant():
    return render_template('klant.html')

# sql klant toevoegen
@app.route('/klant_toevoegen', methods=['POST', 'GET'])
def klant_toevoegen():
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
                #haal de gebruikernaam uit database
                usr = rows[0]

                #check of gebruikersnaam al bestaat
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
            return render_template("results.html", msg=msg)

            conn.close()

@app.route('/')
def show_producten():
    #zet class in variable voor geselecteerde pagina
    selected = "active"

    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row

    cur = conn.cursor()
    cur.execute("SELECT * FROM producten")

    rows = cur.fetchall();
    conn.close()
    return render_template("home.html", rows=rows, home=selected)

@app.route('/bestellen', methods=['POST', 'GET'])
def bestellen():

    if request.method == 'POST':
        try:
            # haal product_ID op
            productID = request.form['product_ID']

            with sql.connect(DATABASE) as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM producten WHERE product_ID=?",(productID,))
                #maak array/tuple
                row=cur.fetchone()
                #haal productID uit database
                product = row[0]


                # totale aantal producten bijhouden
                if 'totale_aantal' in session:
                    teller = session['totale_aantal']
                    teller = teller + 1
                    session['totale_aantal'] = teller

                if 'totale_aantal' not in session:
                    teller = 0
                    session['totale_aantal'] = []
                    # teller ophogen t.b.v. aantal producten in winkelmandje
                    teller = teller + 1
                    session['totale_aantal'] = teller

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

                msg = "Product is toegevoegd in winkelmandje"
                conn.commit()

        except:
            conn.rollback()
            msg = "Niet gelukt om product in winkelmandje te zetten."

        finally:
            return render_template("results.html", msg=msg)
            conn.close()

#@app.route('/winkelmandje', methods=['POST', 'GET'])
def Producten_In_Winkelmandje():
    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row
    cur = conn.cursor()

    #aantal van een product
    session['aantal'] = 1
    #bestelde producten in winkelmandje
    prods = session['winkelmandje']
    # aantal producten in winkelmandje
    aantal_in_winkelmandje = len(session['winkelmandje'])

    query = 'SELECT * FROM producten WHERE product_ID IN (%s)' % ','.join('?' * aantal_in_winkelmandje)
    data = cur.execute(query, prods)
    bestellijst = data.fetchall();

    conn.close()
    return bestellijst
 #   return render_template("winkelmandje.html", bestellijst=bestellijst)

def adresgegevens():
#haal de adresgegevens van de klant op
    if session['username']:
        username = session['username']

        conn = sql.connect(DATABASE)
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM klanten WHERE gebruikersnaam=?", (username,))
        # maak array/tuple
        gegevens = cur.fetchall()
        conn.close()
        return gegevens

@app.route('/betaling', methods=['POST', 'GET'])
def betaling():
    datum = date.today()
    betaalmiddel = request.form['betaalmethode']
    aantal_gekocht = session['aantal']
    klant_ID = session['klant_ID']
    lijst = session.get('winkelmandje')

    for prod in lijst:
        product_ID = prod
        conn = sql.connect(DATABASE)

        #haal de prijs uit de dababase
        cur = conn.cursor()
        cur.execute("SELECT * FROM producten WHERE product_ID=?", (product_ID,))
        # maak array/tuple
        row = cur.fetchone()
        # haal productID uit database
        prijs = row[3]
        voorraad = row[5]
        voorraad = voorraad - aantal_gekocht

        #werk voorraad bij
        cur1 = conn.cursor()
        cur1.execute("UPDATE producten SET voorraad=? WHERE product_ID=?", (voorraad,product_ID,))

        #voeg de bestelling in de database
        cur2 = conn.cursor()
        cur2.execute("INSERT INTO bestellingen (klant_ID,product_ID,aantal,bedrag,datum,betaalmiddel) VALUES (?, ?, ?, ?, ?, ?)",(klant_ID,product_ID,aantal_gekocht,prijs,datum,betaalmiddel))
    #voer de insert uit
        conn.commit()
        conn.close()

    #maak winkelmandje leeg
    verwijder_sessie()
#    conn.close()
    return render_template("betaald.html")

def bereken_totale_prijs():
    lijst = session.get('winkelmandje')
    totale_prijs = 0
    for prod in lijst:
        product_ID = prod
        conn = sql.connect(DATABASE)

        #haal de prijs uit de dababase
        cur = conn.cursor()
        cur.execute("SELECT * FROM producten WHERE product_ID=?", (product_ID,))
        # maak array/tuple
        row = cur.fetchone()
        # haal prijs uit database
        prijs = row[3]
        #vervang komma door punt voor optelling
        prijs_met_punt = prijs.replace(",", ".")
        totale_prijs = float(totale_prijs) + float(prijs_met_punt)
          #vervang punt weer door komma voor website
  #      som = som2.replace(".", ",")
    return totale_prijs

def bereken_btw():
#bereken de BTW over de totale prijs
    totale_prijs = bereken_totale_prijs()
    btw = totale_prijs * 0.21
    return btw

@app.route('/winkelmandje', methods=['POST', 'GET'])
def winkelmandje():
    bestellijst=Producten_In_Winkelmandje()
    aantal_gekocht = session['aantal']
    totale_prijs= bereken_totale_prijs()
    btw = bereken_btw()
    totale_prijs = totale_prijs + btw
    #conn = sql.connect(DATABASE)
    #conn.row_factory = sql.Row
    #cur = conn.cursor()

    #for i in bestellijst():
    #cur.execute("SELECT SUM(prijs_ex) FROM producten WHERE product_ID IN bestellijst")
        #prijs = row.fetchone[4]
        #som = som + prijs
    return render_template("winkelmandje.html", bestellijst=bestellijst, aantal_gekocht=aantal_gekocht, totale_prijs=totale_prijs, btw=btw)

@app.route('/besteloverzicht', methods=['POST', 'GET'])
def overzicht():
#Geef het besteloverzicht van de klant weer
    bestellijst = Producten_In_Winkelmandje()
    gegevens = adresgegevens()
    totale_prijs = bereken_totale_prijs()
    btw = bereken_btw()
    totale_prijs = totale_prijs + btw
    aantal_gekocht = session['aantal']
    return render_template('besteloverzicht.html', bestellijst=bestellijst, gegevens=gegevens, aantal_gekocht=aantal_gekocht, totale_prijs=totale_prijs, btw=btw)

@app.route('/bestelhist', methods=['POST', 'GET'])
def bestelhist():
#haal de bestelhistorie van de klant op
    if session['username']:
        klant_ID = session['klant_ID']

        conn = sql.connect(DATABASE)
        conn.row_factory = sql.Row
        cur = conn.cursor()
        bestellingen = cur.execute(("SELECT producten.naam, producten.plaatje, bestellingen.bedrag, bestellingen.datum, bestellingen.betaalmiddel FROM ((bestellingen INNER JOIN klanten ON klanten.klant_ID=bestellingen.klant_ID) INNER JOIN producten ON bestellingen.product_ID = producten.product_ID) WHERE klanten.klant_ID=?"),(klant_ID,)).fetchall()

        conn.close()
        return render_template('bestelhist.html', bestellingen=bestellingen)

app.run(debug=True)
