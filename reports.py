import sqlite3
import matplotlib.pyplot as plt
from database import connect_db
from datetime import datetime, timedelta

def grafik_analizi(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT kategori, COUNT(*) as adet, ABS(SUM(miktar)) as toplam
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.user_id = ? AND a.hesap_tipi = 'Vadesiz' AND t.miktar < 0
            GROUP BY kategori
            ORDER BY toplam DESC
        """, (user_id,))
        
        veriler = cursor.fetchall()
        if not veriler:
            print("\n❌ No spending data found.")
            return
        
        toplam_harcama = sum(item[2] for item in veriler)

        kategoriler = [item[0] for item in veriler]
        toplamlar = [item[2] for item in veriler]

        print("\n--- 📊 SPENDING ANALYSIS (Recent Transactions) ---")
        print(f"Total Spending: {toplam_harcama:.2f} TL\n")

        for kategori, adet, toplam in veriler:
            yuzde = (toplam / toplam_harcama) * 100
            print(f"{kategori:15} {adet:>3} transactions | {yuzde:5.1f}% ({toplam:.2f} TL)")

        plt.figure(figsize=(8, 6))
        plt.bar(kategoriler, toplamlar, color="tab:blue")
        plt.title("Spending Distribution")
        plt.xlabel("Category")
        plt.ylabel("Total Spending (TL)")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def aylik_ozet(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        son_ay = datetime.now() - timedelta(days=30)
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN t.miktar > 0 THEN t.miktar ELSE 0 END) as gelir,
                ABS(SUM(CASE WHEN t.miktar < 0 THEN t.miktar ELSE 0 END)) as gider
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.user_id = ? AND t.tarih >= ?
        """, (user_id, son_ay))
        
        result = cursor.fetchone()
        gelir = result[0] or 0
        gider = result[1] or 0
        fark = gelir - gider
        
        print("\n--- 💰 MONTHLY SUMMARY (Last 30 Days) ---")
        print(f"Total Income: {gelir:.2f} TL ✅")
        print(f"Total Expense: {gider:.2f} TL ❌")
        print(f"Net Balance: {fark:.2f} TL {'✅' if fark >= 0 else '❌'}")

        plt.figure(figsize=(6, 4))
        plt.bar(["Income", "Expense"], [gelir, gider], color=["tab:green", "tab:red"])
        plt.title("Monthly Income - Expense Summary")
        plt.ylabel("TL")
        for index, value in enumerate([gelir, gider]):
            plt.text(index, value + max(gelir, gider) * 0.02, f"{value:.2f}", ha="center")
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def kredi_analizi(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT l.toplam_borc, l.taksit_miktari, l.kalan_taksit_sayisi, 
                   (l.kalan_taksit_sayisi * l.taksit_miktari) as toplam_odenecek
            FROM loans l
            JOIN accounts a ON l.account_id = a.account_id
            WHERE a.user_id = ? AND l.kalan_taksit_sayisi > 0
        """, (user_id,))
        
        krediler = cursor.fetchall()
        if not krediler:
            print("\n✅ No active loans found.")
            return
        
        print("\n--- 🏦 LOAN ANALYSIS ---")
        for i, (toplam_borc, taksit_miktari, kalan_taksit, toplam_odenecek) in enumerate(krediler, 1):
            odenen = toplam_borc - (kalan_taksit * taksit_miktari)
            yuzde = (odenen / toplam_borc * 100) if toplam_borc > 0 else 0
            
            print(f"\nLoan #{i}:")
            print(f"  Total Debt: {toplam_borc:.2f} TL")
            print(f"  Monthly Installment: {taksit_miktari:.2f} TL")
            print(f"  Remaining Installments: {kalan_taksit}")
            print(f"  Remaining Payment: {toplam_odenecek:.2f} TL")
            print(f"  Payment Progress: {yuzde:.1f}% {'█' * int(yuzde/5)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


def islem_gecmisi(user_id, son_n_islem=10):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.trans_id, t.miktar, t.kategori, t.aciklama, t.tarih, a.hesap_tipi
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.user_id = ?
            ORDER BY t.tarih DESC
            LIMIT ?
        """, (user_id, son_n_islem))
        
        islemler = cursor.fetchall()
        if not islemler:
            print("\n❌ No transaction history found.")
            return
        
        print(f"\n--- 📋 LAST {son_n_islem} TRANSACTIONS ---")
        print(f"{'ID':5} {'Amount':12} {'Category':15} {'Account':12} {'Description':20} {'Date':19}")
        print("-" * 90)
        
        for trans_id, miktar, kategori, aciklama, tarih, hesap_tipi in islemler:
            isaret = "+" if miktar > 0 else "-"
            print(f"{trans_id:<5} {isaret}{abs(miktar):>10.2f} TL {kategori:15} {hesap_tipi:12} {aciklama:20} {tarih:19}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def hesap_ozeti(user_id):
   
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT hesap_tipi, bakiye
            FROM accounts
            WHERE user_id = ?
        """, (user_id,))
        
        hesaplar = cursor.fetchall()
        if not hesaplar:
            print("\n❌ No accounts found.")
            return
        
        toplam = sum(item[1] for item in hesaplar)
        
        print("\n--- 🏦 ACCOUNT SUMMARY ---")
        for hesap_tipi, bakiye in hesaplar:
            durum = "✅" if bakiye >= 0 else "⚠️"
            print(f"{durum} {hesap_tipi:12}: {bakiye:12.2f} TL")
        
        print("-" * 30)
        print(f"Total Net: {toplam:12.2f} TL")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()
