import sqlite3

def connect_db():
    
    try:
        conn = sqlite3.connect('banka.db')
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    
    conn = connect_db()
    if conn is None:
        return

    cursor = conn.cursor()


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ad_soyad TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        sifre TEXT NOT NULL
    )
    ''')

   
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        hesap_tipi TEXT CHECK(hesap_tipi IN ('Vadesiz', 'Yatirim', 'Kredi')),
        bakiye REAL DEFAULT 0.0,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    )
    ''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        miktar REAL NOT NULL,
        kategori TEXT,
        aciklama TEXT,
        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
    )
    ''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        odeme_adi TEXT NOT NULL,
        miktar REAL NOT NULL,
        odeme_gunu INTEGER CHECK(odeme_gunu BETWEEN 1 AND 31),
        FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
    )
    ''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        toplam_borc REAL NOT NULL,
        taksit_miktari REAL NOT NULL,
        kalan_taksit_sayisi INTEGER NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database and tables successfully checked/created.")

if __name__ == "__main__":
    init_db()