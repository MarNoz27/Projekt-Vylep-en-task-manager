import mysql.connector
from mysql.connector import Error

def pripojeni_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1111',
            database='task_manager_db'
        )
        return connection
    except Error as e:
        print(f"Chyba připojení: {e}")
        return None
    
def vytvoreni_tabulky():
    db = pripojeni_db()
    if db:
        try:
            cursor = db.cursor()
            sql = """
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(50) NOT NULL,
                popis VARCHAR(150) NOT NULL,
                stav VARCHAR(20) DEFAULT 'Nezahájeno',
                datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(sql)
        except Error as e:
            print(f"Chyba při inicializaci tabulky: {e}")
        finally:
            cursor.close()
            db.close()

def pridat_ukol(nazev, popis):
    db = pripojeni_db()
    if db:
        try:
            cursor = db.cursor()
            sql = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"
            hodnoty = (nazev, popis)
            cursor.execute(sql, hodnoty)
            db.commit()
            print(f"✅ Úkol '{nazev}' byl uspěšně uložen do databáze.")

        except mysql.connector.Error as e:
            print(f"❌ Nepodařilo se ořidat úkol: {e}")
        finally:
            if 'cursor' in locals ():
                cursor.close()
            db.close()

def zobrazit_ukoly(pouze_aktivni=True):
    db = pripojeni_db()
    if db:
        try:
            cursor = db.cursor()
            if pouze_aktivni:
                sql = "SELECT id, nazev, popis, stav FROM ukoly WHERE stav IN ('Nezahájeno', 'Probíhá')"
            else:
                sql = "SELECT id, nazev, popis, stav FROM ukoly"

            cursor.execute(sql)
            vysledky = cursor.fetchall()

            if not vysledky:
                if pouze_aktivni:
                    print("\n⚠️  Žádné aktivní úkoly k zobrazení")
                else:
                    print("\n⚠️  V databázi nejsou žádné úkoly.")
                return False

            nadpis = "AKTIVNÍ ÚKOLY" if pouze_aktivni else "SEZNAM VŠECH ÚKOLŮ"
            print(f"\n-----{nadpis}-----")
            for (id, nazev, popis, stav) in vysledky:
                print(f"ID: {id} | {nazev} - {popis} [{stav}]")
            print("----------------------")
            return True
            
        finally:
            cursor.close()
            db.close()
    return False

def aktualizovat_ukol():
    while True:
        if not zobrazit_ukoly(pouze_aktivni=False):
            return

        try:
            vstup = input("\nZadejte ID úkolu pro změnu stavu (nebo '0' pro návrat):\n")
            if vstup == '0': 
                break
        
            id_ukolu = int(vstup)
            db = pripojeni_db()

            if db:
                try:
                    cursor = db.cursor()
                    cursor.execute("SELECT id FROM ukoly WHERE id = %s", (id_ukolu,))
                    if not cursor.fetchone():
                        print(f"⚠️  Úkol s ID {id_ukolu} neexistuje.⚠️ Vyberte číslo ze seznamu úkolů.")
                        continue

                    print("Vyberte nový stav:")
                    print("1. Probíhá")
                    print("2. Hotovo")
                    volba_stavu = input("Vyberte (1/2:)\n")

                    novy_stav = ""
                    if volba_stavu == "1": 
                        novy_stav = "Probíhá"
                    elif volba_stavu == "2": 
                        novy_stav = "Hotovo"

                    if novy_stav:
                        cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
                        db.commit()
                        print(f"✅  Stav úkolu ID {id_ukolu} byl změněn na: {novy_stav}")
                        break

                finally:
                    if 'cursor' in locals():
                        cursor.close()
                    db.close()

        except ValueError:
            print("❗  Chyba: Neplatný vstup. ID musí být číslo!")

def odstranit_ukol():
    while True:
        if not zobrazit_ukoly(pouze_aktivni=False):
            return

        try:
            vstup = input("\nZadejte ID úkolu ke smazání (nebo '0' pro návrat):\n")
            if vstup == '0':
                break

            id_ukolu = int(vstup)
            db = pripojeni_db()

            if db:
                try:
                    cursor = db.cursor()
                    cursor.execute("SELECT nazev FROM ukoly WHERE id = %s", (id_ukolu,))
                    vysledek = cursor.fetchone()

                    if not vysledek:
                        print(f"⚠️  Úkol s ID {id_ukolu} neexistuje. Zkuste to znovu.")
                        continue

                    nazev_ukolu = vysledek[0]
                    potvrzeni = input(f"Opravdu chcete trvale smazat úkol '{nazev_ukolu}'? (a/n):\n").lower()

                    if potvrzeni == 'a':
                        sql_delete = "DELETE FROM ukoly WHERE id = %s"
                        cursor.execute(sql_delete, [id_ukolu])
                        cursor.execute("SET @count = 0;")
                        cursor.execute("UPDATE ukoly SET id = (@count := @count + 1);")
                        cursor.execute("ALTER TABLE ukoly AUTO_INCREMENT = 1;")

                        db.commit()
                        print(f"✅  Úkol '{nazev_ukolu}' byl trvale odstraněn.")
                        break
                    else:
                        print("Smazání zrušeno.")
                        break
                finally:
                    if 'cursor' in locals():
                        cursor.close()
                    db.close()

        except ValueError:
            print("❗ Chyba! Zadejte platné číslo ID.")

def hlavni_menu():
    print("\nSprávce úkolů - Hlavní menu")
    print("1. Přidat úkol")
    print("2. Zobrazit úkoly")
    print("3. Aktualizovat úkol")
    print("4. Odstranit úkol")
    print("5. Ukončit program")

def spustit_spravce_ukolu():
    vytvoreni_tabulky()
    while True:
        hlavni_menu()
        try:
            volba = int(input("Vyberte možnost (1-5):\n"))

            if volba == 1:
                nazev = input("Zadejte název úkolu:\n").strip()
                popis = input("Zadejte popis úkolu:\n").strip()
                if nazev and popis:
                    pridat_ukol(nazev, popis)
                else:
                    print("Název i popis musí být vyplněny!")

            elif volba == 2:
                zobrazit_ukoly()

            elif volba == 3:
                aktualizovat_ukol()

            elif volba == 4:
                odstranit_ukol()

            elif volba == 5:
                    print("Konec programu.")
                    break
            else:
                print("❗Neplatná volba❗ Vybete možnost 1-5.")

        except ValueError:
            print("Chyba: Zadejte prosím číslo od 1 do 5.")

if __name__ == "__main__":
    spustit_spravce_ukolu()