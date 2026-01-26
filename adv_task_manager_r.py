# Refaktorovaná verze avd_task_manager_r - 2.projekt
# Vytvořil Martin Nožička

import mysql.connector
from mysql.connector import Error

# Konstanty určené pro hlavni_menu a spustit_spravce_ukolu
PRIDAT_UKOL = 1
ZOBRAZIT_UKOLY = 2
AKTUALIZOVAT_UKOL = 3
ODSTRANIT_UKOL = 4
KONEC = 5

def pripojeni_db():
    """Vrací aktivní DB connection nebo vyhodí vyjímku."""
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1111',
        database='task_manager_db'
    )
    return connection
    
def vytvoreni_tabulky(db):
    if db is None:
        raise RuntimeError("DB není připojena")

    with db.cursor() as cursor:
        sql = f"""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(50) NOT NULL,
            popis VARCHAR(150) NOT NULL,
            stav VARCHAR(20) DEFAULT 'Nezahájeno',
            datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """        
        cursor.execute(sql)
    db.commit()

def vytvorit_ukol(db, nazev, popis):
    if not nazev or not popis:
        raise ValueError("Název a popis nesmí být prázdné.") 

    with db.cursor() as cursor:
        cursor.execute (
            "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s);",(nazev, popis)
            )
    db.commit()

# Přidat úkol - (Funkce č.1)
def pridat_ukol_ui(db):
    nazev = input("Zadej název úkolu:\n").strip()
    popis = input("Zadejte popis úkolu:\n").strip()

    try:
        vytvorit_ukol(db, nazev, popis)
        print(f"✅ Úkol '{nazev}' byl uložen.")
    except ValueError as e:
        print(f"❗ {e}")

# Zobrazení úkolů - (Funkce č.2)
def zobrazit_ukoly(db, pouze_aktivni=True):
    with db.cursor()as cursor:
        if pouze_aktivni:
            sql = f"""
            SELECT id, nazev, popis, stav
            FROM ukoly
            WHERE stav IN ('Nezahájeno', 'Probíhá');
            """
        else:
            sql = "SELECT id, nazev, popis, stav FROM ukoly"

        cursor.execute(sql)
        vysledky = cursor.fetchall()

    if not vysledky:
        if pouze_aktivni:
            print("⚠️  Žádné nezahájené nebo probíhající úkoly k zobrazení.")
        else:
            print("⚠️  V databázi nejsou žádné úkoly.")
        return False

    for id, nazev, popis, stav in vysledky:
        print(f"ID: {id} | {nazev} - {popis} [{stav}]")

    return True

def update_ukolu(db, id_ukolu, novy_stav):
    if novy_stav not in ('Nezahájeno', 'Probíhá', 'Hotovo'):
        raise ValueError("Neplatný stav úkolu.")
    
    with db.cursor() as cursor:
        cursor.execute(
            "UPDATE ukoly SET stav = %s WHERE id = %s;",(novy_stav, id_ukolu)
        )
    db.commit()

# Aktualizovat úkol - (Funkce č.3)
def aktualizovat_ukol(db):
    while True:
        if not zobrazit_ukoly(db, pouze_aktivni=False):
            print("⚠️  Nejsou dostupné žádné nedokončené úkoly.")
            return

        vstup = input("\nZadejte ID úkolu pro změnu stavu (nebo '0' pro návrat):\n") 
        if vstup == "0":
            return

        try:
            id_ukolu = int(vstup)
        except ValueError:
            print("⚠️  ID musí být číslo.")
            continue

        with db.cursor() as cursor:
            cursor.execute("SELECT nazev FROM ukoly WHERE id = %s;", (id_ukolu,))
            vysledek = cursor.fetchone()

        if not vysledek:
            print(f"⚠️  Úkol s ID {id_ukolu} neexistuje. Zvolte možnost z výpisu.")
            continue
        print("\n===>Výběr stavu<==")
        print("Vyberte nový stav:")
        print("1. Probíhá")
        print("2. Hotovo")
        print("<================>")
        volba_stavu = input("Vyberte (1/2:)\n").strip()

        if volba_stavu == "1": 
            novy_stav = "Probíhá"
        elif volba_stavu == "2": 
            novy_stav = "Hotovo"
        else:
            print("❗Neplatná volba stavu.")
            continue

        update_ukolu(db, id_ukolu, novy_stav)
        print(f"✅  Stav úkolu ID {id_ukolu} byl změněn na: {novy_stav}.")
        break

# Odstranit úkol - (Funkce č.4)
def odstranit_ukol(db):
    while True:
        if not zobrazit_ukoly(db, pouze_aktivni=False):
            print("⚠️  Nejsou žádné úkoly ke smazání.")
            return

        vstup = input("\nZadejte ID úkolu ke smazání (nebo '0' pro návrat):\n").strip()
        if vstup == '0':
            return
        try:
            id_ukolu = int(vstup)
        except ValueError:
            print("❗ Zadejte platné číslo ID.")
            continue
        
        with db.cursor() as cursor:
            cursor.execute("SELECT nazev FROM ukoly WHERE id = %s;",(id_ukolu,))
            vysledek = cursor.fetchone()

        if not vysledek:
            print(f"⚠️  Úkol s ID {id_ukolu} neexistuje. Zvolte číslo uvedené ve výpisu.")
            continue

        nazev_ukolu = vysledek[0]
        potvrzeni = input(f"Opravdu chcete trvale smazat úkol '{nazev_ukolu}'? (a/n):\n").lower().strip()

        # Odstranil jsem funkci na tvrdý reset ID v DB. Nyní se identifikátor pouze smaže.
        if potvrzeni == 'a':
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM ukoly WHERE id = %s;", (id_ukolu,))
                db.commit()
                print(f"✅  Úkol '{nazev_ukolu}' byl trvale odstraněn.")
                break
                
        elif potvrzeni == 'n':
            print("⚠️  Smazání zrušeno.")
            break
        else:
            print("⚠️  Neplatná volba. Zvolte 'a' nebo 'n'")
            continue
        
# funkce pro hlavní menu s konstantami
def hlavni_menu():
    print("\n===> Správce úkolů - Hlavní menu <===")
    print(f"{PRIDAT_UKOL}. Přidat úkol")
    print(f"{ZOBRAZIT_UKOLY}. Zobrazit úkoly")
    print(f"{AKTUALIZOVAT_UKOL}. Aktualizovat úkol")
    print(f"{ODSTRANIT_UKOL}. Odstranit úkol")
    print(f"{KONEC}. Ukončit program")
    print("=====================================")

    while True:
        try:
            volba = int(input("Vyberte možnost (1-5):\n"))
            if volba in (PRIDAT_UKOL, ZOBRAZIT_UKOLY, AKTUALIZOVAT_UKOL, ODSTRANIT_UKOL, KONEC):
                return volba
            else:
                print("❗ Chyba: Číslo musí být mezi 1 a 5.")
        except ValueError:
            print("❗ Chyba: Vybete číslo mezi 1 a 5.")

def spustit_spravce_ukolu():
    db = pripojeni_db()
    if db is None:
        print("❌ Nepodařilo se připojit k databázi")
        return

    try:
        vytvoreni_tabulky(db)
        while True:
            volba = hlavni_menu()
            
            if volba == PRIDAT_UKOL:
                pridat_ukol_ui(db)

            elif volba == ZOBRAZIT_UKOLY:
                zobrazit_ukoly(db)

            elif volba == AKTUALIZOVAT_UKOL:
                aktualizovat_ukol(db)

            elif volba == ODSTRANIT_UKOL:
                odstranit_ukol(db)

            elif volba == KONEC:
                print("Konec programu.")
                break

    except mysql.connector.Error as e:
        print(f"❌ Chyba v databázi: {e}")
    except Exception as e:
        print(f"❌  Neočekávaná chyba: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    spustit_spravce_ukolu()