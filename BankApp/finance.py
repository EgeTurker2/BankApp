import sqlite3
from database import connect_db

def hesaplari_listele(user_id):
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT hesap_tipi, bakiye FROM accounts WHERE user_id = ?", (user_id,))
    hesaplar = cursor.fetchall()
    conn.close()
    
    print("\n--- 🏦 ACCOUNT STATUS ---")
    for tip, bakiye in hesaplar:
        print(f"📌 {tip} Account: {bakiye:.2f} TL")

def para_ekle(user_id, hesap_tipi, miktar, kategori, aciklama):
    
    conn = connect_db()
    cursor = conn.cursor()
    try:
        
        cursor.execute("UPDATE accounts SET bakiye = bakiye + ? WHERE user_id = ? AND hesap_tipi = ?", 
                       (miktar, user_id, hesap_tipi))
        
        cursor.execute("SELECT account_id FROM accounts WHERE user_id = ? AND hesap_tipi = ?", (user_id, hesap_tipi))
        acc_id = cursor.fetchone()[0]
        
        cursor.execute("INSERT INTO transactions (account_id, miktar, kategori, aciklama) VALUES (?, ?, ?, ?)",
                       (acc_id, miktar, kategori, aciklama))
        
        conn.commit()
        print(f"✅ {miktar} TL deposited successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def ic_transfer(user_id, kaynak_tip, hedef_tip, miktar):
    
    conn = connect_db()
    cursor = conn.cursor()
    try:
        
        cursor.execute("SELECT bakiye FROM accounts WHERE user_id = ? AND hesap_tipi = ?", (user_id, kaynak_tip))
        mevcut = cursor.fetchone()[0]
        
        if mevcut < miktar:
            print("❌ Insufficient funds!")
            return

        
        cursor.execute("UPDATE accounts SET bakiye = bakiye - ? WHERE user_id = ? AND hesap_tipi = ?", (miktar, user_id, kaynak_tip))
        cursor.execute("UPDATE accounts SET bakiye = bakiye + ? WHERE user_id = ? AND hesap_tipi = ?", (miktar, user_id, hedef_tip))
        
        conn.commit()
        print(f"✅ {kaynak_tip} -> {hedef_tip} transfer completed.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def dis_transfer(gonderen_id, alici_email, miktar):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (alici_email,))
        alici = cursor.fetchone()
        if not alici:
            print("❌ Error: No user found with that email.")
            return

        alici_id = alici[0]

        cursor.execute("SELECT bakiye, account_id FROM accounts WHERE user_id = ? AND hesap_tipi = 'Vadesiz'", (gonderen_id,))
        g_data = cursor.fetchone()
        if g_data[0] < miktar:
            print("❌ Insufficient funds!")
            return

        g_acc_id = g_data[1]


        cursor.execute("UPDATE accounts SET bakiye = bakiye - ? WHERE account_id = ?", (miktar, g_acc_id))
        
        cursor.execute("UPDATE accounts SET bakiye = bakiye + ? WHERE user_id = ? AND hesap_tipi = 'Vadesiz'", (miktar, alici_id))
        
        
        cursor.execute("INSERT INTO transactions (account_id, miktar, kategori, aciklama) VALUES (?, ?, 'Transfer', ?)",
                   (g_acc_id, -miktar, f"Outgoing Transfer: {alici_email}"))

        conn.commit()
        print(f"✅ {miktar} TL successfully sent to {alici_email}.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Transfer failed: {e}")
    finally:
        conn.close()

def para_cek(user_id, hesap_tipi, miktar, kategori):

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT bakiye, account_id FROM accounts WHERE user_id=? AND hesap_tipi=?", (user_id, hesap_tipi))
        data = cursor.fetchone()
        if data[0] < miktar:
            print("❌ Insufficient funds!")
            return
        
        cursor.execute("UPDATE accounts SET bakiye = bakiye - ? WHERE account_id=?", (miktar, data[1]))
        cursor.execute("INSERT INTO transactions (account_id, miktar, kategori, aciklama) VALUES (?, ?, ?, ?)", 
                       (data[1], -miktar, kategori, "Withdrawal"))
        conn.commit()
        print(f"✅ {miktar} TL withdrawn. Category: {kategori}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def faiz_hesapla(user_id, yillik_oran, ay_sayisi):
    
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT bakiye FROM accounts WHERE user_id=? AND hesap_tipi='Yatirim'", (user_id,))
        row = cursor.fetchone()
        if row is None:
            print("❌ Investment account not found. Please create an investment account first.")
            return
        bakiye = row[0]
        conn.close()
        
        
        if ay_sayisi <= 0:
            print("❌ Number of months must be 1 or greater.")
            return
        if yillik_oran < 0:
            print("❌ Interest rate cannot be negative.")
            return
        aylik_oran = yillik_oran / 100 / 12
        faiz = bakiye * aylik_oran * ay_sayisi
        toplam = bakiye + faiz
        
        print(f"\n--- 📊 INTEREST CALCULATION ---")
        print(f"Starting Balance: {bakiye:.2f} TL")
        print(f"Annual Interest Rate: {yillik_oran}%")
        print(f"Period: {ay_sayisi} months")
        print(f"Interest Earned: {faiz:.2f} TL")
        print(f"Resulting Amount: {toplam:.2f} TL")
    except Exception as e:
        print(f"❌ Error: {e}")





def kredi_basvurusu(user_id, istenen_tutar, taksit_suresi):
    
    conn = connect_db()
    cursor = conn.cursor()
    try:
        
        cursor.execute("SELECT account_id FROM accounts WHERE user_id=? AND hesap_tipi='Kredi'", (user_id,))
        kredi_acc = cursor.fetchone()
        if not kredi_acc:
            print("❌ Loan account not found!")
            return
        
        kredi_acc_id = kredi_acc[0]
        
        faiz_orani = 0.15
        toplam_tutar = istenen_tutar * (1 + faiz_orani)
        taksit_miktari = toplam_tutar / taksit_suresi
        
        
        cursor.execute("INSERT INTO loans (account_id, toplam_borc, taksit_miktari, kalan_taksit_sayisi) VALUES (?, ?, ?, ?)",
                       (kredi_acc_id, toplam_tutar, taksit_miktari, taksit_suresi))
        
       
        cursor.execute("UPDATE accounts SET bakiye = bakiye + ? WHERE account_id=?", (istenen_tutar, kredi_acc_id))
        
        conn.commit()
        print(f"\n--- 💳 LOAN APPLICATION APPROVED ---")
        print(f"Requested Amount: {istenen_tutar:.2f} TL")
        print(f"Interest Rate: {faiz_orani*100}%")
        print(f"Total Repayment: {toplam_tutar:.2f} TL")
        print(f"Repayment Period: {taksit_suresi} months")
        print(f"Monthly Installment: {taksit_miktari:.2f} TL")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        conn.close()