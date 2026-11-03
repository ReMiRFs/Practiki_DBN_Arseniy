import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent


class Database:
    def __init__(self, path: Path):
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def query(self, sql: str, params: tuple = ()) -> list:
        with self.connect() as conn:
            return conn.execute(sql, params).fetchall()

    def query_one(self, sql: str, params: tuple = ()):
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: tuple = ()) -> int:
        with self.connect() as conn:
            cur = conn.execute(sql, params)
            return cur.lastrowid

    def init(self) -> None:
        schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
        with self.connect() as conn:
            conn.executescript(schema)
            cols = [r[1] for r in conn.execute("PRAGMA table_info(applications)")]
            if "hall" not in cols:
                conn.execute("ALTER TABLE applications ADD COLUMN hall TEXT NOT NULL DEFAULT 'Большой зал'")
            if conn.execute("SELECT COUNT(*) FROM roles").fetchone()[0] == 0:
                conn.executemany("INSERT INTO roles(id, name) VALUES (?, ?)",
                                 [(1, "participant"), (2, "admin")])
                conn.executemany("INSERT INTO statuses(id, name) VALUES (?, ?)",
                                 [(1, "Новая"), (2, "Назначено"), (3, "Завершено")])
                conn.execute(
                    "INSERT INTO users(login, password_hash, full_name, email, phone, role_id)"
                    " VALUES (?, ?, ?, ?, ?, 2)",
                    ("Admin26", generate_password_hash("Demo2026"), "Администратор портала",
                     "admin@konferencii.rf", "8(900)000-00-00"))
                conn.executemany(
                    "INSERT INTO events(title, event_date, place, description) VALUES (?, ?, ?, ?)",
                    [
                        ("Веб-разработка 2026", "2026-11-20", "Москва, Технопарк «Сколково»",
                         "Ежегодная конференция о современных веб-технологиях: фронтенд, бекенд, DevOps."),
                        ("Тестирование ПО: практика", "2026-12-05", "Санкт-Петербург, ЭКСПОФОРУМ",
                         "Доклады о ручном и автоматизированном тестировании, мастер-классы по Selenium."),
                        ("ИИ в образовании", "2026-10-10", "Онлайн",
                         "Как нейросети меняют обучение программированию: кейсы преподавателей."),
                        ("UX/UI Design Day", "2027-02-14", "Казань, IT-парк",
                         "Дизайн интерфейсов, исследования пользователей, дизайн-системы."),
                    ])
