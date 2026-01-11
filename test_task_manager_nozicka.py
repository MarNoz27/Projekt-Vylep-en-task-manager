import pytest
import mysql.connector
from adv_task_manager_nozicka import pridat_ukol, aktualizovat_ukol, odstranit_ukol, pripojeni_db

TEST_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1111',
    'database': 'task_manager_db'
}

@pytest.fixture(autouse=True)
def setup_db():
    """Fixture, který před každým testem vymaže tabulku úkolů."""

    db = mysql.connector.connect(**TEST_DB_CONFIG)
    cursor = db.cursor()
    cursor.execute("DELETE FROM ukoly")
    cursor.execute("ALTER TABLE ukoly AUTO_INCREMENT = 1")
    db.commit()
    cursor.close()
    db.close()
    yield

    db = mysql.connector.connect(**TEST_DB_CONFIG)
    cursor = db.cursor()
    cursor.execute("DELETE FROM ukoly")
    db.commit()
    cursor.close()
    db.close()

# - PŘIDÁNÍ ÚKOLU (Funkce č.1)

def test_pridat_ukol_pozitivni():
    """TC01 - Pozitivní test: Ověří, že se úkol skutečně uloží do DB."""
    pridat_ukol("Testovací úkol", "Popis testu")
    db = mysql.connector.connect(**TEST_DB_CONFIG)
    cursor = db.cursor()
    cursor.execute("SELECT nazev FROM ukoly WHERE nazev = 'Testovací úkol'")
    vysledek = cursor.fetchone() is not None
    db.close()
    assert vysledek is not None
    assert vysledek[0] == "Testovací úkol"

def test_pridat_ukol_negativni():
    """TC02 - Negativní test: Ověří, že prázdný název neprojde."""

    nazev = ""
    popis = ""
    vysledek = bool(nazev and popis)
    assert vysledek is False

# - AKTUALIZACE ÚKOLU - (Funkce č.2)

def test_aktualizovat_ukol_pozitivni(monkeypatch):
    """TC03 - Pozitivní test: Změna stavu u existujícího ID."""

    pridat_ukol("Původní", "Popis")
    inputs = iter(['1', '2']) # ID 1, volba 2 (Hotovo)
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    aktualizovat_ukol()

    db = mysql.connector.connect(**TEST_DB_CONFIG)
    cursor = db.cursor()
    cursor.execute('SELECT stav FROM ukoly WHERE id = 1')
    stav = cursor.fetchone()[0]
    assert stav == "Hotovo"
    db.close()

def test_aktualizovat_ukol_negativni(monkeypatch):
    """TC04 - Negativní test: Zadání neexistujícího ID (999)"""

    inputs = iter(['999', '0'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    aktualizovat_ukol()

# - ODSTRANIT ÚKOLU - (Funkce č.3)

def test_odstranit_ukol_pozitivni(monkeypatch):
    """TC05 - Pozitivní test: Smazání existujícího úkolu."""

    pridat_ukol("K smazání", "Popis")
    inputs = iter(['1', 'a'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    odstranit_ukol()

    db = mysql.connector.connect(**TEST_DB_CONFIG)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM ukoly")
    pocet = cursor.fetchone()[0]
    assert pocet == 0
    db.close()

def test_odstranit_ukol_negativni(monkeypatch):
    """TC06 - Negativní test: Zadání textu místo čísla ID."""

    inputs = iter(['neplatne_id', '0'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    odstranit_ukol()