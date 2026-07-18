import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

# Absolute path to the SQLite file in the project root, so the location is the
# same no matter what directory the app is launched from.
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "spendly.db",
)

# Fixed category list — keep in sync with the spec.
CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    """Return a SQLite connection with dict-like rows and foreign keys enforced."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables if they don't already exist."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at    TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL NOT NULL,
            category    TEXT NOT NULL,
            date        TEXT NOT NULL,
            description TEXT,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


def seed_db():
    """Insert one demo user and sample expenses — only if the DB is empty."""
    conn = get_db()

    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
    )
    user_id = cursor.lastrowid

    # Spread sample dates across the current month so seed data stays current.
    today = date.today()

    def day(n):
        return today.replace(day=n).isoformat()

    # (amount, category, date, description) — at least one per category.
    sample_expenses = [
        (12.50, "Food", day(2), "Lunch at the deli"),
        (34.00, "Food", day(9), "Weekly groceries"),
        (2.75, "Transport", day(3), "Bus fare"),
        (120.00, "Bills", day(5), "Electricity bill"),
        (45.00, "Health", day(8), "Pharmacy"),
        (18.99, "Entertainment", day(12), "Movie ticket"),
        (67.40, "Shopping", day(14), "New shoes"),
        (9.99, "Other", day(15), "Misc"),
    ]

    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        [(user_id, *row) for row in sample_expenses],
    )

    conn.commit()
    conn.close()
