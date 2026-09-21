import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime

# ── Chemin de la base de données ──────────────────────────
DB_PATH = Path(__file__).parent.parent / "data" / "portfolio.db"
DB_PATH.parent.mkdir(exist_ok=True)   # crée le dossier /data si besoin


# ─────────────────────────────────────────────────────────
#  INITIALISATION DE LA BASE
# ─────────────────────────────────────────────────────────
def init_db() -> None:
    """Crée la table si elle n'existe pas encore."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                isin          TEXT,
                name          TEXT    NOT NULL,
                bond_type     TEXT    NOT NULL,
                currency      TEXT    NOT NULL,
                country       TEXT,
                sector        TEXT,
                rating_sp     TEXT,
                rating_moodys TEXT,
                face_value    REAL    NOT NULL,
                coupon_rate   REAL    NOT NULL,
                maturity_date TEXT    NOT NULL,
                issue_date    TEXT,
                price         REAL    NOT NULL,
                quantity      INTEGER NOT NULL,
                added_at      TEXT    DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


# ─────────────────────────────────────────────────────────
#  LECTURE
# ─────────────────────────────────────────────────────────
def load_portfolio() -> pd.DataFrame:
    """
    Charge le portefeuille depuis SQLite.
    Retourne un DataFrame vide si la table est vide.
    """
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT * FROM portfolio ORDER BY id", conn)
    return df


# ─────────────────────────────────────────────────────────
#  AJOUT D'UNE OBLIGATION
# ─────────────────────────────────────────────────────────
def add_bond(bond: dict) -> int:
    """
    Insère une obligation dans la base.
    Retourne l'id généré.
    """
    init_db()
    sql = """
        INSERT INTO portfolio
            (isin, name, bond_type, currency, country, sector,
             rating_sp, rating_moodys, face_value, coupon_rate,
             maturity_date, issue_date, price, quantity)
        VALUES
            (:isin, :name, :bond_type, :currency, :country, :sector,
             :rating_sp, :rating_moodys, :face_value, :coupon_rate,
             :maturity_date, :issue_date, :price, :quantity)
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(sql, bond)
        conn.commit()
        return cur.lastrowid


# ─────────────────────────────────────────────────────────
#  SUPPRESSION
# ─────────────────────────────────────────────────────────
def delete_bond(bond_id: int) -> None:
    """Supprime une obligation par son id."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM portfolio WHERE id = ?", (bond_id,))
        conn.commit()


def clear_portfolio() -> None:
    """Vide entièrement le portefeuille."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM portfolio")
        conn.commit()


# ─────────────────────────────────────────────────────────
#  MISE À JOUR
# ─────────────────────────────────────────────────────────
def update_bond(bond_id: int, bond: dict) -> None:
    """Met à jour une obligation existante."""
    sql = """
        UPDATE portfolio SET
            isin          = :isin,
            name          = :name,
            bond_type     = :bond_type,
            currency      = :currency,
            country       = :country,
            sector        = :sector,
            rating_sp     = :rating_sp,
            rating_moodys = :rating_moodys,
            face_value    = :face_value,
            coupon_rate   = :coupon_rate,
            maturity_date = :maturity_date,
            issue_date    = :issue_date,
            price         = :price,
            quantity      = :quantity
        WHERE id = :id
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(sql, {**bond, "id": bond_id})
        conn.commit()


# ─────────────────────────────────────────────────────────
#  IMPORT CSV / EXCEL
# ─────────────────────────────────────────────────────────
def import_from_dataframe(df_import: pd.DataFrame) -> tuple[int, list]:
    """
    Importe un DataFrame dans la base.
    Retourne (nb_success, liste_erreurs).
    """
    required_cols = {"name","bond_type","currency",
                     "face_value","coupon_rate","maturity_date","price","quantity"}
    success, errors = 0, []

    for i, row in df_import.iterrows():
        # Vérification colonnes obligatoires
        missing = required_cols - set(row.index)
        if missing:
            errors.append(f"Ligne {i+1} — colonnes manquantes : {missing}")
            continue
        try:
            bond = {
                "isin":          row.get("isin", ""),
                "name":          row["name"],
                "bond_type":     row["bond_type"],
                "currency":      row["currency"],
                "country":       row.get("country", ""),
                "sector":        row.get("sector", ""),
                "rating_sp":     row.get("rating_sp", "NR"),
                "rating_moodys": row.get("rating_moodys", "NR"),
                "face_value":    float(row["face_value"]),
                "coupon_rate":   float(row["coupon_rate"]),
                "maturity_date": str(row["maturity_date"]),
                "issue_date":    str(row.get("issue_date", "")),
                "price":         float(row["price"]),
                "quantity":      int(row["quantity"]),
            }
            add_bond(bond)
            success += 1
        except Exception as e:
            errors.append(f"Ligne {i+1} — {e}")

    return success, errors


# ─────────────────────────────────────────────────────────
#  SESSION STATE SYNC
# ─────────────────────────────────────────────────────────
def sync_session_state() -> None:
    """
    Synchronise la base SQLite → st.session_state.
    À appeler en début de chaque page.
    """
    st.session_state["portfolio"] = load_portfolio()


def get_portfolio() -> pd.DataFrame:
    """
    Retourne le portefeuille depuis session_state.
    Le charge depuis SQLite si absent.
    """
    if "portfolio" not in st.session_state:
        sync_session_state()
    return st.session_state["portfolio"]
