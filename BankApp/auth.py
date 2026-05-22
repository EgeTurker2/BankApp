import sqlite3
from database import connect_db

def register_user(ad_soyad, email, sifre):
    conn = connect_db()
    if conn is None: return False
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (ad_soyad, email, sifre) VALUES (?, ?, ?)", 
            (ad_soyad, email, sifre)
        )
        user_id = cursor.lastrowid
        
        hesaplar = [('Vadesiz', 0.0), ('Yatirim', 0.0), ('Kredi', 0.0)]
        for tip, bakiye in hesaplar:
            cursor.execute(
                "INSERT INTO accounts (user_id, hesap_tipi, bakiye) VALUES (?, ?, ?)", 
                (user_id, tip, bakiye)
            )
        
        conn.commit()
        print(f"\n✅ Registration successful! 3 accounts (Current, Investment, Loan) have been created.")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        conn.close()

def login_user(email, sifre):
    conn = connect_db()
    if conn is None: return None
    
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, ad_soyad FROM users WHERE email = ? AND sifre = ?", 
        (email, sifre)
    )
    user = cursor.fetchone()
    conn.close()
    
    return user