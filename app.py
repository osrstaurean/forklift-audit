 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
###############################################################################
"""
CREATED BY ALEXANDER P CRAWFORD
FOR USE BY AWL AUTOMATION, ALEXANDER CRAWFORD & COMPANY ENTITIES
LICENSE:
"""
###############################################################################
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import io
import os

from flask import Flask, render_template, request, redirect, send_file, url_for, abort
import sqlite3
import qrcode
from datetime import datetime, timezone


# ngrok config add-authtoken 30CBxaAOUQ9MF83bTPDvF7WGSwu_42iAiq1sXonTE2iiWVBbD
DB_PATH = 'forklift_audit.db'
app = Flask(__name__)
try:
    from pyngrok import ngrok
    NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
    if NGROK_AUTH_TOKEN:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    _tunnel = ngrok.connect(5000, bind_tls=True)
    PUBLIC_URL = _tunnel.public_url
    print(f" * ngrok tunnel established at {PUBLIC_URL}")
except ImportError:
    # If pyngrok isn’t installed, fall back to PUBLIC_URL env or request.url_root
    PUBLIC_URL = os.getenv("PUBLIC_URL", "")
    if PUBLIC_URL:
        print(f" * Using PUBLIC_URL={PUBLIC_URL}")
    else:
        print(" * No pyngrok or PUBLIC_URL; QR will point at local host")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT
        operator TEXT
        overheadGuard INTEGER
        hydraulic_cylinders INTEGER
        mast INTEGER
        lift_ChainsRollers INTEGER
        forks INTEGER
        tires INTEGER
        lpgTankPin INTEGER
        lpgTankHose INTEGER
        gasGauge INTEGER
        engineOilLevel INTEGER
        battery INTEGER
        hydraulicFluidLevel INTEGER
        engineCoolantLevel INTEGER
        glovesarePresent INTEGER
        comments TEXT
        submitted_at TEXT
        )
    ''')
    existing = { row[1] for row in c.fetchall() }


    desired = {
        "operator":             "TEXT",
        "forklift_id":          "TEXT",
        "overheadGuard":        "INTEGER",
        "hydraulic_cylinders":  "INTEGER",
        "mast":                 "INTEGER",
        "lift_ChainsRollers":   "INTEGER",
        "forks":                "INTEGER",
        "tires":                "INTEGER",
        "lpgTankPin":           "INTEGER",
        "lpgTankHose":          "INTEGER",
        "gasGauge":             "INTEGER",
        "engineOilLevel":       "INTEGER",
        "battery":              "INTEGER",
        "hydraulicFluidLevel":  "INTEGER",
        "engineCoolantLevel":   "INTEGER",
        "glovesarePresent":     "INTEGER",
        "comments":             "TEXT",
        "submitted_at":         "TEXT"
    }


    for col, col_type in desired.items():
        if col not in existing:
            try:
                print(f"🛠 Adding column `{col}` {col_type}")
                c.execute(f"ALTER TABLE audits ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError as e:
                # If it was already added (race or prior run), ignore it
                if "duplicate column name" in str(e).lower():
                    print(f"⚠️ Column `{col}` already exists, skipping")
                else:
                    raise



    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('form.html', today=datetime.today().strftime('%Y-%m-%d'))
@app.route('/submit', methods=['POST'])
def submit():
    data = {
        'date': request.form.get('date'),
        'operator': request.form.get('operator'),
        'forklift_id': request.form.get('forklift_id'),
        'overheadGuard': int(bool(request.form.get('overheadGuard'))),
        'hydraulic_cylinders': int(bool(request.form.get('hydraulic_cylinders'))),
        'mast': int(bool(request.form.get('mast'))),
        'lift_ChainsRollers': int(bool(request.form.get('lift_ChainsRollers'))),
        'forks': int(bool(request.form.get('forks'))),
        'tires': int(bool(request.form.get('tires'))),
        'lpgTankPin': int(bool(request.form.get('lpgTankPin'))),
        'lpgTankHose': int(bool(request.form.get('lpgTankHose'))),
        'gasGauge': int(bool(request.form.get('gasGauge'))),
        'engineOilLevel': int(bool(request.form.get('engineOilLevel'))),
        'battery': int(bool(request.form.get('battery'))),
        'hydraulicFluidLevel': int(bool(request.form.get('hydraulicFluidLevel'))),
        'engineCoolantLevel': int(bool(request.form.get('engineCoolantLevel'))),
        'glovesarePresent': int(bool(request.form.get('glovesarePresent'))),
        'comments': request.form.get('comments'),
        'submitted_at': datetime.now(timezone.utc).isoformat()
    }
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    INSERT INTO audits (
        date, operator,
        forklift_id,
        overheadGuard, hydraulic_cylinders,
        mast, lift_ChainsRollers,
        forks, tires,
        lpgTankPin, lpgTankHose,
        gasGauge, engineOilLevel,
        battery, hydraulicFluidLevel,
        engineCoolantLevel, glovesarePresent,
        comments, submitted_at
    ) VALUES (
        :date, :operator, :forklift_id,
        :overheadGuard, :hydraulic_cylinders,
        :mast, :lift_ChainsRollers,
        :forks, :tires,
        :lpgTankPin, :lpgTankHose,
        :gasGauge, :engineOilLevel,
        :battery, :hydraulicFluidLevel,
        :engineCoolantLevel, :glovesarePresent,
        :comments, :submitted_at   
    )    
    ''', data)
    conn.commit()
    conn.close()
    return render_template('thankyou.html')

@app.route('/audits')
def audits():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
      SELECT
        date,
        operator,
        forklift_id,
        overheadGuard,
        hydraulic_cylinders,
        mast,
        lift_ChainsRollers,
        forks,
        tires,
        lpgTankPin,
        lpgTankHose,
        gasGauge,
        engineOilLevel,
        battery,
        hydraulicFluidLevel,
        engineCoolantLevel,
        glovesarePresent,
        comments,
        submitted_at
      FROM audits
      ORDER BY submitted_at DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return render_template('audits.html', audits=rows)

@app.route('/qr.png')
def qr_png():
    # 1️⃣ Option A: Hard‑code your ngrok URL:
    # public_url = 'https://81caa7a66b2e.ngrok-free.app'
    #
    # 2️⃣ Option B: Read it from PUBLIC_URL env var (recommended):
    #public_url = os.getenv('PUBLIC_URL', request.url_root.rstrip('/'))
    public_url = 'https://e0b7ba8fef2d.ngrok-free.app'
    # Decide which public URL to use
    base = PUBLIC_URL.rstrip('/') or request.url_root.rstrip('/')
    target = f"{base}{url_for('index')}"
    # Generate and send QR
    img = qrcode.make(target)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')


if __name__ == '__main__':
    '''init_db()'''
    # **this guard must be exactly this**
    app.run(host='0.0.0.0', port=5000)


'''date, operator,
overheadGuard, hydraulic_cylinders,
mast, lift_ChainsRollers,
forks, tires,
lpgTankPin, lpgTankHose,
gasGauge, engineOilLevel,
battery, hydraulicFluidLevel,
engineCoolantLevel, glovesarePresent,
comments, submitted_at'''