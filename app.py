from flask import Flask, render_template, request, redirect, url_for, session
import uuid  # Untuk membuat ID pengguna unik
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_here'  # Ganti dengan kunci rahasia yang kuat dan unik

# Fungsi untuk menyimpan informasi pengguna (dapat diganti dengan database)
users = {}

# Fungsi bantu untuk menyimpan pengguna ke dalam struktur data (dapat diganti dengan database)
def save_user(username, password):
    user_id = str(uuid.uuid4())  # Buat ID pengguna unik
    if username not in users:
        users[username] = {'user_id': user_id, 'password': password, 'balance': 10000000.0}  # Set saldo awal 10.000.000

def save_transaction(username, description, amount):
    global transactions
    transaction = {'username': username, 'description': description, 'amount': amount, 'date': datetime.now()}  # Tambahkan informasi tanggal
    transactions.append(transaction)

# Fungsi bantu untuk mentransfer saldo dari satu pengguna ke pengguna lain
def transfer_money(from_user, to_user, amount):
    if from_user in users and to_user in users:
        if users[from_user]['balance'] >= amount:
            users[from_user]['balance'] -= amount
            users[to_user]['balance'] += amount
            return True
    return False

# Fungsi untuk menyimpan transaksi
transactions = []

# Halaman index (hanya bisa diakses setelah login)
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Jika belum login, arahkan ke halaman login

    # Di sini bisa diletakkan logika untuk menampilkan informasi pengguna
    user_id = session['user_id']
    usernames = [username for username, user in users.items() if user['user_id'] == user_id]
    if usernames:  # Pastikan list tidak kosong sebelum mengambil nama pengguna
        username = usernames[0]  # Ambil nama pengguna dari list jika ada
        balance = users[username]['balance']
        total_income = sum(transaction['amount'] for transaction in transactions if transaction['username'] == username and transaction['amount'] > 0)
        total_expense = abs(sum(transaction['amount'] for transaction in transactions if transaction['username'] == username and transaction['amount'] < 0))
        return render_template('index.html', user={'name': username}, balance=balance, total_income=total_income, total_expense=total_expense, transactions=transactions)
    else:
        # Jika ID pengguna tidak ditemukan, redirect ke halaman login
        return redirect(url_for('login'))

# Halaman register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))  # Jika sudah login, arahkan ke halaman index

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Simpan informasi pengguna baru
        save_user(username, password)
        return redirect(url_for('login'))  # Redirect ke halaman login setelah pendaftaran berhasil

    return render_template('register.html')

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))  # Jika sudah login, arahkan ke halaman index

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Memeriksa keberadaan pengguna dan validasi password
        if username in users and users[username]['password'] == password:
            session['user_id'] = users[username]['user_id']  # Simpan ID pengguna dalam session
            return redirect(url_for('index'))  # Redirect ke halaman index setelah login berhasil

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login')) # Redirect ke halaman login setelah logout berhasil

@app.route('/transfer', methods=['POST'])
def transfer_money():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect jika pengguna belum login

    if request.method == 'POST':
        from_user_id = session['user_id']
        from_user = next((username for username, user in users.items() if user['user_id'] == from_user_id), None)
        to_user = request.form['to_user']
        amount = float(request.form['amount'])

        if not from_user:
            return "Pengguna tidak ditemukan."

        if to_user not in users:
            return "Penerima tidak ditemukan."

        if to_user == from_user:
            return "Anda tidak dapat mentransfer uang kepada diri sendiri."

        if users[from_user]['balance'] < amount:
            return "Saldo tidak mencukupi untuk transfer."

        users[from_user]['balance'] -= amount
        users[to_user]['balance'] += amount

        # Simpan transaksi pada sistem
        save_transaction(from_user, f"Transfer ke {to_user}", -amount)
        save_transaction(to_user, f"Transfer dari {from_user}", amount)

        return redirect(url_for('index'))

@app.route('/transaction_history')
def transaction_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect jika pengguna belum login
    
    user_id = session['user_id']
    usernames = [username for username, user in users.items() if user['user_id'] == user_id]
    if usernames:  
        username = usernames[0] 
        user_transactions = [transaction for transaction in transactions if transaction['username'] == username]
        return render_template('transaction_history.html', user={'name': username}, transactions=user_transactions)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
