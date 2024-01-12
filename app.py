from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import math

app = Flask(__name__)

# Vordefinierte Werte für den Kalibrierungsoffset (ersetzen Sie dies durch echte Werte)
LF_OFFSET = 0
RF_OFFSET = 0
LR_OFFSET = 0
RR_OFFSET = 0

# SQLite-Datenbank initialisieren
conn = sqlite3.connect('weight_logs.db')
cursor = conn.cursor()

# Erstellen Sie die Tabelle, wenn sie noch nicht existiert
cursor.execute('''
    CREATE TABLE IF NOT EXISTS weight_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        time TEXT,
        LF REAL,
        RF REAL,
        LR REAL,
        RR REAL,
        theta_x REAL,
        theta_y REAL,
        LF_CAL REAL,
        RF_CAL REAL,
        LR_CAL REAL,
        RR_CAL REAL,
        action TEXT,
        total_mass REAL,
        Fgx REAL,
        Frx REAL,
        Fgx_schräg REAL,
        Fgy REAL,
        Fry REAL,
        Fgy_schräg REAL,
        Fg_schräg REAL
    )
''')
conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        LF = float(request.form['LF'])
        RF = float(request.form['RF'])
        LR = float(request.form['LR'])
        RR = float(request.form['RR'])
        theta_x = float(request.form['theta_x'])
        theta_y = float(request.form['theta_y'])
        
        LF_CAL = float(request.form['LF_CAL'])
        RF_CAL = float(request.form['RF_CAL'])
        LR_CAL = float(request.form['LR_CAL'])
        RR_CAL = float(request.form['RR_CAL'])

        if request.form['action'] == 'Tara':
            LF -= LF_OFFSET
            RF -= RF_OFFSET
            LR -= LR_OFFSET
            RR -= RR_OFFSET

        # Berechnungen
        LF_mass = (LF - LF_OFFSET) / LF_CAL
        RF_mass = (RF - RF_OFFSET) / RF_CAL
        LR_mass = (LR - LR_OFFSET) / LR_CAL
        RR_mass = (RR - RR_OFFSET) / RR_CAL

        total_mass = LF_mass + RF_mass + LR_mass + RR_mass

        Fgx = total_mass * 9.81 * math.cos(math.radians(theta_x))
        Fgy = total_mass * 9.81 * math.cos(math.radians(theta_y))

        Frx = total_mass * 9.81 * math.sin(math.radians(theta_x))
        Fry = total_mass * 9.81 * math.sin(math.radians(theta_y))

        Fgx_schräg = Fgx - Frx
        Fgy_schräg = Fgy - Fry

        Fg_schräg = math.sqrt(Fgx_schräg ** 2 + Fgy_schräg ** 2)

        # Log-Eintrag erstellen und in die Datenbank einfügen
        log_entry = (
            datetime.now().strftime('%Y-%m-%d'),  # Datum
            datetime.now().strftime('%H:%M:%S'),  # Uhrzeit
            LF, RF, LR, RR, theta_x, theta_y,
            LF_CAL, RF_CAL, LR_CAL, RR_CAL,
            request.form['action'], total_mass, Fgx, Frx,
            Fgx_schräg, Fgy, Fry, Fgy_schräg, Fg_schräg
        )

        cursor.execute('''
            INSERT INTO weight_logs (
                date, time, LF, RF, LR, RR, theta_x, theta_y,
                LF_CAL, RF_CAL, LR_CAL, RR_CAL,
                action, total_mass, Fgx, Frx,
                Fgx_schräg, Fgy, Fry, Fgy_schräg, Fg_schräg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', log_entry)

        conn.commit()

        return render_template('index.html', total_mass=total_mass, Fgx=Fgx, Frx=Frx,
                               Fgx_schräg=Fgx_schräg, Fgy=Fgy, Fry=Fry,
                               Fgy_schräg=Fgy_schräg, Fg_schräg=Fg_schräg,
                               LF_CAL=LF_CAL, RF_CAL=RF_CAL, LR_CAL=LR_CAL, RR_CAL=RR_CAL)

    return render_template('index.html', total_mass=None, LF_CAL=LF_CAL, RF_CAL=RF_CAL, LR_CAL=LR_CAL, RR_CAL=RR_CAL)

if __name__ == '__main__':
    app.run(debug=True)
