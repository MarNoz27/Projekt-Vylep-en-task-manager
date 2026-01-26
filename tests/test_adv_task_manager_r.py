# Sada automatizovaných testů k aplikaci adv_task_manager_r - 2. verze
# Vytvořil Martin Nožička

import pytest
import builtins
from unittest.mock import MagicMock
from adv_task_manager_r import pridat_ukol_ui, aktualizovat_ukol, odstranit_ukol

# Pozitivní test funkce č.1
@pytest.mark.positive
def test_pridat_ukol_positive(monkeypatch):
    """TEST 01 - Přidání úkolu (pozitivní případ)
    Uživatel zadá platný název a popis úkolu.
    Očekává se potvrzení uložení nového úkolu.)"""

    # ARRANGE
    ts_inputs = iter(["TEST 01 - Testovací text 01", "Popis 01"])
    monkeypatch.setattr(builtins, "input", lambda _: next(ts_inputs))

    fake_cursor = MagicMock()
    fake_db = MagicMock()
    fake_db.cursor.return_value.__enter__.return_value = fake_cursor

    # ACT
    pridat_ukol_ui(fake_db)

    # ASSERT
    fake_cursor.execute.assert_called_once()
    fake_db.commit.assert_called_once()

# Nezativní test fukce č.1
@pytest.mark.negative
def test_pridat_ukol_negative(monkeypatch):
    """TEST 02 - Přidání úkolu (negativní případ)
    Uživatel vloží prázdný vstup.
    Očekává se, že se úkol neuloží a DB operace neproběhne. 
    Aplikace zastaví operaci hláškou, že název a popis nesmí být prázdné."""

    # ARRANGE
    ts_inputs = iter(["", ""])
    monkeypatch.setattr(builtins, "input", lambda _: next(ts_inputs))

    fake_cursor = MagicMock()
    fake_db = MagicMock()
    fake_db.cursor.return_value.__enter__.return_value = fake_cursor

    # ACT
    pridat_ukol_ui(fake_db)

    # ASSERT
    fake_cursor.execute.assert_not_called()
    fake_db.commit.assert_not_called()

# Pozitivní test funkce č:3
@pytest.mark.positive
def test_aktualizovat_ukol_positive(monkeypatch):
    """TEST 03 - Aktualizace úkolů - pozitivní test.
    Uživatel změní stav dvou úkoů na 'Probíhá' a 'Hotovo'.
    Očekává se úspěšná změna stavu úkolů na oba zmíněné stavy."""

    # ARRANGE
    ts_inputs = iter(["1", "1", "2", "2", "0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(ts_inputs))

    fake_cursor =MagicMock()
    fake_cursor.fetchone.side_effect = [("Úkol 01",),("Úkol 02",)]

    fake_db = MagicMock()
    fake_db.cursor.return_value.__enter__.return_value = fake_cursor

    update_mock = MagicMock()
    monkeypatch.setattr("adv_task_manager_r.update_ukolu", update_mock)

    # ACT
    aktualizovat_ukol(fake_db) # Volání pro 'Úkol 01'
    aktualizovat_ukol(fake_db) # Volání pro 'Úkol 02'

    # ASSERT
    assert update_mock.call_args_list == [
        ((fake_db, 1, "Probíhá"),),
        ((fake_db, 2, "Hotovo"),)
    ]

# Negativní test funkce č:3
@pytest.mark.negative
def test_aktualizovat_ukol_neagtive(monkeypatch):
    """TEST 04 - Aktualizace úkolu - Negativní test.
    Uživatel zvolí neexistující ID úkolu.
    Očekávíéá se od funkce by měla vypsat hlášku o neexistujím ID."""

    # ARRANGE
    ts_imputs = iter(["777", "abs", "0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(ts_imputs))

    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = None

    fake_db = MagicMock()
    fake_db.cursor.return_value.__enter__.return_value = fake_cursor

    update_mock = MagicMock()
    monkeypatch.setattr("adv_task_manager_r.update_ukolu", update_mock)

    # ACT
    aktualizovat_ukol(fake_db)

    # ASSERT
    update_mock.assert_not_called()

# Pozitivní test funkce č.4
@pytest.mark.positive
def test_odstranit_ukol_positive(monkeypatch):
    """Test 05 - Odstranit úkol - pozitivní test.
    Uživatel odstraní uložený úkol.
    Očekává se potvrzení o odstranění úkolu."""

    # ARRANGE
    ts_inputs = iter(["1", "a"])
    monkeypatch.setattr(builtins, "input", lambda _: next(ts_inputs))

    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = ("Úkol 01",)

    fake_db = MagicMock()
    fake_db.cursor.return_value.__enter__.return_value = fake_cursor

    monkeypatch.setattr("adv_task_manager_r.odstranit_ukol",
                        lambda db, pouze_aktivni=False:True)

    # ACT
    odstranit_ukol(fake_db)

    # ASSERT
    fake_cursor.execute.assert_any_call(
        "DELETE FROM ukoly WHERE id = %s;", (1,))
    fake_db.commit.assert_called_once()

# Negativní test funkce č:4
@pytest.mark.negative
def test_odstranit_ukol_negative(monkeypatch):
    """TEST 06 - Odstranit úkol - negativní test.
    Uživatel se pokusí smazat neexistující ID úkolu.
    Očekává se hláška, že zvolený ID neexistuje a vyzve uživatele k jiné volbě."""

    # ARRANGE
    ts_inputs = iter(["99", "0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(ts_inputs))

    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = None

    fake_db = MagicMock()
    fake_db.cursor.return_value.__enter__.return_value = fake_cursor

    monkeypatch.setattr(
        "adv_task_manager_r.zobrazit_ukoly",
        lambda db, pouze_aktivni=False: True)

    # ACT
    odstranit_ukol(fake_db)

    # ASSERT    
    fake_cursor.execute.assert_any_call(
        "SELECT nazev FROM ukoly WHERE id = %s;", (99,))

    assert not any(
        call_args[0][0].startswith("DELETE FROM ukoly") 
        for call_args in fake_cursor.execute.call_args_list)
    fake_db.commit.assert_not_called()