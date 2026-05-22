import database
import auth
import finance
import reports
import sys

def vadesiz_menu(user_id, ad_soyad):
    while True:
        print(f"\n--- 💳 CURRENT ACCOUNT | {ad_soyad} ---")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money (Categorized)")
        print("4. Send Money to Another User (Email)")
        print("5. Transfer Between My Accounts")
        print("6. Spending Analysis (Chart)")
        print("7. Recent Transactions")
        print("0. Back to Account Selection")
        
        secim = input("Choice: ")
        if secim == "1": finance.hesaplari_listele(user_id)
        elif secim == "2":
            miktar = float(input("Amount: "))
            finance.para_ekle(user_id, "Vadesiz", miktar, "Income", "Deposit")
        elif secim == "3":
            miktar = float(input("Amount: "))
            kat = input("Category (Food/Bills/Entertainment/Transport/Other...): ")
            finance.para_cek(user_id, "Vadesiz", miktar, kat)
        elif secim == "4":
            mail = input("Recipient Email: ")
            miktar = float(input("Amount: "))
            finance.dis_transfer(user_id, mail, miktar)
        elif secim == "5":
            hedef = input("Target Account (Yatirim/Kredi): ")
            miktar = float(input("Amount: "))
            finance.ic_transfer(user_id, "Vadesiz", hedef, miktar)
        elif secim == "6": reports.grafik_analizi(user_id)
        elif secim == "7": reports.islem_gecmisi(user_id, 10)
        elif secim == "0": break

def yatirim_menu(user_id, ad_soyad):
    while True:
        print(f"\n--- 📈 SAVINGS/INVESTMENT ACCOUNT | {ad_soyad} ---")
        print("1. Investment Balance")
        print("2. Calculate Interest/Return")
        print("3. Transfer Back to Current Account")
        print("0. Back to Account Selection")
        
        secim = input("Choice: ")
        if secim == "1": finance.hesaplari_listele(user_id)
        elif secim == "2":
            oran = float(input("Annual Interest Rate (%): "))
            ay = int(input("Number of Months: "))
            finance.faiz_hesapla(user_id, oran, ay)
        elif secim == "3":
            miktar = float(input("Amount: "))
            finance.ic_transfer(user_id, "Yatirim", "Vadesiz", miktar)
        elif secim == "0": break

def kredi_menu(user_id, ad_soyad):
    while True:
        print(f"\n--- 🏦 LOAN ACCOUNT | {ad_soyad} ---")
        print("1. Loan Status")
        print("2. New Loan Application Simulation")
        print("3. Detailed Loan Analysis")
        print("0. Back to Account Selection")
        
        secim = input("Choice: ")
        if secim == "1":
            finance.hesaplari_listele(user_id)
        elif secim == "2":
            tutar = float(input("Requested Amount: "))
            ay = int(input("Repayment Period (Months): "))
            finance.kredi_basvurusu(user_id, tutar, ay)
        elif secim == "3":
            reports.kredi_analizi(user_id)
        elif secim == "0": break

def dashboard(user_id, ad_soyad):
    """First stop after login: Account Selection"""
    while True:
        print(f"\n==========================================")
        print(f"       MAIN DASHBOARD - WELCOME {ad_soyad.upper()}")
        print(f"==========================================")
        print("1. 💳 Current Account Operations")
        print("2. 📈 Savings & Investment Operations")
        print("3. 🏦 Loan & Debt Operations")
        print("4. 📊 General Reports & Analysis")
        print("0. Secure Exit (Main Menu)")
        
        hesap_secim = input("Select the account you want to operate: ")

        if hesap_secim == "1": vadesiz_menu(user_id, ad_soyad)
        elif hesap_secim == "2": yatirim_menu(user_id, ad_soyad)
        elif hesap_secim == "3": kredi_menu(user_id, ad_soyad)
        elif hesap_secim == "4": rapor_menu(user_id, ad_soyad)
        elif hesap_secim == "0": break

def rapor_menu(user_id, ad_soyad):
    """General Reports and Analysis Menu"""
    while True:
        print(f"\n--- 📊 REPORTS & ANALYSIS | {ad_soyad} ---")
        print("1. Spending Analysis (Chart)")
        print("2. Monthly Summary (Income-Expense)")
        print("3. Loan Analysis")
        print("4. Account Summary")
        print("5. Recent Transactions")
        print("0. Back")
        
        secim = input("Choice: ")
        if secim == "1": reports.grafik_analizi(user_id)
        elif secim == "2": reports.aylik_ozet(user_id)
        elif secim == "3": reports.kredi_analizi(user_id)
        elif secim == "4": reports.hesap_ozeti(user_id)
        elif secim == "5": 
            n = int(input("How many transactions would you like to see? "))
            reports.islem_gecmisi(user_id, n)
        elif secim == "0": break

def main():
    database.init_db()
    while True:
        print("\n1. Login\n2. Register\n3. Quit")
        secim = input("Choice: ")
        if secim == "1":
            email = input("Email: ")
            sifre = input("Password: ")
            user = auth.login_user(email, sifre)
            if user: dashboard(user[0], user[1])
        elif secim == "2":
            ad = input("Full Name: ")
            email = input("Email: ")
            sifre = input("Password: ")
            auth.register_user(ad, email, sifre)
        elif secim == "3": sys.exit()

if __name__ == "__main__":
    main()